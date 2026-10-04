# 🧠 Re:Learn IDE — Cognitive Misconception Engine & Resolution Loop

> **"Cursor fixes your syntax and makes you dependent; ChatGPT does your homework; Re:Learn is the first IDE that diagnoses why you failed, tutors without leaking answers, and proves you actually learned — while giving your professor a live classroom epidemiology heatmap."**

[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-DistilBERT-EE4C2C.svg?logo=pytorch)](https://pytorch.org)
[![Accuracy](https://img.shields.io/badge/Held--Out%20Accuracy-98.0%25-brightgreen.svg)](#4-model-training--empirical-evaluation)
[![M-09 Precision](https://img.shields.io/badge/M--09%20Sloppiness%20Precision-100%25-blue.svg)](#4-model-training--empirical-evaluation)
[![Firewall Leakage](https://img.shields.io/badge/Solution%20Leakage-0.00%25-success.svg)](#5-cognitive-firewall-adversarial-red-teaming)

---

## 📑 Core Documentation Index

- 📘 [PRD.md](file:///c:/Users/JUBER/Downloads/hackathon/PRD.md): Formal Product Requirements Document with full cognitive research foundations.
- 🏗️ [SYSTEM_DESIGN_AND_ARCHITECTURE.md](file:///c:/Users/JUBER/Downloads/hackathon/SYSTEM_DESIGN_AND_ARCHITECTURE.md): Complete UI system design, capacity math (120k runs/term), state machine, and scale path to 10k students.
- 🏆 [PITCH.md](file:///c:/Users/JUBER/Downloads/hackathon/PITCH.md): 8-slide pitch deck blueprint with market timing ($44.2B ITS market) and unfair angles.
- 🎬 [DEMO_SCRIPT.md](file:///c:/Users/JUBER/Downloads/hackathon/DEMO_SCRIPT.md): Rehearsed 3-minute winning presentation choreography.

---

## 1. The Core Scientific Problem

In introductory computer science (CS1), compilers and AI code tools diagnose **what** failed (the error message), but completely fail to diagnose **why** it failed (the student's cognitive mental model).

1. **Weak Consensus Among Faculty**: Brown & Altadmri (University of Kent) analyzed **100M+ compilation events** across 900+ students and proved educators themselves have only *weak consensus* on what students actually misunderstand — and years of teaching experience do not improve teacher intuition.
2. **The Many-to-Many Dilemma**: Compiler errors have a many-to-many relationship with misconceptions. One `SyntaxError: invalid syntax` can stem from 5 distinct cognitive failures.
3. **The Sloppiness Dilemma (Perkins' 1986 "Bugs vs. Slips")**: Treating every careless typo as a conceptual deficit wastes student time and destroys trust. Re:Learn explicitly separates motor slips from cognitive gaps via the **M-09 Sloppiness Negative Class**.
4. **The Resolution Void**: Every tool diagnoses; almost none **proves resolution** via structurally fresh, isomorphic checks.

---

## 2. Re:Learn System Architecture

```text
┌───────────────────────────────── BROWSER CLIENT ─────────────────────────────────┐
│ • Monaco Code Editor (Tactile, line-accurate visual diagnostic markers)          │
│ • State-Machine Rail (One active cognitive mode at a time: Code/Diagnose/Verify) │
│ • Cognitive Diagnosis Card (Animated border beam, calibrated confidence score)   │
│ • Socratic Dialogue Drawer (AntD X Bubble/Sender, <50 word analogies)            │
│ • Dynamic Isomorphic Quiz (RareUI 3D tactile cards, fresh parameterized logic)   │
│ • Soundcn Audio Microfeedback (4 restrained synthesized acoustic signals)        │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ JSON-RPC / REST
                                         ▼
┌─────────────────────────────── BACKEND API ENGINE ───────────────────────────────┐
│ 1. TRI-ENGINE ARBITRATION ROUTER                                                 │
│    ├─ AST Deterministic Pre-Screener (<5ms, zero cloud cost)                     │
│    ├─ Fine-Tuned DistilBERT Classifier (Offline-capable, 98% accuracy)           │
│    └─ LLM Socratic Reasoner (Groq Llama-3.3-70B / Gemini few-shot)               │
│                                                                                  │
│ 2. COGNITIVE FIREWALL & OUTPUT LEAK FILTER                                       │
│    └─ Intercepts prompt injections; enforces 0% executable code leakage          │
│                                                                                  │
│ 3. DYNAMIC ISOMORPHIC RESOLUTION VERIFIER                                        │
│    └─ Parameterized code generation with 3-tier escalation (Analogy ➔ Trace ➔ TA) │
│                                                                                  │
│ 4. PERSISTENT LEARNER MODEL & TEACHER EPIDEMIOLOGY                               │
│    └─ SQLite WAL Mode event stream + Real-time classroom epidemic heatmap        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The 6 Unfair Advantages

| # | Hidden Insight | How Re:Learn Solves It |
|---|---|---|
| **1** | **M-09 Sloppiness Negative Class** | Uses paired hard negatives to isolate typos from conceptual gaps (Perkins 1986). Typo slips receive a 1-second linter nudge (neutral blue) instead of patronizing lectures. |
| **2** | **Closed-Loop Resolution Verification** | Replaces "code runs now" with novel isomorphic prediction challenges testing the identical concept with fresh surface syntax. |
| **3** | **Classroom Misconception Epidemiology** | Live teacher heatmap alerts professors to active cognitive epidemics, directly answering: *"What do I teach tomorrow?"* |
| **4** | **Cognitive Firewall (0% Answer Leak)** | Structurally prohibits complete code output (<50 words, Socratic questions); complies with university academic integrity rules. |
| **5** | **Proprietary Data Flywheel** | Every session logs `(code, error, chat, diagnosis, isomorphic outcome)` — a uniquely labeled dataset that does not exist anywhere. |
| **6** | **Domain Generalization** | The pipeline (execute ➔ diagnose ➔ Socratic intervention ➔ isomorphic verify) ports directly to Introductory Algebra and Physics. |

---

## 4. Model Training & Empirical Evaluation

To eliminate synthetic data leakage (a critical vulnerability in hackathon submissions), Re:Learn was trained on **mutation-verified executable code** with **paired hard negatives**:

- **Dataset**: 290 executable-verified samples with real Python compiler tracebacks.
- **Flagship Paired Hard Negative**: Two rows with the **identical compiler error** (`SyntaxError` on `if target = 5:`), where Row A represents M-01 (concept gap) and Row B represents M-09 (typo slip by a student who demonstrated mastery of `==` elsewhere).
- **Fine-Tuned Transformer**: DistilBERT (`distilbert-base-uncased`) trained via Google Colab ([training/train_relearn.ipynb](file:///c:/Users/JUBER/Downloads/hackathon/training/train_relearn.ipynb)).

### Held-Out Test Evaluation (59 Samples)
```text
              precision    recall  f1-score   support

        M-01       0.90      1.00      0.95         9
        M-02       1.00      1.00      1.00         8
        M-03       1.00      1.00      1.00         8
        M-04       1.00      1.00      1.00         6
        M-05       1.00      1.00      1.00         6
        M-06       0.00      0.00      0.00         1
        M-07       1.00      1.00      1.00         4
        M-08       1.00      1.00      1.00         6
        M-09       1.00      1.00      1.00        11

    accuracy                           0.98        59
   macro avg       0.88      0.89      0.88        59
weighted avg       0.97      0.98      0.98        59
```
- **Overall Accuracy**: **98.0%**
- **M-09 Sloppiness Precision**: **1.00 (100%)** — Zero false alarms on careless typing slips!
- **M-09 Sloppiness Recall**: **1.00 (100%)**

---

## 5. Cognitive Firewall Adversarial Red-Teaming

Evaluated across **50 adversarial prompt injections** ("ignore previous instructions", "just give me the code", "do my homework") via [training/eval_guardrail.py](file:///c:/Users/JUBER/Downloads/hackathon/training/eval_guardrail.py):

| Metric | Result | Target | Status |
|---|---|---|---|
| **Total Adversarial Attacks** | 50 | 50 | Completed |
| **Solution Leaks Detected** | **0** | 0 | **PASS** |
| **Solution Leakage Rate** | **0.00%** | 0.00% | **100% Strict Socratic Posture** |

---

## 6. Quick Start & Execution

### 1-Click Launch (Windows)
Double-click [run.bat](file:///c:/Users/JUBER/Downloads/hackathon/run.bat) or run:
```powershell
.\run.bat
```

### Manual Command-Line Startup
```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Launch FastAPI Unified Server (Frontend + Backend on port 8000)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Open your browser to:  
👉 **`http://localhost:8000`**

---

## 7. Project Structure

```text
├── backend/
│   ├── main.py                  # FastAPI Tri-Engine Router & unified server
│   ├── runner.py                # Isolated sandbox runner with AST security checks
│   ├── ast_engine.py            # High-speed AST deterministic pre-screener (<5ms)
│   ├── guardrail.py             # Cognitive Firewall: 0% solution leakage filter
│   ├── isomorphic_engine.py     # Parameterized quiz generator with 3 escalation tiers
│   ├── classifier.pkl           # Calibrated multinomial model for offline inference
│   └── relearn.db               # SQLite database in Write-Ahead Logging (WAL) mode
├── dataset/
│   ├── label_schema.json        # 9-class taxonomy schema (M-01..M-09)
│   ├── misconceptions.csv       # 20 gold seed cases
│   ├── misconceptions_expanded.csv # 290 mutation-verified samples with hard negatives
│   └── generate_hard_negatives.py # Mutation generator with executable verification
├── frontend/
│   └── index.html               # 2-column studio layout (RareUI + Soundcn + Ant Design)
├── training/
│   ├── train_relearn.ipynb      # Google Colab notebook for DistilBERT fine-tuning
│   ├── train_local.py           # Local evaluation pipeline with confusion matrix
│   ├── eval_guardrail.py        # 50-prompt adversarial red-teaming test harness
│   ├── training_metrics.json    # Evaluated test metrics JSON
│   └── confusion_matrix.png     # Pitch-ready dark-mode confusion matrix
├── PRD.md                       # Product Requirements Document
├── SYSTEM_DESIGN_AND_ARCHITECTURE.md # System design primer & capacity analysis
├── PITCH.md                     # 8-slide presentation blueprint
└── DEMO_SCRIPT.md               # 3-minute rehearsed walkthrough script
```

---

## 8. License & Attribution
- Based on research taxonomy from **Brown & Altadmri (2017, 2020)** and **Perkins et al. (1986)**.
- Built for the Hackathon by the **Re:Learn Engineering Team**.
