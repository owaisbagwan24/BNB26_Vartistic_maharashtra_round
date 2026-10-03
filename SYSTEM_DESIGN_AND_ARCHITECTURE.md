# Re:Learn — UI + System Design + Workflow Architecture

*(Built from synthesis of Ant Design v6, @ant-design/x, React Bits, RareUI, Soundcn, Puncsky System Design, and Donne Martin System Design Primer)*

---

## 0. Component Library & Architectural Synthesis

| Library / Source | Core Specification | Role in Re:Learn |
|---|---|---|
| **Ant Design (v6)** | Pure CSS variables, token theming, semantic classNames, React 18/19 native | **Design System Backbone** — Panels, tabs, forms, problems table, dark/light token provider. |
| **@ant-design/x** | AI-native UI kit: `Bubble.List`, `Sender`, `Think`/`ThoughtChain`, streaming markdown | **Cognitive Socratic Chat** — Transparent diagnostic reasoning without code spoilers. |
| **React Bits** | Copy-paste micro-interactions, spotlight cards, glowing border beam, reveal animations | **Visual Polish** — Animated border beam on diagnosis cards, celebration reveals. |
| **RareUI** | Signature widgets: step player, animated counter, glass shimmer button, matrix pill | **Resolution Widgets** — Step-by-step verification player and haptic buttons. |
| **Soundcn** | Base64 Web Audio synthesizer modules, zero external audio asset dependencies | **Audio Microfeedback** — 4 restrained acoustic signals (ping, tick, chime, alert). |
| **Puncsky System Design** | 4-step framework; "Designing Online Judge or LeetCode" case study | **Architecture Methodology** — Defense blueprint for technical judging panels. |
| **Donne Martin Primer** | Back-of-the-envelope capacity math, latency bounds, CAP theorem, caching | **Scalability Validation** — Capacity justification for 10,000+ student cohorts. |

---

## 1. UI & Design System Architecture

### 1.1 Ant Design v6 Design Tokens
```tsx
theme={{
  token: {
    colorPrimary: '#6D5EF0',        // Re:Learn violet
    colorSuccess: '#2BA471',        // Resolved concept (verified)
    colorWarning: '#D89614',        // Active misconception (concept gap)
    colorError: '#D54941',          // Recurring misconception / epidemic
    colorInfo: '#1469C9',           // Sloppiness (M-09) — neutral blue, NOT red
    borderRadius: 10,
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  }
}}
```

#### Semantic Color Rule (The Differentiator Made Visible):
- **True Concept Deficits (M-01..M-08)**: Rendered in **warm amber/orange** (`#D89614`). Indicates cognitive restructuring is needed.
- **Motor Slips (M-09 Sloppiness)**: Rendered in **neutral calm blue** (`#1469C9`). No shame, no patronizing lectures — simply prompts a 1-second syntax check.

### 1.2 Information Architecture
```text
/student
  /ide          ← Core interactive studio (Monaco + Pyodide + State Machine Rail)
  /concepts     ← Visual concept mastery graph (9 taxonomy nodes)
  /history      ← Historical resolution timeline & diagnostic logs
/teacher
  /dashboard    ← Class-wide misconception heatmap (Section A/B/C)
  /epidemics    ← Automated alerts (>30% active unresolved) + lecture suggestions
  /students/:id ← Individual learner model progression & office-hour tickets
```

### 1.3 State-Machine-Driven Layout (Zero Visual Clutter)
Unlike conventional cluttered learning tools that stack 5 side drawers at once, Re:Learn enforces **one active cognitive mode at a time on the right rail**:

```text
┌────────────────────────────────────────────────────────┐
│ TopBar: Run ▶ | Mode: [Code] ➔ [Diagnose] ➔ [Verify]   │
├───────────────────────────────┬────────────────────────┤
│                               │ Right Rail:            │
│   Monaco Code Editor          │ (One mode at a time)   │
│   (Pyodide local WASM sandbox)│                        │
│                               │ • MODE: Code           │
│                               │   ➔ Rail collapsed     │
│   Terminal & Output Drawer    │ • MODE: Diagnose       │
│   (stdout, stderr, traceback) │   ➔ Diagnosis Card     │
│                               │ • MODE: Reflect        │
│                               │   ➔ Socratic Chat      │
│                               │ • MODE: Verify         │
│                               │   ➔ Isomorphic Quiz    │
└───────────────────────────────┴────────────────────────┘
```

### 1.4 Soundcn Acoustic Hierarchy (Restraint as a Feature)
Only **4 micro-feedback sounds** exist in the system to prevent sensory fatigue:
1. **Diagnosis Notification (`Soundcn.run()`)**: Soft, unobtrusive 440Hz pop when diagnosis arrives.
2. **Escalation Tick (`Soundcn.retry()`)**: Subtle low-pitch tick when stepping through guided hints.
3. **Resolution Chime (`Soundcn.success()`)**: Crisp dual-tone major third chord (`523Hz ➔ 659Hz`) on passing isomorphic verification.
4. **Epidemic Alert (`Soundcn.pop()`)**: Audible cue when opening teacher classroom alerts.
*(TopBar includes an immediate 🔊/🔇 toggle with persisted preference).*

---

## 2. Cognitive Loop as an Explicit State Machine

