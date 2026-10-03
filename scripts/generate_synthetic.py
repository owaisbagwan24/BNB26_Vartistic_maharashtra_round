"""Generate synthetic labeled training rows with an LLM, then HUMAN-VERIFY each one.
Usage: python generate_synthetic.py  (set GROQ_API_KEY first)
"""
import csv, json, os, sys
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
schema = json.load(open("../dataset/label_schema.json"))["labels"]

def gen_for(label_id, label_info, n=6):
    prompt = f"""You are building a dataset of NOVICE Python student mistakes.
Create {n} realistic student submissions for misconception {label_id}: {label_info['name']} — {label_info['desc']}.
Make them DIVERSE (different variable names, topics, contexts). Also include realistic wrong outputs.
Return STRICT JSON array of objects with keys:
student_code, error_message (empty string if code runs), wrong_output,
socratic_intervention (a guiding QUESTION, never the answer), reassessment_question.
Example misconception: {label_info['example']}"""

    r = client.chat.completions.create(model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}, temperature=0.9)
    data = json.loads(r.choices[0].message.content)
    items = data if isinstance(data, list) else data.get("items", data.get("examples", []))
    return items

def main():
    out = open("synthetic_raw.csv", "w", newline="")
    w = csv.writer(out)
    w.writerow(["id","student_code","error_message","wrong_output","misconception_id",
                "correct_code","socratic_intervention","reassessment_question"])
    i = 9000
    for lid, info in schema.items():
        if lid == "M-09":
            continue  # sloppiness rows: write manually, LLM often fakes them
        for item in gen_for(lid, info):
            i += 1
            w.writerow([f"SYN{i}", item["student_code"], item.get("error_message",""),
                        item.get("wrong_output",""), lid, "",
                        item["socratic_intervention"], item["reassessment_question"]])
    out.close()
    print("Done -> synthetic_raw.csv. NOW: manually verify each row, fix wrong labels, "
          "then append to dataset/misconceptions.csv")

if __name__ == "__main__":
    main()
