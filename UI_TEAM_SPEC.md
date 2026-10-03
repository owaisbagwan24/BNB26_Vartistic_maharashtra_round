# 🎨 UI & Frontend Team Specification & Handover Brief
> **For: Ritesh & Owaise**  
> **From: Core Architecture Team**  
> **Project: Re:Learn IDE — The Cognitive IDE that Diagnoses WHY, Not Just WHAT**

---

## 📌 1. Tumhara Goal (What You Need to Deliver)
Tumhe Re:Learn IDE ka **Frontend Interface** build/refine karna hai. Yeh koi normal code editor nahi hai — yeh ek **Cognitive Learning Studio** hai jisme student code likhta hai, bug aane par AI uski *misconception* diagnose karta hai, aur Socratic hints + interactive quiz se verify karta hai.

---

## 🖥️ 2. UI Layout Architecture (True VS Code & Cursor Layout)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 🔴🟡🟢 Re:Learn IDE — The Cognitive Studio   [Presets: if x=5 | '5'+3 | ...]  ● WASM  │
├────┬──────────────────┬────────────────────────────────────────────┬───────────────────┤
│ 📁 │ EXPLORER         │ [🐍 main.py ✕]          [↺ Reset] [▶ Run]  │ 🧠 Re:Learn AI    │
│ 🔍 │ ▼ PYTHON_LEARNING│────────────────────────────────────────────│ LLaMA-3.3 + AST   │
│ 🧠 │  🐍 main.py      │ 1  x = 5                                   ├───────────────────┤
│ 📊 │  📄 test_types.py│ 2  if x = 5:                               │ 🚨 M-01 Diagnosed │
│    │                  │ 3      print('x is five')                  │ Confidence: 98%   │
│    │                  │                                            │                   │
│    │                  │ [🚨 Coach Bar: Misconception Detected!     │ 🎯 1-Click Quiz:  │
│    │                  │    (💡 View Diagnosis) (🎯 1-Click Quiz)]  │ [A] '=' vs '==' ✅│
│    │                  ├────────────────────────────────────────────┤ [B] Numbers only  │
│    │                  │ PROBLEMS | TERMINAL | OUTPUT               │ [C] Interchange   │
│    │                  │ >>> SyntaxError: invalid syntax (Line 2)   ├───────────────────┤
│    │                  │ >>> Exit: Exception                        │ 🤖 Socratic Chat  │
│ ⚙️ │                  │                                            │ [Ask question...] │
├────┴──────────────────┴────────────────────────────────────────────┴───────────────────┤
│ ⚡ main* | ⚠ 1 Misconception | Ln 2, Col 7 | UTF-8 | Python 3.12 WASM | Socratic: ON   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 3. Backend API Contract (Tumhe Kaunse Endpoints Call Karne Hain)

Backend already `http://localhost:8000` par chal raha hai. Tumhe bas standard `fetch()` se ye endpoints call karne hain:

### Endpoint 1: Code Diagnose (`POST /diagnose`)
Jab student **Run Code** dabata hai aur code me error/issue hota hai:
- **URL**: `POST http://localhost:8000/diagnose`
- **Request Body**:
```json
{
  "session": "student-12345",
  "code": "x = 5\nif x = 5:\n    print(x)",
  "error": "SyntaxError: invalid syntax",
  "output": "",
  "history": []
}
```
- **Response**:
```json
{
  "label": "M-01",
  "confidence": 0.98,
  "is_sloppiness": false,
  "reasoning": "Single assignment '=' used inside conditional test expression instead of comparison '=='.",
  "socratic_hint": "In English, 'is x 5?' is a question, but 'let x be 5' is a command. What is the difference between '=' and '==' in Python?",
  "reassessment_question": "If x = 7, is 'x = 7' asking a question or setting a value?"
}
```

---

### Endpoint 2: Socratic Chat (`POST /chat`)
Jab student chat panel me tutor se sawaal poochta hai:
- **URL**: `POST http://localhost:8000/chat`
- **Request Body**:
```json
{
  "session": "student-12345",
  "misconception": "M-01",
  "message": "Why can't I use single equal here?",
  "code": "if x = 5:"
}
```
- **Response**:
```json
{
  "reply": "Think of it this way: when you ask a question vs when you give a command. Does 'if' test a fact or command a change?"
}
```
*(Rule: AI kabhi direct code answer nahi dega, guidance sawaal dega)*

---

### Endpoint 3: Resolution Verification (`POST /assess`)
Jab student quiz option select karta hai ya apna answer type karta hai:
- **URL**: `POST http://localhost:8000/assess`
- **Request Body**:
```json
{
  "session": "student-12345",
  "misconception_id": "M-01",
  "question": "What is the difference between '=' and '=='?",
  "student_answer": "single = sets value, double == compares"
}
```
- **Response**:
```json
{
  "resolved": true,
  "explanation": "Excellent distinction! You correctly differentiated between assignment and comparison."
}
```
👉 **UI Action on `resolved: true`**:
1. Confetti blast trigger karo (`confetti()`).
2. Audio chime play karo (`playAudio('success')`).
3. Badge ko green **RESOLVED ✅** karo.

---

### Endpoint 4: Teacher Dashboard Analytics (`GET /teacher/dashboard`)
Classroom Heatmap tab load karne ke liye:
- **URL**: `GET http://localhost:8000/teacher/dashboard`
- **Response**:
```json
{
  "total_active_students": 5,
  "total_diagnoses": 18,
  "class_misconception_counts": { "M-01": 8, "M-05": 5, "M-08": 3, "M-09": 2 },
  "resolved_counts": { "M-01": 6, "M-05": 3 }
}
```

---

## 🎨 4. Must-Have Interactive Features Checklist
- [x] **Monaco Editor**: Left side me clean VS Code dark theme me render hona chahiye.
- [x] **Top Preset Buttons**: Pill chips taaki demo me 1 click se bugs load ho sakein (`if x = 5`, `'5' + 3`, etc.).
- [x] **Coach Alert Bar**: Bug aate hi editor ke theek neeche glowing alert bar appear ho.
- [x] **Clickable Quiz Cards (A, B, C)**: Beginner ko type na karna pade — 1-click se answer select ho aur instant confetti & resolved status mile.
- [x] **4 Tabs on Right**:
  1. 🔬 Misconception Diagnosis
  2. 🤖 Socratic Mentor (Chat)
  3. 📈 Mastery Health Grid (M-01 se M-09 status)
  4. 👨‍🏫 Class Analytics (Heatmap bars)

---

## 🚀 5. Local Run Command
Frontend already `http://localhost:8000` par backend ke saath mounted hai.
Sirf project root me `run.bat` par double-click karo ya:
```bash
python -m uvicorn backend.main:app --port 8000
```
Browse to: `http://localhost:8000`
