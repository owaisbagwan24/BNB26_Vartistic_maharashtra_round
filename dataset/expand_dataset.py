"""Synthetic dataset generator that expands the 20 gold samples
into 180+ diverse, realistic novice student submissions across all 9 misconception classes.
Includes diverse variable names, contexts, syntax permutations, and sloppiness variants.
"""
import csv
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GOLD_CSV = BASE_DIR / "misconceptions.csv"
EXPANDED_CSV = BASE_DIR / "misconceptions_expanded.csv"

# Templates for generating diverse student mistakes
TEMPLATES = {
    "M-01": [
        ("if {var} = {val}:\n    print('{msg}')", "SyntaxError: invalid syntax", "no output", "if {var} == {val}:", "Ask: What is the difference between '=' and '==' in Python?", "If x = 10, is 'x = 10' setting a value or checking equality?"),
        ("while {var} = {val}:\n    {var} += 1", "SyntaxError: invalid syntax", "no output", "while {var} == {val}:", "Ask: In a while condition, do you want to assign or compare?", "How do you test if count is equal to 0?"),
        ("elif {var} = '{val}':\n    status = True", "SyntaxError: invalid syntax", "no output", "elif {var} == '{val}':", "Ask: Does elif test an equality condition or set a variable?", "Is 'role = admin' valid inside an elif? Why not?"),
    ],
    "M-02": [
        ("total = 0\nfor i in range(1, {num}):\n    total += i\nprint(total)", "(none)", "off by one sum", "for i in range(1, {num}+1):", "Ask: In range(1, N), does Python include N?", "What is the last number in range(0, 5)?"),
        ("items = ['a', 'b', 'c']\nprint(items[{idx}])", "IndexError: list index out of range", "no output", "print(items[{idx}-1])", "Ask: Python list indexing begins at what index number?", "What is the index of the first item in any Python list?"),
        ("for i in range({num}):\n    print(i)", "(none)", "starts at 0 expected 1", "for i in range(1, {num}+1):", "Ask: Does range(N) start at 0 or 1?", "Predict all numbers printed by range(4)"),
    ],
    "M-03": [
        ("list1 = [{val1}, {val2}]\nlist2 = list1\nlist2.append({val3})\nprint(list1)", "(none)", "both lists modified", "list2 = list1.copy()", "Ask: Did list2 = list1 copy the elements or link both names?", "If a = [1]; b = a; b.append(2), what is a?"),
        ("def register(user, group=[]):\n    group.append(user)\n    return group", "(none)", "group retains past calls", "def register(user, group=None): group = group or []", "Ask: When is a default list created in a Python function?", "Why is default [] dangerous in function definitions?"),
    ],
    "M-04": [
        ("val = {val1} or {val2}\nprint(val)", "(none)", "expected True/False got number", "val = bool({val1} or {val2})", "Ask: Does 'or' in Python always evaluate to a boolean True/False?", "What is the output of '0 or 5' in Python?"),
        ("if active == True:\n    print('online')", "(none)", "redundant condition", "if active:", "Ask: If active is already a boolean, do you need '== True'?", "Why is 'if is_valid:' preferred over 'if is_valid == True:'?"),
    ],
    "M-05": [
        ("score = '{val1}' + {val2}\nprint(score)", "TypeError: can only concatenate str to str", "no output", "score = int('{val1}') + {val2}", "Ask: Can Python add a text string and a number directly without conversion?", "What is the difference between '3' + '3' and 3 + 3?"),
        ("res = '{val1}' + '{val2}'\nprint(res)", "(none)", "concatenated instead of added", "res = int('{val1}') + int('{val2}')", "Ask: What does '+' do when both sides are enclosed in quotes?", "How do you turn '42' into an integer?"),
    ],
    "M-06": [
        ("{var} = 0\nwhile {var} < {num}:\n    print('tick')", "(runs forever)", "infinite loop", "{var} += 1 inside loop", "Ask: Which line inside the loop changes {var} so the loop can stop?", "What causes an infinite while loop in Python?"),
        ("count = 10\nwhile count > 0:\n    print(count)", "(runs forever)", "infinite loop", "count -= 1 inside loop", "Ask: What line will make count eventually reach 0?", "How do you ensure a while loop terminates?"),
    ],
    "M-07": [
        ("if {var} > {val}:\nprint('greater')", "IndentationError: expected an indented block", "no output", "indent print inside if", "Ask: In Python, how do you show that a line belongs inside an if statement?", "How does Python define the scope of a block without braces {}?"),
        ("for x in range({num}):\n    print(x)\n  print('done')", "IndentationError: unindent does not match any outer indentation level", "no output", "align print('done')", "Ask: Should 'done' print once or every iteration?", "What does inconsistent indentation mean in Python?"),
    ],
    "M-08": [
        ("def calc(a, b):\n    print(a + b)\nres = calc({val1}, {val2})\nprint(res * 2)", "TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'", "no output", "return a + b", "Ask: Does print() send a value back to the variable, or just print to screen?", "What does a function return by default if there is no return statement?"),
        ("def square(n):\n    ans = n * n\nprint(square({num}))", "(none)", "prints None", "return ans", "Ask: ans was calculated, but did the function hand it back to the caller?", "What keyword sends data out of a function?"),
    ],
    "M-09": [
        ("prnt('welcome to python')", "NameError: name 'prnt' is not defined", "no output", "print('welcome to python')", "Typo slip: minor character omission. Correct concept.", "Did you intend the builtin print() function?"),
        ("whlie True:\n    break", "NameError: name 'whlie' is not defined", "no output", "while True:\n    break", "Typo slip: transposed characters in 'while'.", "Notice the spelling of 'while'."),
        ("for i in ragne(5):\n    pass", "NameError: name 'ragne' is not defined", "no output", "for i in range(5):", "Typo slip: transposed characters in 'range'.", "Notice the spelling of 'range'."),
        ("x = 5\nif x = 5:\n    print('five') # Student already knows == in chat", "SyntaxError: invalid syntax", "no output", "x == 5", "Slip under speed. Student previously demonstrated distinction.", "Quick self-check: single = vs double ==?"),
    ]
}

