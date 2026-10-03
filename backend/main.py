"""Re:Learn backend — FastAPI (Production Tri-Engine Router).
Arbitrates between:
1. AST Deterministic Pre-Screener (<5ms)
2. Calibrated ML Classifier (Trained on Paired Hard Negatives)
3. Guardrailed LLM Socratic Reasoner (Groq Llama-3.3-70B / Gemini)

Endpoints: /run, /diagnose, /chat, /assess, /isomorphic/quiz, /progress/{session}, /teacher/dashboard, /presets
"""
import json
import sqlite3
import os
import uuid
import csv
import pickle
import ast
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ast_engine import analyze_code_and_error
from runner import execute_sandbox_code
from guardrail import check_adversarial_prompt, sanitize_and_guard_response, SOCRATIC_FALLBACK_REDIRECTS
from isomorphic_engine import generate_isomorphic_quiz, evaluate_isomorphic_attempt

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATASET_DIR = PROJECT_ROOT / "dataset"
LABEL_SCHEMA_PATH = DATASET_DIR / "label_schema.json"
MISCONCEPTIONS_CSV_PATH = DATASET_DIR / "misconceptions.csv"
CLASSIFIER_PATH = BASE_DIR / "classifier.pkl"

# Load Taxonomy Schema
if LABEL_SCHEMA_PATH.exists():
    with open(LABEL_SCHEMA_PATH, encoding="utf-8") as f:
        LABELS = json.load(f)["labels"]
else:
    LABELS = {}

LABEL_TEXT = "\n".join(f'{k}: {v["name"]} — {v["desc"]}' for k, v in LABELS.items())

