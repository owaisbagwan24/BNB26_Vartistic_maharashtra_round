"""Re:Learn Dynamic Isomorphic Reassessment & Resolution Engine.

Proves learning actually happened (closing the cognitive loop):
- Generates novel isomorphic prediction challenges testing the identical concept with fresh surface forms.
- Replaces static questions with parameterized problem generators.
- Manages 3-tier escalation:
    Tier 1: Subtle mental model analogy
    Tier 2: Guided decomposition / step-by-step trace
    Tier 3: Scaffolded fill-in & instructor queue flag
"""
import random
from typing import Dict, Any, List

ISOMORPHIC_TEMPLATES = {
    "M-01": [
        {
            "code": "status = {val1}\nif status == {val2}:\n    print('A')\nelse:\n    print('B')",
            "question": "If status is initialized with '=', but line 2 uses '==', what will print?",
            "options": ["A", "B", "SyntaxError", "None"],
            "correct": lambda v1, v2: "A" if v1 == v2 else "B",
            "concept_insight": "In Python, '=' assigns a value into storage, while '==' asks whether two values match."
        },
        {
            "code": "count = {val1}\ncheck = (count == {val2})\nprint(type(check))",
            "question": "What is the data type stored in variable 'check'?",
            "options": ["<class 'int'>", "<class 'bool'>", "<class 'str'>", "SyntaxError"],
            "correct": lambda v1, v2: "<class 'bool'>",
            "concept_insight": "Comparison with '==' produces a boolean value (True or False), not an assignment."
        }
    ],
    "M-02": [
        {
            "code": "items = []\nfor i in range({start}, {stop}):\n    items.append(i)\nprint(len(items))",
            "question": "What is the length of the list after the loop completes?",
            "options": lambda s, e: [str(e - s), str(e - s + 1), str(e), str(s)],
            "correct": lambda s, e: str(e - s),
            "concept_insight": "Python's range(a, b) stops strictly before 'b', generating exactly (b - a) numbers."
        },
        {
            "code": "words = ['apple', 'berry', 'cherry', 'date']\nprint(words[{idx}])",
            "question": "What element does this line access?",
            "options": lambda idx: ["apple", "berry", "cherry", "date"],
            "correct": lambda idx: ["apple", "berry", "cherry", "date"][idx],
            "concept_insight": "Zero-based indexing means element 0 is the first item, and element (n-1) is the last item."
        }
    ],
    "M-03": [
        {
            "code": "source = [{val1}, {val2}]\npointer = source\npointer.append({val3})\nprint(len(source))",
            "question": "What is len(source) printed at the end?",
            "options": ["2", "3", "Error", "1"],
            "correct": lambda v1, v2, v3: "3",
            "concept_insight": "Assignment 'pointer = source' creates an alias to the same list in memory, not a new copy."
        },
        {
            "code": "a = [10]\nb = a\nb = [20]\nprint(a[0])",
            "question": "What is printed by print(a[0])?",
            "options": ["10", "20", "None", "IndexError"],
            "correct": lambda: "10",
            "concept_insight": "Reassigning 'b = [20]' binds the name 'b' to a brand-new list without mutating 'a'."
        }
    ],
    "M-05": [
        {
            "code": "qty = '{val1}'\nfactor = {val2}\nprint(qty * factor)",
            "question": "What does Python produce when multiplying a string by an integer?",
            "options": lambda v1, v2: [str(int(v1) * v2), str(v1) * v2, "TypeError", "None"],
            "correct": lambda v1, v2: str(v1) * v2,
            "concept_insight": "Multiplying a string by an integer repeats the text; it does not perform arithmetic."
        },
        {
            "code": "val_a = '{val1}'\nval_b = '{val2}'\nprint(val_a + val_b)",
            "question": "What is printed when '+' is used between two strings?",
            "options": lambda v1, v2: [f"{v1}{v2}", str(int(v1) + int(v2)), "TypeError", "Error"],
            "correct": lambda v1, v2: f"{v1}{v2}",
            "concept_insight": "String concatenation links text characters together instead of calculating mathematical sum."
        }
    ],
    "M-08": [
        {
            "code": "def emit(val):\n    print(val)\n\nres = emit({val1})\nprint(res is None)",
            "question": "Does 'res' hold the printed number, or is it None?",
            "options": ["True", "False", "SyntaxError", "Error"],
            "correct": lambda v1: "True",
            "concept_insight": "Functions that do not explicitly 'return' a value evaluate to 'None' in the caller."
        },
        {
            "code": "def triple(x):\n    return x * 3\n\nval = triple({val1})\nprint(val)",
            "question": "What is the value of 'val'?",
            "options": lambda v: [str(v * 3), "None", str(v), "Error"],
            "correct": lambda v: str(v * 3),
            "concept_insight": "The 'return' statement passes the computed result directly back to the calling expression."
        }
    ],
    "M-09": [
        {
            "code": "# Student understands syntax\nlimit = 100\nif limit == 100:\n    print('correct')",
            "question": "Quick check: What is the purpose of '==' on line 3?",
            "options": ["Compare equality", "Assign new value", "Define a variable", "Cast to string"],
            "correct": lambda: "Compare equality",
            "concept_insight": "This was identified as a motor slip! Your conceptual understanding of equality is solid."
        }
    ]
}