def generate_expanded_dataset():
    rows = []
    # 1. First add original gold samples
    if GOLD_CSV.exists():
        with open(GOLD_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    
    # 2. Synthesize variations for each misconception category
    row_id = 100
    variables = ["count", "total", "score", "index", "num", "val", "age", "speed", "n", "x", "y"]
    
    for category, template_list in TEMPLATES.items():
        # Generate 18-22 variants per category to build a 180+ dataset
        for _ in range(20):
            row_id += 1
            tpl = random.choice(template_list)
            var = random.choice(variables)
            val1 = random.randint(1, 20)
            val2 = random.randint(1, 20)
            val3 = random.randint(21, 50)
            num = random.randint(3, 15)
            idx = random.randint(3, 8)
            msg = random.choice(["valid", "matched", "passed", "success", "alert"])
            
            code = tpl[0].format(var=var, val=val1, val1=val1, val2=val2, val3=val3, num=num, idx=idx, msg=msg)
            correct = tpl[3].format(var=var, val=val1, val1=val1, val2=val2, val3=val3, num=num, idx=idx, msg=msg)
            
            rows.append({
                "id": f"SYN{row_id:04d}",
                "student_code": code,
                "error_message": tpl[1],
                "wrong_output": tpl[2],
                "misconception_id": category,
                "correct_code": correct,
                "socratic_intervention": tpl[4].format(var=var, val=val1, num=num),
                "reassessment_question": tpl[5]
            })

    # Save to expanded CSV
    with open(EXPANDED_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "student_code", "error_message", "wrong_output", "misconception_id", "correct_code", "socratic_intervention", "reassessment_question"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} samples in {EXPANDED_CSV}")

if __name__ == "__main__":
    generate_expanded_dataset()