# Load Gold Misconception Snippets for Presets and Reference Reassessment
GOLD_SAMPLES = []
if MISCONCEPTIONS_CSV_PATH.exists():
    with open(MISCONCEPTIONS_CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        GOLD_SAMPLES = list(reader)

# Load Trained Calibrated ML Classifier
LOCAL_CLASSIFIER = None
if CLASSIFIER_PATH.exists():
    try:
        with open(CLASSIFIER_PATH, "rb") as f:
            LOCAL_CLASSIFIER = pickle.load(f)
        print("Loaded production ML classifier pipeline from classifier.pkl")
    except Exception as e:
        print(f"Notice: ML classifier loading deferred: {e}")

DB_PATH = BASE_DIR / "relearn.db"

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
        con.execute("""CREATE TABLE IF NOT EXISTS events(
            id TEXT PRIMARY KEY,
            session TEXT,
            kind TEXT,
            payload TEXT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);")

init_db()

def log_event(session: str, kind: str, payload: dict):
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO events (id, session, kind, payload) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), session, kind, json.dumps(payload))
        )

app = FastAPI(title="Re:Learn IDE API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiagnoseReq(BaseModel):
    session: str
    code: str
    error: str = ""
    output: str = ""
    history: List[Dict[str, Any]] = []
    api_key: Optional[str] = None

class ChatReq(BaseModel):
    session: str
    misconception: str
    message: str
    code: str
    api_key: Optional[str] = None

class AssessReq(BaseModel):
    session: str
    misconception_id: str
    question: str
    student_answer: str
    quiz_data: Optional[Dict[str, Any]] = None
    attempt_number: int = 1
    api_key: Optional[str] = None

class RunReq(BaseModel):
    code: str

DIAG_PROMPT = """You are Re:Learn's Misconception Engine for novice Python learners.
Given student code, error/output, and chat history, identify the UNDERLYING misconception.

Valid labels:
{labels}

Rules:
- M-09 (sloppiness) only if evidence suggests the concept is understood (typo, slips, quick careless mistake).
- Respond ONLY with JSON:
{{
  "label": "M-0X",
  "confidence": 0.85,
  "reasoning": "one concise line explaining why",
  "is_sloppiness": false,
  "socratic_hint": "one question that guides WITHOUT giving code or direct answer",
  "reassessment_question": "a short follow-up question or prediction check to verify they truly understand"
}}"""

CHAT_PROMPT = """You are Re:Learn's Socratic programming tutor.
The student has misconception: {m}.
Strict Guardrail Rules:
1. NEVER output corrected code or the direct solution.
2. Ask ONE guiding thought-provoking question, or provide a tiny mental model analogy.
3. Keep response strictly under 50 words.
4. Tone: warm, curious, encouraging, non-judgmental."""

def get_llm_client(user_key: Optional[str] = None):
    key = user_key or os.environ.get("GROQ_API_KEY")
    if key and key != "paste-key-here" and len(key) > 8:
        try:
            from groq import Groq
            return Groq(api_key=key), "llama-3.3-70b-versatile"
        except Exception:
            pass
    return None, None

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "labels_loaded": len(LABELS),
        "gold_samples": len(GOLD_SAMPLES),
        "ml_classifier_loaded": LOCAL_CLASSIFIER is not None,
        "db": str(DB_PATH)
    }

@app.post("/run")
def execute_python_code(req: RunReq):
    """Executes Python code in an isolated sandbox with timeout protection, security screening, and structured traceback parsing."""
    return execute_sandbox_code(req.code)

@app.get("/presets")
def get_presets():
    """Returns curated demo scenarios so judges can test with 1-click."""
    return [
        {
            "id": "demo-m01",
            "name": "M-01: Assignment vs Comparison",
            "code": "x = 5\nif x = 5:\n    print('x is five')\n",
            "description": "Uses single '=' instead of comparison '==' inside conditional."
        },
        {
            "id": "demo-m09-pair",
            "name": "M-09: Paired Hard Negative (Motor Slip)",
            "code": "# Student demonstrated mastery of == on line 3\nscore = 10\nif score == 10:\n    print('Top mark!')\ntarget = 5\nif target = 5:\n    print('Target reached')\n",
            "description": "Identical SyntaxError on target=5, but student knows ==. Classified as M-09 Sloppiness Slip."
        },
        {
            "id": "demo-m05",
            "name": "M-05: Implicit Type Coercion",
            "code": "age = '5' + 3\nprint('Age next year:', age)\n",
            "description": "Attempts to add string and integer directly."
        },
        {
            "id": "demo-m08",
            "name": "M-08: Print vs Return Duality",
            "code": "def double(x):\n    print(x * 2)\n\ny = double(5)\nprint('Result is:', y + 1)\n",
            "description": "Expects print() to supply return value to caller."
        },
        {
            "id": "demo-m03",
            "name": "M-03: Mutable List Aliasing",
            "code": "a = [1, 2]\nb = a\nb.append(3)\nprint('Original list a:', a)\n",
            "description": "Thinks assignment b = a creates an independent copy."
        }
    ]

@app.get("/isomorphic/quiz")
def get_isomorphic_quiz(misconception: str = Query("M-01")):
    """Generates a novel isomorphic prediction problem with dynamic parameterization."""
    return generate_isomorphic_quiz(misconception)

@app.post("/diagnose")
def diagnose(req: DiagnoseReq):
    """Tri-Engine Arbitrator: AST Pre-Screener + ML Classifier + Socratic Guardrails."""
    # Step 1: Run deterministic AST / Heuristic Analyzer (<5ms)
    ast_result = analyze_code_and_error(req.code, req.error, req.output, req.history)
    
    # Step 2: Run Local Calibrated ML Classifier if available
    ml_prediction = None
    if LOCAL_CLASSIFIER:
        try:
            snippet = f"{req.code} [ERR] {req.error} [OUT] {req.output}"
            probas = LOCAL_CLASSIFIER.predict_proba([snippet])[0]
            top_idx = probas.argmax()
            ml_prediction = {
                "label": LOCAL_CLASSIFIER.classes_[top_idx],
                "confidence": round(float(probas[top_idx]), 4),
                "is_sloppiness": LOCAL_CLASSIFIER.classes_[top_idx] == "M-09"
            }
        except Exception as e:
            print(f"ML inference error: {e}")

    # Step 3: Run LLM Reasoning if API key provided
    client, model_name = get_llm_client(req.api_key)
    if client:
        try:
            hist_str = "\n".join(f"{h.get('role')}: {h.get('text')}" for h in req.history[-6:])
            user_prompt = f"CODE:\n{req.code}\n\nERROR:\n{req.error}\n\nOUTPUT:\n{req.output}\n\nCHAT:\n{hist_str}"
            
            r = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": DIAG_PROMPT.format(labels=LABEL_TEXT)},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=5.0
            )
            llm_result = json.loads(r.choices[0].message.content)
            llm_result.setdefault("is_sloppiness", llm_result.get("label") == "M-09")
            
            # Sanitize Socratic hint with Cognitive Firewall
            safe_hint, _ = sanitize_and_guard_response(llm_result.get("socratic_hint", ""), llm_result.get("label", "M-01"))
            llm_result["socratic_hint"] = safe_hint

            if not llm_result.get("reassessment_question"):
                matched_gold = next((g for g in GOLD_SAMPLES if g["misconception_id"] == llm_result.get("label")), None)
                if matched_gold:
                    llm_result["reassessment_question"] = matched_gold["reassessment_question"]
                    
            log_event(req.session, "diagnosis", llm_result)
            return llm_result
        except Exception as e:
            print(f"LLM diagnosis failed or timed out: {e}. Falling back to AST/ML arbitrator.")

    # Step 4: Arbitration between AST and ML Classifier
    if ast_result and ast_result.get("confidence", 0) >= 0.85:
        # High confidence AST rule match
        final_result = ast_result
        final_result["engine"] = "AST Deterministic Pre-Screener"
    elif ml_prediction and ml_prediction.get("confidence", 0) >= 0.60:
        # Calibrated ML classifier match
        lbl = ml_prediction["label"]
        matched_gold = next((g for g in GOLD_SAMPLES if g["misconception_id"] == lbl), None)
        final_result = {
            "label": lbl,
            "confidence": ml_prediction["confidence"],
            "is_sloppiness": ml_prediction["is_sloppiness"],
            "reasoning": f"Cognitive model matched misconception pattern {lbl} from code AST and runtime state.",
            "socratic_hint": SOCRATIC_FALLBACK_REDIRECTS.get(lbl, "Take a step back: what value does each variable hold right before that line?"),
            "reassessment_question": matched_gold["reassessment_question"] if matched_gold else "Explain what happened on that line in your own words.",
            "engine": "Calibrated N-Gram Multinomial Classifier"
        }
    elif ast_result:
        final_result = ast_result
        final_result["engine"] = "AST Heuristic Engine"
    else:
        # Check if code is clean
        if not req.error:
            try:
                ast.parse(req.code)
                clean_result = {
                    "label": "NONE",
                    "confidence": 1.0,
                    "is_sloppiness": False,
                    "is_clean": True,
                    "reasoning": "Code executed cleanly with zero syntax errors or cognitive misconceptions detected.",
                    "socratic_hint": "Outstanding! Your program logic compiled and executed smoothly without cognitive traps.",
                    "reassessment_question": "Can you explain how this logic handles boundary or edge cases?",
                    "engine": "Compiler Clean Verification"
                }
                log_event(req.session, "diagnosis", clean_result)
                return clean_result
            except Exception:
                pass

        final_result = {
            "label": "M-09",
            "confidence": 0.50,
            "is_sloppiness": True,
            "reasoning": "Standard syntax or runtime check. Check line numbers and operator formatting.",
            "socratic_hint": "Trace through your code line by line. What is each variable holding right before the error?",
            "reassessment_question": "Explain in your own words what line the error points to and what value caused it.",
            "engine": "Default Fallback"
        }

    # Ensure Cognitive Firewall sanitizes hint
    safe_hint, _ = sanitize_and_guard_response(final_result.get("socratic_hint", ""), final_result.get("label", "M-01"))
    final_result["socratic_hint"] = safe_hint

    log_event(req.session, "diagnosis", final_result)
    return final_result

@app.post("/chat")
def chat(req: ChatReq):
    # 1. Adversarial Guardrail Pre-Check
    if check_adversarial_prompt(req.message):
        fallback = SOCRATIC_FALLBACK_REDIRECTS.get(req.misconception, SOCRATIC_FALLBACK_REDIRECTS["M-01"])
        log_event(req.session, "chat", {"misconception": req.misconception, "msg": req.message, "reply": fallback, "guardrail_blocked": True})
        return {"reply": fallback}

    client, model_name = get_llm_client(req.api_key)
    if client:
        try:
            r = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": CHAT_PROMPT.format(m=req.misconception)},
                    {"role": "user", "content": f"CODE:\n{req.code}\n\nSTUDENT SAYS: {req.message}"}
                ],
                temperature=0.3,
                timeout=5.0
            )
            raw_reply = r.choices[0].message.content
            safe_reply, _ = sanitize_and_guard_response(raw_reply, req.misconception)
            log_event(req.session, "chat", {"misconception": req.misconception, "msg": req.message, "reply": safe_reply})
            return {"reply": safe_reply}
        except Exception as e:
            print(f"LLM Chat error: {e}")

    # Socratic rule-based fallback responses tailored to the misconception
    m = req.misconception
    msg_low = req.message.lower()
    
    if m == "M-01":
        if "==" in msg_low or "equal" in msg_low or "compare" in msg_low:
            reply = "Spot on! In Python, '==' asks the question 'are these equal?', whereas a single '=' changes a variable. How does that change line 2?"
        else:
            reply = "Think of it this way: when you ask a question vs when you give an assignment command. Does 'if' want to test a fact or command a change?"
    elif m == "M-05":
        reply = "Consider how Python sees quotes: '5' is a letter or symbol on a page, while 5 is a quantity you can calculate with. How do you convert between them?"
    elif m == "M-08":
        reply = "Remember: print() writes words onto your screen, but return hands a package back to your code. Does your function currently pack anything to send back?"
    elif m == "M-03":
        reply = "Imagine a house with two different street addresses pointing to the same door. Did writing 'b = a' build a new house, or point to the same one?"
    elif m == "M-09":
        reply = "You've got the concept down! Just double-check your spelling or operator punctuation on that line."
    else:
        reply = "Great reflection! If you run this step in your head, what value does the variable take immediately before that line?"

    safe_reply, _ = sanitize_and_guard_response(reply, m)
    log_event(req.session, "chat", {"misconception": req.misconception, "msg": req.message, "reply": safe_reply})
    return {"reply": safe_reply}

@app.post("/assess")
def assess(req: AssessReq):
    # Dynamic Isomorphic Assessment evaluation
    if req.quiz_data:
        eval_result = evaluate_isomorphic_attempt(req.quiz_data, req.student_answer, req.attempt_number)
        log_event(req.session, "assessment", {"m": req.misconception_id, "isomorphic": True, **eval_result})
        return eval_result

    # Standard LLM Assessment evaluation
    client, model_name = get_llm_client(req.api_key)
    if client:
        try:
            r = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Judge if the student's answer demonstrates true conceptual understanding (not a lucky guess). "
                            "Return STRICT JSON: {\"resolved\": true/false, \"explanation\": \"one clear line of feedback\"}"
                        )
                    },
                    {"role": "user", "content": f"QUESTION: {req.question}\nSTUDENT ANSWER: {req.student_answer}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                timeout=5.0
            )
            result = json.loads(r.choices[0].message.content)
            log_event(req.session, "assessment", {"m": req.misconception_id, **result})
            return result
        except Exception as e:
            print(f"LLM Assess error: {e}")

    # Deterministic Assessment Heuristic
    ans = req.student_answer.strip().lower()
    m = req.misconception_id
    
    resolved = False
    explanation = "Provide a bit more detail on why that is the case."
    
    if m == "M-01":
        if any(w in ans for w in ["==", "compare", "question", "test", "set", "assign", "value"]):
            resolved = True
            explanation = "Excellent distinction! You correctly differentiated between assignment and comparison."
    elif m == "M-05":
        if any(w in ans for w in ["int", "type", "convert", "quotes", "text", "string", "concatenate", "22"]):
            resolved = True
            explanation = "Correct! '2' + '2' joins text strings to make '22', while 2 + 2 adds numeric quantities to make 4."
    elif m == "M-08":
        if any(w in ans for w in ["return", "none", "give", "back", "caller", "hand"]):
            resolved = True
            explanation = "Accurate! Without a return statement, a Python function implicitly returns None."
    elif m == "M-03":
        if any(w in ans for w in ["same", "reference", "alias", "both", "[1, 2, 3]", "copy"]):
            resolved = True
            explanation = "Exactly right! Both names refer to the same list in memory."
    elif m == "M-02":
        if any(w in ans for w in ["0", "zero", "stop", "before", "5", "n-1", "index"]):
            resolved = True
            explanation = "Spot on! Python's range stops right before the end boundary, and indices start at 0."
    else:
        if len(ans) > 4:
            resolved = True
            explanation = "Good explanation demonstrating conceptual understanding."

    result = {"resolved": resolved, "explanation": explanation}
    log_event(req.session, "assessment", {"m": req.misconception_id, **result})
    return result

@app.get("/progress/{session}")
def progress(session: str):
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(
            "SELECT kind, payload FROM events WHERE session=? AND kind IN ('diagnosis', 'assessment') ORDER BY ts ASC",
            (session,)
        ).fetchall()
    
    status = {}
    history_events = []
    
    for kind, p in rows:
        d = json.loads(p)
        history_events.append({"kind": kind, "data": d})
        m = d.get("label") or d.get("m") or d.get("misconception_id")
        if not m:
            continue
        if kind == "assessment" and d.get("resolved") is True:
            status[m] = "resolved"
        elif m not in status or status[m] != "resolved":
            status[m] = "active"
            
    return {
        "session": session,
        "concepts": status,
        "event_count": len(history_events)
    }

@app.get("/teacher/dashboard")
def dashboard():
    with sqlite3.connect(DB_PATH) as con:
        diag_rows = con.execute("SELECT payload FROM events WHERE kind='diagnosis'").fetchall()
        assess_rows = con.execute("SELECT payload FROM events WHERE kind='assessment'").fetchall()
        sessions = con.execute("SELECT DISTINCT session FROM events").fetchall()
    
    counts = {}
    for (p,) in diag_rows:
        d = json.loads(p)
        lbl = d.get("label", "Unknown")
        counts[lbl] = counts.get(lbl, 0) + 1
        
    resolved_counts = {}
    for (p,) in assess_rows:
        d = json.loads(p)
        if d.get("resolved") is True:
            m = d.get("m") or d.get("label") or d.get("misconception_id", "Unknown")
            resolved_counts[m] = resolved_counts.get(m, 0) + 1

    # Detect Epidemics (misconceptions with >3 active unresolved cases)
    epidemics = []
    for lbl, total in counts.items():
        if lbl in ["NONE", "Unknown"]:
            continue
        res = resolved_counts.get(lbl, 0)
        unresolved = total - res
        if unresolved >= 3:
            epidemics.append({
                "label": lbl,
                "name": LABELS.get(lbl, {}).get("name", lbl),
                "unresolved": unresolved,
                "total": total,
                "action_recommendation": f"Dedicate 10 minutes in next lecture to {LABELS.get(lbl, {}).get('name', lbl)}."
            })

    return {
        "total_active_students": len(sessions),
        "total_diagnoses": len(diag_rows),
        "class_misconception_counts": counts,
        "resolved_counts": resolved_counts,
        "epidemics": epidemics,
        "taxonomy": LABELS,
        "research_backing": "Brown & Altadmri (2017) 100M+ events; Perkins (1986) Bugs vs Slips"
    }

# Mount Frontend static directory for single-port unified deployment
from starlette.staticfiles import StaticFiles
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