def generate_isomorphic_quiz(misconception_id: str) -> Dict[str, Any]:
    """Generates a novel isomorphic prediction problem with dynamic parameterization."""
    templates = ISOMORPHIC_TEMPLATES.get(misconception_id, ISOMORPHIC_TEMPLATES["M-01"])
    tmpl = random.choice(templates)
    
    # Generate dynamic values
    v1 = random.randint(1, 9)
    v2 = random.randint(1, 9)
    v3 = random.randint(10, 99)
    start = random.randint(0, 3)
    stop = random.randint(4, 8)
    idx = random.randint(0, 3)
    
    code_text = tmpl["code"].format(
        val1=v1, val2=v2, val3=v3,
        start=start, stop=stop, idx=idx
    )
    
    # Compute correct answer
    corr_fn = tmpl["correct"]
    try:
        if misconception_id == "M-01":
            corr = corr_fn(v1, v2)
        elif misconception_id == "M-02":
            corr = corr_fn(start, stop) if "items" in code_text else corr_fn(idx)
        elif misconception_id == "M-03":
            corr = corr_fn(v1, v2, v3) if "pointer" in code_text else corr_fn()
        elif misconception_id == "M-05":
            corr = corr_fn(v1, v2)
        elif misconception_id == "M-08":
            corr = corr_fn(v1) if "emit" in code_text else corr_fn(v1)
        else:
            corr = corr_fn()
    except Exception:
        corr = "Correct"

    # Compute options
    opts_raw = tmpl["options"]
    if callable(opts_raw):
        if misconception_id == "M-02":
            opts = opts_raw(start, stop) if "items" in code_text else opts_raw(idx)
        elif misconception_id == "M-05":
            opts = opts_raw(v1, v2)
        elif misconception_id == "M-08":
            opts = opts_raw(v1)
        else:
            opts = ["A", "B", "C", "D"]
    else:
        opts = list(opts_raw)
        
    # Ensure correct option is present and deduplicated
    if corr not in opts:
        opts[0] = corr
    opts = list(dict.fromkeys(opts))
    random.shuffle(opts)
    
    return {
        "misconception_id": misconception_id,
        "is_isomorphic": True,
        "code_snippet": code_text,
        "question": tmpl["question"],
        "options": opts,
        "correct_answer": str(corr),
        "concept_insight": tmpl["concept_insight"],
        "tier": 1
    }

def evaluate_isomorphic_attempt(quiz_data: Dict[str, Any], student_answer: str, attempt_number: int = 1) -> Dict[str, Any]:
    """Evaluates student answer with multi-tier escalation."""
    ans = student_answer.strip().lower()
    correct = str(quiz_data.get("correct_answer", "")).strip().lower()
    
    is_correct = (ans == correct) or (correct in ans)
    
    if is_correct:
        return {
            "resolved": True,
            "escalate": False,
            "tier": attempt_number,
            "message": "Spot on! You demonstrated genuine conceptual understanding across fresh surface syntax.",
            "concept_insight": quiz_data.get("concept_insight", "")
        }
    
    # Escalation tiers
    if attempt_number == 1:
        return {
            "resolved": False,
            "escalate": True,
            "tier": 2,
            "hint": f"Take a close look at the code: {quiz_data.get('concept_insight', '')}",
            "message": "Not quite yet. Trace the variables step by step before looking at the output."
        }
    else:
        return {
            "resolved": False,
            "escalate": True,
            "tier": 3,
            "hint": "Flagged for instructor office-hour assistance.",
            "message": "You're encountering a tricky mental model hurdle. We've added this to your review queue."
        }
