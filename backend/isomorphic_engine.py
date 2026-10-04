"""Re:Learn Dynamic Isomorphic Reassessment & Bayesian Resolution Engine.

Proves learning actually happened across distinct cognitive item types:
- Stage 1: Isomorphic Prediction Challenge (novel parameterization)
- Stage 2: Transfer Problem (different context & structural domain)
- Stage 3: Delayed Retest Verification (ensures retention, avoids one-guess resolution)

Bayesian Knowledge Tracing (BKT) updates misconception probability P(M) after each attempt.
Resolution requires: P(M) <= 0.15 AND >= 2 consecutive stages passed.
"""
import random
from typing import Dict, Any, List, Optional

# Structured 3-Stage Assessment Templates (Prediction -> Transfer -> Delayed Retest)
STAGED_TEMPLATES = {
    "M-01": {
        1: [
            {
                "item_type": "isomorphic_prediction",
                "stage_name": "Stage 1: Isomorphic Prediction",
                "code": "status = {val1}\nif status == {val2}:\n    print('A')\nelse:\n    print('B')",
                "question": "If status is initialized with '=', but line 2 uses '==', what will print?",
                "options": ["A", "B", "SyntaxError", "None"],
                "correct": lambda v1, v2: "A" if v1 == v2 else "B",
                "concept_insight": "In Python, '=' assigns a value into storage, while '==' asks whether two values match."
            }
        ],
        2: [
            {
                "item_type": "transfer_problem",
                "stage_name": "Stage 2: Cross-Domain Transfer",
                "code": "logged_in = False\nuser_id = {val1}\nif user_id == {val2}:\n    logged_in = True\nprint(type(logged_in))",
                "question": "In this transfer scenario, what Python data type is stored in 'logged_in'?",
                "options": ["<class 'bool'>", "<class 'int'>", "<class 'str'>", "SyntaxError"],
                "correct": lambda v1, v2: "<class 'bool'>",
                "concept_insight": "Conditionals test boolean truth values; '==' evaluates to a boolean (True/False)."
            }
        ],
        3: [
            {
                "item_type": "delayed_retest",
                "stage_name": "Stage 3: Delayed Retest Verification",
                "code": "def check_match(target, current):\n    return target == current\n\nresult = check_match({val1}, {val2})\nprint(result)",
                "question": "What does check_match evaluate to when target is {val1} and current is {val2}?",
                "options": lambda v1, v2: ["True", "False", "None", "SyntaxError"],
                "correct": lambda v1, v2: "True" if v1 == v2 else "False",
                "concept_insight": "The function returns the boolean result of comparison '==' directly without mutation."
            }
        ]
    },
    "M-02": {
        1: [
            {
                "item_type": "isomorphic_prediction",
                "stage_name": "Stage 1: Isomorphic Prediction",
                "code": "items = []\nfor i in range({start}, {stop}):\n    items.append(i)\nprint(len(items))",
                "question": "What is the length of the list after the loop completes?",
                "options": lambda s, e: [str(e - s), str(e - s + 1), str(e), str(s)],
                "correct": lambda s, e: str(e - s),
                "concept_insight": "Python's range(a, b) stops strictly before 'b', generating exactly (b - a) numbers."
            }
        ],
        2: [
            {
                "item_type": "transfer_problem",
                "stage_name": "Stage 2: Cross-Domain Transfer",
                "code": "words = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']\nprint(words[{idx}])",
                "question": "Under Python's 0-based indexing, what element does words[{idx}] access?",
                "options": lambda idx: ["alpha", "beta", "gamma", "delta", "epsilon"],
                "correct": lambda idx: ["alpha", "beta", "gamma", "delta", "epsilon"][idx],
                "concept_insight": "Zero-based indexing means index 0 is first, index 1 is second, up to index N-1."
            }
        ],
        3: [
            {
                "item_type": "delayed_retest",
                "stage_name": "Stage 3: Delayed Retest Verification",
                "code": "data = [10, 20, 30]\n# Goal: print the last element safely\nprint(data[len(data) - 1])",
                "question": "Why does data[len(data) - 1] succeed while data[len(data)] throws IndexError?",
                "options": [
                    "A list of length N has valid indices 0 to N-1",
                    "Python lists cannot hold 3 items",
                    "data[len(data)] returns None instead of error",
                    "Indices start at 1 in Python"
                ],
                "correct": lambda: "A list of length N has valid indices 0 to N-1",
                "concept_insight": "Since indexing starts at 0, the N-th element resides at index N-1."
            }
        ]
    },
    "M-03": {
        1: [
            {
                "item_type": "isomorphic_prediction",
                "stage_name": "Stage 1: Isomorphic Prediction",
                "code": "source = [{val1}, {val2}]\npointer = source\npointer.append({val3})\nprint(len(source))",
                "question": "What is len(source) printed at the end?",
                "options": ["2", "3", "Error", "1"],
                "correct": lambda v1, v2, v3: "3",
                "concept_insight": "Assignment 'pointer = source' creates an alias to the same list in memory, not a new copy."
            }
        ],
        2: [
            {
                "item_type": "transfer_problem",
                "stage_name": "Stage 2: Cross-Domain Transfer",
                "code": "original = [{val1}]\ncloned = list(original)\ncloned.append({val2})\nprint(len(original))",
                "question": "Because list() created a shallow copy, what is len(original)?",
                "options": ["1", "2", "0", "TypeError"],
                "correct": lambda v1, v2: "1",
                "concept_insight": "Using list() or .copy() creates an independent container, protecting the original."
            }
        ],
        3: [
            {
                "item_type": "delayed_retest",
                "stage_name": "Stage 3: Delayed Retest Verification",
                "code": "a = [5, 10]\nb = a\nb[0] = 99\nprint(a[0])",
                "question": "What is the value of a[0] after modifying b[0]?",
                "options": ["99", "5", "10", "IndexError"],
                "correct": lambda: "99",
                "concept_insight": "Mutating an object through one alias is visible immediately across all references."
            }
        ]
    },
    "M-05": {
        1: [
            {
                "item_type": "isomorphic_prediction",
                "stage_name": "Stage 1: Isomorphic Prediction",
                "code": "qty = '{val1}'\nfactor = {val2}\nprint(qty * factor)",
                "question": "What does Python produce when multiplying a string by an integer?",
                "options": lambda v1, v2: [str(int(v1) * v2), str(v1) * v2, "TypeError", "None"],
                "correct": lambda v1, v2: str(v1) * v2,
                "concept_insight": "Multiplying a string repeats the sequence; it does not perform arithmetic."
            }
        ],
        2: [
            {
                "item_type": "transfer_problem",
                "stage_name": "Stage 2: Cross-Domain Transfer",
                "code": "val_a = '{val1}'\nval_b = '{val2}'\nprint(val_a + val_b)",
                "question": "What is printed when '+' is used between two text strings?",
                "options": lambda v1, v2: [f"{v1}{v2}", str(int(v1) + int(v2)), "TypeError", "Error"],
                "correct": lambda v1, v2: f"{v1}{v2}",
                "concept_insight": "String '+' is concatenation (joining text), not numeric addition."
            }
        ],
        3: [
            {
                "item_type": "delayed_retest",
                "stage_name": "Stage 3: Delayed Retest Verification",
                "code": "x = '10'\ny = int(x) + 5\nprint(y)",
                "question": "What is printed after explicit conversion with int()?",
                "options": ["15", "105", "TypeError", "None"],
                "correct": lambda: "15",
                "concept_insight": "Explicit type casting converts string representations of numbers to mathematical integers."
            }
        ]
    },
    "M-08": {
        1: [
            {
                "item_type": "isomorphic_prediction",
                "stage_name": "Stage 1: Isomorphic Prediction",
                "code": "def emit(val):\n    print(val)\n\nres = emit({val1})\nprint(res is None)",
                "question": "Does 'res' hold the printed number, or is it None?",
                "options": ["True", "False", "SyntaxError", "Error"],
                "correct": lambda v1: "True",
                "concept_insight": "Functions without a 'return' statement implicitly evaluate to 'None'."
            }
        ],
        2: [
            {
                "item_type": "transfer_problem",
                "stage_name": "Stage 2: Cross-Domain Transfer",
                "code": "def double(x):\n    return x * 2\n\nval = double({val1})\nprint(val)",
                "question": "What value is stored in 'val'?",
                "options": lambda v: [str(v * 2), "None", str(v), "Error"],
                "correct": lambda v: str(v * 2),
                "concept_insight": "The 'return' keyword passes data back to the calling expression for storage or computation."
            }
        ],
        3: [
            {
                "item_type": "delayed_retest",
                "stage_name": "Stage 3: Delayed Retest Verification",
                "code": "def show(msg):\n    print(msg)\n\nx = show('hello')\n# Can x be used in arithmetic or string operations?\nprint(type(x))",
                "question": "What is type(x) after calling a print-only function?",
                "options": ["<class 'NoneType'>", "<class 'str'>", "<class 'int'>", "SyntaxError"],
                "correct": lambda: "<class 'NoneType'>",
                "concept_insight": "Printing sends text to the screen; it does NOT deliver a value into Python memory."
            }
        ]
    },
    "M-09": {
        1: [
            {
                "item_type": "isomorphic_prediction",
                "stage_name": "Stage 1: Slip Verification Check",
                "code": "# Student understands syntax\nlimit = 100\nif limit == 100:\n    print('correct')",
                "question": "Quick check: What is the purpose of '==' on line 3?",
                "options": ["Compare equality", "Assign new value", "Define a variable", "Cast to string"],
                "correct": lambda: "Compare equality",
                "concept_insight": "This was confirmed as an isolated motor slip! Conceptual understanding of equality is intact."
            }
        ],
        2: [
            {
                "item_type": "transfer_problem",
                "stage_name": "Stage 2: Slip vs Bug Differentiation",
                "code": "x = 10\nif x = 10:\n    pass",
                "question": "Why does Python raise SyntaxError on 'if x = 10:'?",
                "options": [
                    "Assignment '=' cannot be used inside an 'if' condition",
                    "Variable x was never declared",
                    "10 is not a valid number",
                    "Missing parentheses around 10"
                ],
                "correct": lambda: "Assignment '=' cannot be used inside an 'if' condition",
                "concept_insight": "Assignments are statements, whereas 'if' requires a boolean condition expression."
            }
        ],
        3: [
            {
                "item_type": "delayed_retest",
                "stage_name": "Stage 3: Motor Slip Self-Correction",
                "code": "score = 95\n# How to test if score is 95?\nif score == 95:\n    print('A')",
                "question": "Which operator correctly compares score against 95?",
                "options": ["==", "=", ":=", "==="],
                "correct": lambda: "==",
                "concept_insight": "Double equals '==' is the comparison operator across Python expressions."
            }
        ]
    }
}

