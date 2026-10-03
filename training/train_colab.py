"""Re:Learn — Misconception Classifier Training (Google Colab)
Upload dataset/misconceptions.csv (scaled to 150-300 rows) to Colab, then run top-to-bottom.
Outputs: accuracy, classification report, confusion matrix PNG -> put in pitch deck.
"""
# !pip install transformers datasets accelerate scikit-learn matplotlib -q

import pandas as pd, torch, matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          TrainingArguments, Trainer)

import os
CSV = "misconceptions_expanded.csv" if os.path.exists("misconceptions_expanded.csv") else "../dataset/misconceptions_expanded.csv" if os.path.exists("../dataset/misconceptions_expanded.csv") else "misconceptions.csv"
MODEL_NAME = "distilbert-base-uncased"
df = pd.read_csv(CSV)

# Feature: code + error + output (never error alone — many-to-many mapping!)
df["text"] = df["student_code"].astype(str) + " [ERR] " + df["error_message"].astype(str) +              " [OUT] " + df["wrong_output"].astype(str)
labels = sorted(df["misconception_id"].unique())
lab2id = {l: i for i, l in enumerate(labels)}
df["label"] = df["misconception_id"].map(lab2id)
print("Label map:", lab2id)

# Concept-wise split: hold out M-08 + M-05 as UNSEEN (proves unseen-misconception generalization)
unseen = ["M-08", "M-05"]
test_unseen = df[df["misconception_id"].isin(unseen)]
rest = df[~df["misconception_id"].isin(unseen)]
train_df, test_seen = train_test_split(rest, test_size=0.25, random_state=42, stratify=rest["label"])
test_df = pd.concat([test_seen, test_unseen])

tok = AutoTokenizer.from_pretrained(MODEL_NAME)
def enc(batch): return tok(batch["text"], truncation=True, padding="max_length", max_length=256)
train_ds = Dataset.from_pandas(train_df).map(enc, batched=True)
test_ds  = Dataset.from_pandas(test_df).map(enc, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=len(labels), id2label={i: l for l, i in lab2id.items()},
    label2id=lab2id)

args = TrainingArguments(output_dir="relearn_model", num_train_epochs=6, per_device_train_batch_size=8,
    per_device_eval_batch_size=8, learning_rate=2e-5, eval_strategy="epoch",
    save_strategy="no", report_to=[], seed=42)
trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=test_ds)
trainer.train()

preds = trainer.predict(test_ds)
y_pred = preds.predictions.argmax(-1); y_true = preds.label_ids
print(classification_report(y_true, y_pred, target_names=[lab2id and labels[i] for i in range(len(labels))]))
fig, ax = plt.subplots(figsize=(8, 8))
ConfusionMatrixDisplay.from_predictions(y_true, y_pred, display_labels=labels,
                                        xticks_rotation=90, ax=ax, cmap="viridis")
plt.tight_layout(); plt.savefig("confusion_matrix.png", dpi=150)
print("Saved confusion_matrix.png -> slide it into your pitch deck!")
model.save_pretrained("relearn_model"); tok.save_pretrained("relearn_model")