```text
        ┌──────────┐   Run ▶   ┌────────────┐
        │  WRITING ├──────────►│ EXECUTING  │ (Pyodide local sandbox)
        └────┬─────┘           └─────┬──────┘
             │ Fixes code            │ Clean? ──────► WRITING (Clean state)
             │                       │ Error / Wrong output
             │                ┌──────▼───────┐
             │                │  DIAGNOSING  │ AST prescreener (<5ms)
             │                └──────┬───────┘ ──► Local ML classifier ──► LLM
             │        High confidence│ Low confidence (τ < 0.60)
             │                ┌──────▼───────┐      │ Route to "Uncertain"
             │                │  INTERVENING │ M-09: Quick typo nudge (blue)
             │                │  (Tier 1-3)  │ M-01..08: Socratic analogy (amber)
             │                └──────┬───────┘
             │             Passes or answers diagnosis
             │                ┌──────▼───────┐
             │                │  VERIFYING   │ Dynamic isomorphic prediction check
             │                └──────┬───────┘ (Fresh variable names, novel logic)
             │                  Pass │         Fail
             │                ┌──────▼───┐  ┌──▼───────────┐
             │                │ RESOLVED │  │ Tier 2 Trace │
             │                │ ✅+chime │  │ Tier 3 Ticket│
             │                └────┬─────┘  └───┬──────────┘
             │  Schedule 24h review│            │ Escalates back to Socratic
             ▼                     ▼            ▼
        ┌───────────────────────────────────────┐
        │ LEARNER MODEL (Per-student concept:   │
        │ unknown ➔ exposed ➔ active ➔ resolved)│
        └──────────────────┬────────────────────┘
                           ▼ Aggregation
                   ┌───────────────┐
                   │ TEACHER HEAT  │ Real-time class epidemiology heatmap
                   └───────────────┘
```

---

## 3. System Design & Scalability Analysis (Primer Format)

### 3.1 Requirements
- **Functional**: Local Python execution, 9-class cognitive diagnosis, 0%-leak Socratic tutor, dynamic isomorphic verification, persistent learner model, teacher epidemiology.
- **Non-Functional**:
  - $p95$ diagnosis latency $< 1500\text{ms}$ (classroom patience window).
  - Zero server sandbox fleet cost (execution runs in-browser / local sandbox).
  - High availability during synchronized 300-student lab sessions.

### 3.2 Back-of-the-Envelope Capacity Estimation
- **Classroom Cohort**: 1 lecture section = 200 active students.
- **Session Activity**: 30 runs per student per 90-minute lab session.
- **Term Usage**: 20 lab sessions per academic semester.
- **Total Diagnostic Events**:
  $$\text{Events} = 200 \text{ students} \times 30 \text{ runs} \times 20 \text{ sessions} = 120,000 \text{ events/term/class}$$
- **Peak Concurrency**: Synchronized lab exercises generate **20–40 QPS peak**.
- **Infra Footprint**:
  - Event payload $\approx 2\text{ KB}$ (code snippet, traceback, diagnosis JSON).
  - Storage required: $120,000 \times 2\text{ KB} \approx \mathbf{240\text{ MB/term/class}}$.
  - A single FastAPI instance with SQLite in WAL mode trivially handles up to 500 QPS on a modest $10/month cloud node.

### 3.3 The Core Economic Moat: Dual-Engine Cost Decoupling
Conventional AI tutor startups route every single compiler error to OpenAI/Anthropic APIs:
$$\text{Cost}_{\text{competitors}} = 120,000 \text{ runs} \times \$0.015 \approx \mathbf{\$1,800\text{ per class per term!}}$$

**Re:Learn Dual-Engine Solution**:
- **AST Pre-Screener + Local DistilBERT Classifier**: Handles the deterministic routing offline in $<15\text{ms}$ at **$0.00 infrastructure cost**.
- **LLM Socratic Voice**: Triggered only when the student actively requests conversational dialogue ($\sim 10\%$ of interactions).
- **Cost Reduction**: **$>90\%$ operational savings**, making institutional site licenses highly profitable at $15/student/semester.

### 3.4 Scale Horizon (10,000+ Students)
| Architectural Layer | Hackathon MVP | Scale Horizon (10,000+ Students) |
|---|---|---|
| **Code Execution** | Isolated sub-process sandbox / Pyodide WASM | 100% Client-Side Pyodide WASM (Zero cloud server compute cost) |
| **Misconception Classifier** | Local Calibrated Multinomial Model (<5ms) | Containerized DistilBERT ONNX runtime on Triton Inference Server |
| **Learner Persistence** | SQLite with Write-Ahead Logging (WAL) | Managed PostgreSQL with TimescaleDB event partitioning & Redis cache |
| **Epidemiology Analytics** | REST `/teacher/dashboard` polling | WebSocket / SSE pub-sub for live lab monitoring |
| **Identity & Access** | Anonymous token / localStorage | LTI 1.3 LMS Single Sign-On (Canvas, Blackboard, GradeScope) |

---

## 4. 4-Week Implementation Roadmap

- **Week 1 (Foundations)**: Vite + React + TypeScript scaffold; AntD v6 token system; Monaco editor integration; Pyodide runtime; State machine router.
- **Week 2 (Cognitive Brain)**: Tri-engine arbitration (`AST` + `DistilBERT` + `LLM`); `@ant-design/x` Socratic chat; Cognitive Firewall output leak filter.
- **Week 3 (Closed-Loop Resolution)**: RareUI Step Player isomorphic quizzes; Soundcn audio synthesis; persistent learner model; teacher epidemiology heatmap.
- **Week 4 (Harden & Polish)**: React Bits landing page reveals; Colab transformer fine-tuning on paired hard negatives; 50-prompt adversarial red-teaming eval; 3-minute rehearsed pitch choreography.

---

## 5. Judge Evaluation Takeaway
> *"Cursor fixes syntax and makes students dependent. ChatGPT writes solutions and destroys critical thinking.  
> Re:Learn is the first developer environment built around cognitive science: diagnosing root causes, separating typos from concept gaps, tutoring without leaking answers, and proving learning through isomorphic verification."*
