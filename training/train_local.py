"""Re:Learn Local Training & Evaluation Pipeline
Trains an interpretable, high-accuracy Misconception Classifier on the expanded dataset.
Zero-dependency CSV loader (no pandas needed).

Implements:
1. Multi-modal feature representation: Code AST text + Runtime Error + Wrong Output
2. Multi-class Cognitive Misconception Classifier (M-01 to M-09)
3. Direct Sloppiness vs Conceptual Deficit differentiation metric
4. Confusion Matrix generator for Pitch Deck (confusion_matrix.png)
"""
import csv
import json
from pathlib import Path
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATASET_PATH = PROJECT_ROOT / "dataset" / "misconceptions_expanded.csv"

def run_training():
    if not DATASET_PATH.exists():
        print(f"Error: {DATASET_PATH} not found.")
        return

    texts = []
    labels = []

    with open(DATASET_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Feature: Student code + Error + Wrong Output
            # Never error alone due to many-to-many misconception mapping
            snippet = f"{row['student_code']} [ERR] {row.get('error_message', '')} [OUT] {row.get('wrong_output', '')}"
            texts.append(snippet)
            labels.append(row["misconception_id"])

    print(f"Loaded {len(texts)} student submission samples.")
    all_labels = sorted(list(set(labels)))
    print(f"Taxonomy categories ({len(all_labels)}): {', '.join(all_labels)}")

    # 1. Stratified Train / Test Split (75% train, 25% test)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )
    print(f"Train split: {len(X_train)} samples | Test split: {len(X_test)} samples")

    # 2. Pipeline: Sublinear N-Gram TF-IDF + Calibrated Multi-class Logistic Classifier
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=1,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            C=8.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        ))
    ])

    print("\nTraining Misconception Classifier...")
    pipeline.fit(X_train, y_train)

    # 3. Evaluation
    y_pred = pipeline.predict(X_test)

    print("\n================ CLASSIFICATION REPORT ================")
    report_text = classification_report(y_test, y_pred, zero_division=0)
    print(report_text)
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    accuracy = report_dict["accuracy"]
    print(f"Overall Accuracy: {accuracy * 100:.2f}%")

    # 4. Generate Pitch-Deck Ready Confusion Matrix
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(9, 8), dpi=150)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#0b0f19")

    cm = confusion_matrix(y_test, y_pred, labels=all_labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=all_labels)
    disp.plot(cmap="Blues", ax=ax, xticks_rotation=45, colorbar=True)

    plt.title("Re:Learn IDE — Misconception Classifier Confusion Matrix\n(Evaluation on Held-Out Test Set)", 
              fontsize=13, fontweight="bold", pad=15, color="#f1f5f9")
    plt.xlabel("Predicted Misconception Label", fontsize=11, labelpad=10, color="#cbd5e1")
    plt.ylabel("Ground Truth Cognitive Misconception", fontsize=11, labelpad=10, color="#cbd5e1")
    plt.tight_layout()

    cm_path = BASE_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, facecolor=fig.get_facecolor(), edgecolor="none")
    print(f"\nSaved pitch-ready Confusion Matrix to: {cm_path}")

    # 5. Save Evaluation Metrics JSON
    metrics = {
        "dataset_samples": len(texts),
        "classes": all_labels,
        "test_samples": len(X_test),
        "overall_accuracy": round(accuracy, 4),
        "macro_f1": round(report_dict["macro avg"]["f1-score"], 4),
        "sloppiness_precision": round(report_dict.get("M-09", {}).get("precision", 1.0), 4),
        "sloppiness_recall": round(report_dict.get("M-09", {}).get("recall", 1.0), 4),
    }

    metrics_path = BASE_DIR / "training_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved training metrics to: {metrics_path}")

if __name__ == "__main__":
    run_training()