def generate_isomorphic_quiz(misconception_id: str, stage: int = 1) -> Dict[str, Any]:
    """Generates a novel isomorphic prediction or transfer challenge for the specified stage."""
    m_dict = STAGED_TEMPLATES.get(misconception_id, STAGED_TEMPLATES["M-01"])
    stage_key = min(max(stage, 1), 3)
    templates = m_dict.get(stage_key, m_dict[1])
    tmpl = random.choice(templates)

    # Dynamic parameterized values
    v1 = random.randint(1, 9)
    v2 = random.randint(1, 9)
    v3 = random.randint(10, 99)
    start = random.randint(0, 3)
    stop = random.randint(4, 8)
    idx = random.randint(0, 4)

    code_text = tmpl["code"].format(
        val1=v1, val2=v2, val3=v3,
        start=start, stop=stop, idx=idx
    )

    corr_fn = tmpl["correct"]
    try:
        if misconception_id == "M-01":
            corr = corr_fn(v1, v2)
        elif misconception_id == "M-02":
            corr = corr_fn(start, stop) if "items" in code_text else (corr_fn(idx) if "words" in code_text else corr_fn())
        elif misconception_id == "M-03":
            corr = corr_fn(v1, v2, v3) if "pointer" in code_text else (corr_fn(v1, v2) if "cloned" in code_text else corr_fn())
        elif misconception_id == "M-05":
            corr = corr_fn(v1, v2) if callable(corr_fn) and corr_fn.__code__.co_argcount == 2 else corr_fn()
        elif misconception_id == "M-08":
            corr = corr_fn(v1) if callable(corr_fn) and corr_fn.__code__.co_argcount == 1 else corr_fn()
        else:
            corr = corr_fn()
    except Exception:
        corr = "Correct"

    opts_raw = tmpl["options"]
    if callable(opts_raw):
        try:
            if misconception_id == "M-02":
                opts = opts_raw(start, stop) if "items" in code_text else opts_raw(idx)
            elif misconception_id == "M-05":
                opts = opts_raw(v1, v2)
            elif misconception_id == "M-08":
                opts = opts_raw(v1)
            elif misconception_id == "M-01" and stage_key == 3:
                opts = opts_raw(v1, v2)
            else:
                opts = ["A", "B", "C", "D"]
        except Exception:
            opts = ["A", "B", "C", "D"]
    else:
        opts = list(opts_raw)

    if str(corr) not in opts:
        opts[0] = str(corr)
    opts = list(dict.fromkeys(opts))
    random.shuffle(opts)

    return {
        "misconception_id": misconception_id,
        "stage": stage_key,
        "stage_name": tmpl.get("stage_name", f"Stage {stage_key}"),
        "item_type": tmpl.get("item_type", "isomorphic_prediction"),
        "code_snippet": code_text,
        "question": tmpl["question"].format(val1=v1, val2=v2) if "{" in tmpl["question"] else tmpl["question"],
        "options": opts,
        "correct_answer": str(corr),
        "concept_insight": tmpl["concept_insight"]
    }

def update_bayesian_probability(prior_p: float, is_correct: bool, guess_rate: float = 0.25, slip_rate: float = 0.10) -> float:
    """Computes Bayesian Knowledge Tracing (BKT) posterior probability of misconception presence P(M).
    
    A student with misconception M answers correctly with probability:
      P(correct | M) = guess_rate (lucky guess)
    A student without misconception (~M) answers correctly with probability:
      P(correct | ~M) = 1 - slip_rate (mastered, occasional slip)
    """
    prior = min(max(prior_p, 0.01), 0.99)
    if is_correct:
        # P(M | correct) = (P(M) * g) / (P(M) * g + (1 - P(M)) * (1 - s))
        numerator = prior * guess_rate
        denominator = (prior * guess_rate) + ((1.0 - prior) * (1.0 - slip_rate))
        posterior = numerator / denominator
    else:
        # P(M | incorrect) = (P(M) * (1 - g)) / (P(M) * (1 - g) + (1 - P(M)) * s)
        numerator = prior * (1.0 - guess_rate)
        denominator = (prior * (1.0 - guess_rate)) + ((1.0 - prior) * slip_rate)
        posterior = numerator / denominator
    return round(float(min(max(posterior, 0.02), 0.98)), 4)
