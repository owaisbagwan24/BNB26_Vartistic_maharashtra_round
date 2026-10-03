# Re:Learn IDE — Starter Kit

AI-powered learning IDE that diagnoses the *misconception* behind a student's wrong code
(not just the error), gives a Socratic intervention, and *verifies* resolution.

---

## 1. Full Requirements / Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React (or plain HTML/JS for speed) + Monaco Editor | Monaco = the VS Code editor, free |
| In-browser Python | Pyodide (WASM) | No server sandbox needed, offline demo possible |
| Backend | FastAPI + Uvicorn | Fast, easy JSON APIs |
| Diagnosis brain (demo) | Groq API (llama-3.3-70b) or Gemini free tier | Fast + free |
| Diagnosis brain (trained proof) | DistilBERT fine-tuned on `dataset/misconceptions.csv` | Confusion matrix for judges |
| DB | SQLite (demo) → Postgres (scale) | Zero setup |
| Training env | Google Colab (free GPU) | No local GPU needed |
| Deployment | Vercel/Netlify (frontend), Render (backend) | Free tiers |

Python >= 3.10 required.

Install backend:
```
pip install fastapi uvicorn groq pandas scikit-learn torch transformers
```

---

## 2. Data Requirements

- `dataset/label_schema.json` — 9 labels (M-01..M-09). M-09 = SLOPPINESS negative class (key differentiator).
- `dataset/misconceptions.csv` — 20 gold rows to start.
- Scale to 150-300 rows using `scripts/generate_synthetic.py` (LLM-generated + human verified).
- Field meanings:
  - `student_code` — what the student wrote
  - `error_message` / `wrong_output` — surface signal
  - `misconception_id` — the WHY (label)
  - `socratic_intervention` — question, never an answer
  - `reassessment_question` — used to verify resolution

Golden rule: 1 error message can map to many misconceptions (many-to-many, proven in research) —
so features = code + error + chat signal, never error alone.

## 3. Training Plan (Colab)

1. Load `misconceptions.csv`, build text = code + error + output.
2. Split **by misconception** (hold out 2 labels as "unseen" -> directly satisfies the
   "unseen misconceptions" evaluation requirement).
3. Fine-tune DistilBERT (multiclass, 9 classes) — see `training/train.py`.
4. Report: accuracy + classification report + confusion matrix (put screenshot in pitch deck).
5. Runtime: LLM few-shot for the live demo; fine-tuned model as the "production" proof + fallback.

## 4. Run It

Terminal 1 (backend):
```
cd backend && uvicorn main:app --reload --port 8000
```
Terminal 2: serve frontend/
```
cd frontend && python -m http.server 5173
```
Open http://localhost:5173 — write buggy code in the editor, press Run,
watch the diagnosis card + Socratic chat appear.

Set your key: `export GROQ_API_KEY=...` (or paste in the UI for demo).

## 5. 3-Day Build Plan

- Day 1: Monaco + Pyodide run loop; dataset v1 (50 rows)
- Day 2: Diagnosis engine + Socratic chat + learner model (SQLite)
- Day 3: Reassessment quiz + dashboard + Colab training + confusion matrix + pitch
