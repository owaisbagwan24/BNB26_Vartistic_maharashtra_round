"""Re:Learn backend — FastAPI.
Hybrid Misconception Diagnostic Engine: AST Deterministic Pre-Screener + LLM Socratic Reasoning.
Endpoints: /diagnose, /chat, /assess, /progress, /teacher/dashboard, /presets
"""
import json
import sqlite3
import os
import uuid
import csv
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import subprocess
import ast

from ast_engine import analyze_code_and_error
from runner import execute_sandbox_code

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATASET_DIR = PROJECT_ROOT / "dataset"
LABEL_SCHEMA_PATH = DATASET_DIR / "label_schema.json"
MISCONCEPTIONS_CSV_PATH = DATASET_DIR / "misconceptions.csv"

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

app = FastAPI(title="Re:Learn IDE API", version="1.0.0")
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
    api_key: Optional[str] = None

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
        "db": str(DB_PATH)
    }

class RunReq(BaseModel):
    code: str

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
        },
        {
            "id": "demo-m09",
            "name": "M-09: Sloppiness Slip (Negative Class)",
            "code": "pritn('Hello from Re:Learn!')\n",
            "description": "Demonstrates carelessness/typo without conceptual deficit."
        }
    ]

@app.post("/diagnose")
def diagnose(req: DiagnoseReq):
    # Step 1: Run deterministic AST / Heuristic Analyzer
    ast_result = analyze_code_and_error(req.code, req.error, req.output, req.history)
    
    # Step 2: Attempt LLM Diagnosis if API key is provided
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
            
            # If reassessment question missing, populate from gold samples
            if not llm_result.get("reassessment_question"):
                matched_gold = next((g for g in GOLD_SAMPLES if g["misconception_id"] == llm_result.get("label")), None)
                if matched_gold:
                    llm_result["reassessment_question"] = matched_gold["reassessment_question"]
                    
            log_event(req.session, "diagnosis", llm_result)
            return llm_result
        except Exception as e:
            # Gracefully fall back to AST analyzer
            print(f"LLM diagnosis failed or timed out: {e}. Falling back to AST analyzer.")

    # Step 3: High-accuracy AST / Rule fallback
    if ast_result:
        # Match reassessment from gold samples if needed
        if not ast_result.get("reassessment_question"):
            matched_gold = next((g for g in GOLD_SAMPLES if g["misconception_id"] == ast_result["label"]), None)
            if matched_gold:
                ast_result["reassessment_question"] = matched_gold["reassessment_question"]
        log_event(req.session, "diagnosis", ast_result)
        return ast_result

    # If no error reported and code is syntactically sound, it is clean valid execution
    if not req.error and ast_result is None:
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
                "rule_matched": "clean_execution"
            }
            log_event(req.session, "diagnosis", clean_result)
            return clean_result
        except Exception:
            pass

    # Default fallback if error occurred but no specific rule triggered
    fallback = {
        "label": "M-09",
        "confidence": 0.50,
        "is_sloppiness": True,
        "reasoning": "Standard syntax or runtime check. Check line numbers and operator formatting.",
        "socratic_hint": "Trace through your code line by line. What is each variable holding right before the error?",
        "reassessment_question": "Explain in your own words what line the error points to and what value caused it.",
        "rule_matched": "default_fallback"
    }
    log_event(req.session, "diagnosis", fallback)
    return fallback

@app.post("/chat")
def chat(req: ChatReq):
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
            reply = r.choices[0].message.content
            log_event(req.session, "chat", {"misconception": req.misconception, "msg": req.message, "reply": reply})
            return {"reply": reply}
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
        reply = f"Great reflection! If you run this step in your head, what value does the variable take immediately before that line?"

    log_event(req.session, "chat", {"misconception": req.misconception, "msg": req.message, "reply": reply})
    return {"reply": reply}

@app.post("/assess")
def assess(req: AssessReq):
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
        if len(ans) > 6:
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
        m = d.get("label") or d.get("m")
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
            m = d.get("m") or d.get("label", "Unknown")
            resolved_counts[m] = resolved_counts.get(m, 0) + 1

    return {
        "total_active_students": len(sessions),
        "total_diagnoses": len(diag_rows),
        "class_misconception_counts": counts,
        "resolved_counts": resolved_counts,
        "taxonomy": LABELS
    }

# Mount Frontend static directory for single-port unified deployment
from starlette.staticfiles import StaticFiles
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

