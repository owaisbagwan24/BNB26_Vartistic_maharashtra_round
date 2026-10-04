import csv
import json
import pickle
import sys
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent

with open(BASE / "backend" / "classifier.pkl", "rb") as f:
    clf = pickle.load(f)

pilot_rows = list(csv.DictReader(open(BASE / "dataset" / "pilot_student_samples.csv", encoding="utf-8")))
X = [f"{r['student_code']} [ERR] {r['error_message']} [OUT] {r['wrong_output']}" for r in pilot_rows]
y_true = [r["true_misconception_id"] for r in pilot_rows]
y_pred = clf.predict(X)

acc = accuracy_score(y_true, y_pred)
print(f"Real-Student Pilot Accuracy (n={len(pilot_rows)}): {acc*100:.1f}%")
print("=" * 60)
for r, pred in zip(pilot_rows, y_pred):
    ok = "PASS" if pred == r["true_misconception_id"] else "FAIL"
    print(f"  [{ok}] {r['sample_id']}: Expected={r['true_misconception_id']} | Predicted={pred} ({r['student_level']})")

pilot_report = {
    "pilot_sample_count": len(pilot_rows),
    "accuracy": round(float(acc), 4),
    "student_cohorts": ["CS1-Week1", "CS1-Week2", "CS1-Week3", "CS1-Week4"],
    "details": [
        {
            "id": r["sample_id"],
            "true_label": r["true_misconception_id"],
            "predicted_label": pred,
            "correct": bool(pred == r["true_misconception_id"])
        }
        for r, pred in zip(pilot_rows, y_pred)
    ]
}

with open(BASE / "training" / "pilot_eval_report.json", "w", encoding="utf-8") as f:
    json.dump(pilot_report, f, indent=2)
print("=" * 60)
print(f"Saved pilot evaluation report -> training/pilot_eval_report.json")
