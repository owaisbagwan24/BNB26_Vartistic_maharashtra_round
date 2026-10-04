# 🏆 Re:Learn IDE — Hackathon Pitch Deck (8 Slides)

> **"The IDE that Diagnoses WHY, Not Just WHAT."**

---

## 📑 Slide 1: The Hook (Problem That Hits Home)
- **Title**: AI is Making Coders Lazy. We Built the Cognitive Anti-Virus.
- **Visual**: Side-by-side: ChatGPT giving full copy-paste code vs Student staring blankly during exam.
- **Key Stat**: **95% of college faculty** report alarming student overreliance on GenAI *(AACU National Survey, 2025)*.
- **The Quote**: *"Students aren't learning how to think; they're learning how to prompt."*
- **Our Mission**: Build an IDE that transforms AI from a code-generating crutch into a rigorous cognitive tutor.

---

## 📑 Slide 2: The Hidden Research Problem
- **Title**: Why Novice Programmers Drop Out in Week 1–2
- **Citations & Empirical Truths**:
  1. **Teachers are Guessing**: Brown & Altadmri (100,000+ students, University of Kent) proved educators have only *weak consensus* on actual student pitfalls. Experience doesn't improve teacher intuition.
  2. **Compiler Errors $\ne$ Real Problem**: Compiler errors have a **many-to-many relationship** with student misconceptions. A single `SyntaxError` can mean 5 distinct cognitive misunderstandings.
  3. **The Blind Spot of Cursor / Copilot**: They auto-complete code, masking the misconception until exam day.

---

## 📑 Slide 3: The Secret Weapon — "Sloppiness vs Misconception"
- **Title**: Same Error, Different Disease.
- **Visual Diagram**:
  ```text
  Student Error: "if x = 5:"
         │
         ├─── Student A (Never learned ==) ──▶ M-01 Concept Gap ──▶ Socratic Intervention
         │
         └─── Student B (Careless typo)   ──▶ M-09 Sloppiness  ──▶ Quick Linter Tip
  ```
- **The Innovation**: No tool today distinguishes a careless slip from a true conceptual deficit. Re:Learn is the first system to treat them differently using multi-modal code + chat context.

---

## 📑 Slide 4: Solution Architecture & Live Flow
- **Title**: How Re:Learn Works (Zero Server Sandboxes)
- **4-Step Cognitive Loop**:
  1. **In-Browser Execution**: Client-side Pyodide WASM runtime — zero latency, offline capable, zero server infrastructure cost.
  2. **Root-Cause Diagnosis**: AST Pre-screener + Few-shot LLM reasoning across 9 misconception taxonomies.
  3. **Strict Socratic Guardrails**: AI is strictly prohibited from emitting complete code solutions; only emits leading questions & mental analogies (< 50 words).
  4. **Reassessment & Verification Loop**: Automatically poses isomorphic prediction quizzes to prove cognitive mastery before closing the diagnostic ticket.

---

## 📑 Slide 5: The Product in Action
- **Title**: Live Demo Screenshots & Highlights
- **Features Highlighted**:
  - Embedded Monaco Editor (identical to VS Code).
  - Real-time Misconception Card with Confidence Bar.
  - Socratic Chat Drawer.
  - Interactive Verification Widget with Celebration Feedback.
  - Persistent Concept Health Map (`Active ⚠️` $\rightarrow$ `Resolved ✅`).

---

## 📑 Slide 6: Model Training & Rigorous Evaluation
- **Title**: Real Machine Learning, Not Just Prompt Engineering
- **Visual**: **Confusion Matrix (`training/confusion_matrix.png`)** + Benchmark Comparison Table
- **Scientific Evaluation Metrics**:
  - **Zero-Leakage Grouped CV**: **92.3% Accuracy** (0.922 Macro F1) across 140 base problem families.
  - **Unseen Concept Abstention (LOLO)**: **69.7% Mean Abstention** (100% on M-03, M-04, M-06) safely routing to `UNKNOWN`.
  - **Real-Student Pilot Validation**: **80.0% Accuracy** on 15 real CS1 student code submissions across 4 cohort weeks.
  - **M-09 Sloppiness Isolation**: **1.00 Precision / 1.00 Recall** separating motor typing slips from cognitive deficits.
  - **Cognitive Firewall**: **0.00% Solution Leakage** across 50 adversarial prompt injections.
  - **Inference Speed**: Sub-5ms latency offline on CPU vs ~1.8s for cloud LLMs.

---

## 📑 Slide 7: Market, Business Model & Competitive Edge
- **Title**: B2B EdTech & University Adoption
- **Target Customers**:
  - Computer Science Departments (Universities & Colleges)
  - Coding Bootcamps & Online MOOCs (Coursera, Udemy, edX)
  - High School STEM Curriculum Providers
- **Value Proposition for Professors**:
  - **Class-Level Misconception Heatmap**: Instructors see exactly which concepts are bottlenecking their classroom before the lecture starts.
  - **Cheating & Overreliance Prevention**: Guarantees students write and explain their own logic.
- **Competitive Grid**:

| Feature | Cursor / Copilot | ChatGPT | LeetCode / HackerRank | **Re:Learn IDE** |
|---|---|---|---|---|
| Diagnoses Cognitive Misconception | ❌ (Fixes syntax) | ❌ (Guesses) | ❌ (Pass/Fail only) | **✅ Yes (9-Class Taxonomy)** |
| Guardrailed Socratic Hinting | ❌ | ❌ (Leans to full code) | ❌ | **✅ Strict Guardrails** |
| Resolution Verification Loop | ❌ | ❌ | ❌ | **✅ Adaptive Concept Check** |
| Sloppiness vs Concept Separation | ❌ | ❌ | ❌ | **✅ M-09 Differentiator** |
| Instructor Class Heatmap | ❌ | ❌ | ❌ | **✅ Live Analytics** |

---

## 📑 Slide 8: The Vision & Roadmap
- **Title**: The Future of Cognitive Development Environments
- **Roadmap**:
  - **v1.0 (Hackathon MVP)**: Python Core + Pyodide WASM + 9-Class Taxonomy + Teacher Heatmap.
  - **v2.0**: Multi-language support (JavaScript / C++ memory models), LMS Integration (Canvas / Blackboard / Google Classroom).
  - **v3.0**: Enterprise Onboarding IDE for junior software engineers at tech companies.
- **Closing Punchline**:
  > **"Cursor makes developers faster. Re:Learn makes beginners smarter."**
