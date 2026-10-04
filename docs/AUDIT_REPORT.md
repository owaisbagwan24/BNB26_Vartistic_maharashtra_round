# 🔍 Re:Learn Project Audit — Requirements Check

Verdict: 9.5/10 on build quality. 7/10 on scientific credibility (fixable in 1 day).

## ✅ What's DONE (seriously impressive)

| Requirement (from hackathon problem statement) | Status | Evidence |
|---|---|---|
| Misconception Dataset | ✅ EXCEEDS | 290 rows, 9 labels, hard negatives, M-09 sloppiness has 52 rows |
| Misconception Model | ✅ DONE | Tri-engine: AST screener + classifier + LLM (Groq w/ Gemini fallback) |
| Misconception Differentiation | ✅ DONE | Paired hard negatives + guardrail eval (50 adversarial prompts, 0% leak) |
| Adaptive Intervention | ✅ DONE | Isomorphic engine w/ 3-tier escalation (analogy -> decomposition -> instructor flag) |
| Resolution Assessment | ✅ DONE + BEST PART | Parameterized isomorphic quizzes, not static — genuinely novel |
| Learner Model | ✅ DONE | /progress endpoint + SQLite events + teacher dashboard |
| Model Evaluation | ⚠️ PARTIAL | Metrics exist, BUT see Critical Finding #1 and #2 |
| Docs | ✅ EXCEEDS | PRD, System Design, Pitch, Demo Script, Team Handover — 1000+ lines |

## 🔴 CRITICAL FINDING #1: 98% accuracy is NOT defensible (synthetic leakage)

Why: Your 290 rows are LLM-synthetic + paired hard negatives. TF-IDF (n-gram 1-3) sees
near-identical tokens in train and test because stratified random split scatters
near-duplicates across both. train_local.py ITSELF admits "~92-95% honest" but
training_metrics.json shows 98.6%. An ML-savvy judge WILL ask:
"Is your test set truly unseen? Show me the split logic."
If positive + its hard-negative pair land in different splits -> leakage.
If in same split -> memorization. Either way 98% gets challenged.

FIX: Add Leave-One-Label-Out (LOLO) evaluation (script provided: train_unseen_eval.py).
Train on 7 labels, test on 2 completely unseen labels. Report that number honestly.
85% on a true unseen-concept split >> 98% on a leaky random split. Judges reward honesty.

## 🔴 CRITICAL FINDING #2: Unseen-misconception evaluation MISSING

Problem statement literally says: "Model Evaluation: Evaluate ... performance on
responses or misconceptions NOT SEEN during training."
Your split is stratified random — every label appears in train AND test.
train_colab.py (DistilBERT) also has no concept-wise split.
=> You are not evaluating the exact thing the hackathon asks for.

FIX: LOLO eval (script provided). Also update pitch: "85% on never-before-seen misconceptions."

## 🟡 FINDING #3: Badge vs reality mismatch (DistilBERT vs TF-IDF)

README badge: "Held-Out Accuracy 98% - DistilBERT". Production model: 209KB TF-IDF+LR pickle.
If a judge opens classifier.pkl size or asks about the architecture, mismatch is exposed.

FIX (pick one):
A) Actually run train_colab.py (DistilBERT) on Colab, get real numbers, update badges; or
B) Change badges to the honest TF-IDF story: "Calibrated TF-IDF+LR, 98.6% stratified / XX% LOLO".
Option B is safer for the demo. Option A is stronger if you have 2-3 hours of Colab time.

## 🟡 FINDING #4: Zero real-student data

All 290 rows are synthetic. Research impact argument (Brown & Altadmri) cites real data;
judges may ask "did you validate on any real student?"
FIX (cheap, 2 hours): collect 15-20 real buggy submissions from friends/juniors,
label them with your schema, run classifier on them, report "real-data pilot accuracy".
Even a small real-world pilot section in the pitch = massive credibility.

## 🟡 FINDING #5: Frontend is vanilla JS, docs mention React/AntD components

UI_TEAM_SPEC.md describes React/AntD X components; frontend/index.html is a polished
single-file vanilla app (antd script referenced but no JSX/babel). Not a code problem —
the app looks great — but align docs so judges don't spot the gap.

FIX: one line in README: "Production demo ships as a zero-build single-file app;
React/AntD X spec documents the scale-up component architecture."

## 🟢 MINOR: offline demo risk
2133-line HTML pulls Monaco + confetti + antd from CDNs. If venue wifi dies, demo dies.
FIX: pre-record a 90-sec screen capture as backup (DEMO_SCRIPT exists; add fallback note).

## 🏆 Priority Action List (1 day)

1. [MUST] Run train_unseen_eval.py -> get LOLO number -> update training_metrics.json + badges + pitch
2. [MUST] Update PITCH slide 6: show BOTH numbers ("98.6% seen-concept / XX% never-seen concept")
3. [HIGH] Collect 15 real student samples -> pilot eval slide
4. [HIGH] Align README badges with whichever model story you choose
5. [MED] Add backup screen recording to demo kit
6. [MED] One-line doc alignment (React spec = scale-up architecture)

After fixes: 9.5/10 on both axes. The isomorphic engine + firewall are already
judge-winning material — don't let a leaky 98% undermine it.
