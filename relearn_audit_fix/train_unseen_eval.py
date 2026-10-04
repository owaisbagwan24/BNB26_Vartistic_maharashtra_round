"""Leave-One-Label-Out (LOLO) evaluation — the MISSING piece for the hackathon.

Problem statement requires: "performance on misconceptions NOT SEEN during training."
Stratified random split does NOT test this. LOLO does: for each label L, train on all
other labels, test ONLY on L. Report mean/min per-label accuracy.

Run:  python training/train_unseen_eval.py
Then: paste results into training/training_metrics.json + README badges + PITCH slide 6.
"""
import csv, json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score

BASE = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(BASE/"dataset"/"misconceptions_expanded.csv", encoding="utf-8")))
texts = [f"{r['student_code']} [ERR] {r.get('error_message','')} [OUT] {r.get('wrong_output','')}" for r in rows]
labels = [r["misconception_id"] for r in rows]
all_labels = sorted(set(labels))

def make_pipe():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,3), min_df=1, sublinear_tf=True,
                                  token_pattern=r"(?u)\b\w+\b|[=+\-*/<>:!%]+")),
        ("clf", LogisticRegression(C=4.5, max_iter=3000)),
    ])

print("Leave-One-Label-Out evaluation (unseen misconceptions):")
print("=" * 60)
per_label = {}
for held in all_labels:
    Xtr = [t for t, l in zip(texts, labels) if l != held]
    ytr = [l for l in labels if l != held]
    Xte = [t for t, l in zip(texts, labels) if l == held]
    yte = [l for l in labels if l == held]
    if len(Xte) < 3:
        continue
    pipe = make_pipe().fit(Xtr, ytr)
    acc = accuracy_score(yte, pipe.predict(Xte))
    per_label[held] = round(acc, 3)
    print(f"  Unseen {held}: {acc*100:.1f}%  (n={len(Xte)} test, trained WITHOUT any {held})")

mean_acc = float(np.mean(list(per_label.values())))
min_acc = float(np.min(list(per_label.values())))
print("=" * 60)
print(f"LOLO mean accuracy on NEVER-SEEN misconceptions: {mean_acc*100:.1f}%")
print(f"LOLO worst-case: {min_acc*100:.1f}%  <- show BOTH numbers in pitch")

out = {
  "evaluation": "leave_one_label_out",
  "unseen_misconception_accuracy_mean": round(mean_acc, 4),
  "unseen_misconception_accuracy_min": round(min_acc, 4),
  "per_label": per_label,
  "note": "Stratified split (98.6%) = seen-concept performance. THIS = unseen-concept performance. Report both."
}
with open(BASE/"training"/"lolo_eval_report.json", "w") as f:
    json.dump(out, f, indent=2)
print("Saved -> training/lolo_eval_report.json")
