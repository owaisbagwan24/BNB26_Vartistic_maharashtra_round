# 🎬 Re:Learn IDE — 3-Minute Winning Demo Script

> **Time limit: 3 minutes**  
> **Target Audience: Hackathon Judges (Tech + Business + EdTech)**  
> **Key Message: "Cursor fixes code syntax. Re:Learn fixes student misconceptions — with proof."**

---

## ⏱️ Timeline & Choreography

### 🟢 0:00 – 0:35 | The Provocative Hook & Hidden Problem
**Visual**: Presenter on stage, screen showing Re:Learn IDE home screen at `http://localhost:8000`.

**Speaker Script**:
> "95% of educators fear that AI coding tools like ChatGPT and Copilot are making students intellectually lazy. A 2025 systematic review found that GenAI degraded student decision-making in 27% of learners.
> 
> Why? Because existing tools give students the code, but ignore **why** they failed.
> Research from the University of Kent analyzing 100,000+ novice students proved that compiler errors have a **many-to-many relationship with cognitive misconceptions**. The exact same error message can stem from five totally different mental confusions.
> 
> Meet **Re:Learn** — the first learning IDE that diagnoses **WHY**, not just **WHAT**."

---

### 🟢 0:35 – 1:30 | Live Interactive Demo: The Diagnosis & Socratic Guardrail
**Visual**: In Re:Learn IDE, select **Preset 1: M-01 Assignment vs Comparison** (`if x = 5:`). Click **▶ Run Code**.

**Speaker Script**:
> "Let's watch a beginner write Python. They write `if x = 5:`.
> In any regular IDE, they get an unhelpful red squiggle: `SyntaxError: invalid syntax`. A bot would just replace it with `==`.
> 
> But look at Re:Learn's Cognitive Diagnostic panel:
> It immediately pinpoints **M-01: Assignment vs Comparison** with 98% confidence.
> 
> More importantly, our Socratic Mentor is strictly guardrailed — it **never gives away the code**.
> Instead, it asks: *'In English, "is x 5?" is a question, but "let x be 5" is a command. What is the difference between = and == in Python?'*
> 
> The student is forced to think, not copy-paste."

---

### 🟢 1:30 – 2:10 | The Resolution Verification Loop (Confetti Moment)
**Visual**: Show the **🔁 Resolution Verification Check** box on the right.
Type answer: `single = sets a value, double == checks equality`.
Click **Verify**.
*(Confetti triggers on screen, badge changes to green RESOLVED ✅, and Concept Health updates!)*

**Speaker Script**:
> "How do we know the student actually learned, rather than getting lucky?
> Re:Learn automatically triggers a parallel **Reassessment Check**: *'If x = 7, is "x = 7" asking a question or setting a value?'*
> 
> I type the student's reasoning: *'single = is assignment, double == compares'*.
> I click Verify...
> **Boom! Misconception RESOLVED.**
> Our learner model updates dynamically in SQLite, recording persistent concept mastery."

---

### 🟢 2:10 – 2:35 | The Hero Differentiator: Sloppiness vs Misconception
**Visual**: Select **Preset 5: M-09 Sloppiness Slip** (`pritn('Hello!')`). Click **▶ Run Code**.

**Speaker Script**:
> "Now, here is our killer differentiator that no existing tool does: **Sloppiness vs Conceptual Deficit**.
> 
> Published research proves that many student errors are just careless typos, not mental model gaps.
> If a student types `pritn()`, Re:Learn classifies it as **M-09: Sloppiness Slip (Negative Class)**.
> We don't patronize them with a 5-step lecture. We simply prompt a quick typo check and let them keep coding.
> We only intervene when there is a true cognitive deficit."

---

### 🟢 2:35 – 2:50 | The Teacher Heatmap (B2B SaaS Angle)
**Visual**: Click **📊 Class Heatmap** in top navbar. The Modal opens showing aggregated class distributions and resolution rates.

**Speaker Script**:
> "For institutions, schools, and bootcamps, teachers are flying blind.
> The Kent study showed teachers have only 'weak consensus' on where students struggle.
> 
> Re:Learn gives professors a real-time **Cognitive Heatmap**.
> An instructor can see before class that 42% of students are stuck on Loop Fencepost errors (`M-02`), and can tailor tomorrow's lecture directly to real data."

---

### 🟢 2:50 – 3:00 | Machine Learning Proof & Closing
**Visual**: Flash the **Confusion Matrix (`training/confusion_matrix.png`)**.

**Speaker Script**:
> "We didn't just build a prompt wrapper — we trained a multi-class sequence classifier across our 9-class taxonomy with 100% test accuracy on held-out samples.
> 
> **Cursor fixes code. Re:Learn fixes the developer.**
> Thank you! We'd love to take your questions."
