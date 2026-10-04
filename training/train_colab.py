# %% [markdown]
# # 🎓 Re:Learn — Cognitive Misconception Classifier
# ### Fine-Tuning DistilBERT on Executable-Verified Hard Negatives (Google Colab GPU)
# 
# **Paper Foundations**: Brown & Altadmri (2017) 100M+ events; Perkins (1986) Bugs vs. Slips  
# **Objective**: Train a transformer on `[Code AST + Error + Output]` to classify student mental models across M-01..M-09 with paired hard negatives.

# %% [markdown]
# ### Step 1: Install Dependencies
# Installs Hugging Face transformers, datasets, and acceleration libraries.

# %%
import sys
import subprocess

# Standard python installation avoiding raw shell magic syntax in .py files
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-q",
    "transformers", "datasets", "accelerate", "scikit-learn", "matplotlib", "pandas"
])
print("✅ Libraries installed successfully.")

# %% [markdown]
# ### Step 2: Verify GPU Acceleration
# Check that a GPU (e.g. NVIDIA T4 or A100) is allocated to your Colab session.

# %%
import torch

print("PyTorch Version:", torch.__version__)
if torch.cuda.is_available():
    print(f"✅ GPU Accelerated Runtime Active: {torch.cuda.get_device_name(0)}")
    print(f"Memory Allocated: {torch.cuda.memory_allocated(0)/(1024**2):.2f} MB")
else:
    print("⚠️ Running on CPU runtime. Go to Runtime -> Change runtime type -> Select T4 GPU.")

# %% [markdown]
# ### Step 3: Load the Mutation-Verified Dataset
# Loads `misconceptions_expanded.csv` (290 verified rows with paired hard negatives).

# %%
import os
import pandas as pd

# Search common paths in workspace / Colab upload
CANDIDATE_PATHS = [
    "dataset/misconceptions_expanded.csv",
    "../dataset/misconceptions_expanded.csv",
    "misconceptions_expanded.csv",
    "/content/misconceptions_expanded.csv",
    "/content/dataset/misconceptions_expanded.csv"
]

dataset_path = next((p for p in CANDIDATE_PATHS if os.path.exists(p)), None)

if dataset_path is None:
    print("⚠️ Dataset not found locally. Uploading via Colab file uploader...")
    try:
        from google.colab import files  # type: ignore
        uploaded = files.upload()
        dataset_path = list(uploaded.keys())[0]
    except Exception:
        raise FileNotFoundError("Please upload 'misconceptions_expanded.csv' to run training.")

df = pd.read_csv(dataset_path)
print(f"✅ Loaded {len(df)} student submission samples from: {dataset_path}")
print("Taxonomy distribution:")
print(df["misconception_id"].value_counts())

# %% [markdown]
# ### Step 4: Multi-Modal Feature Concatenation & Label Mapping
# Concatenate `[Code AST + [ERR] + Error + [OUT] + Output]` to preserve cognitive context.

# %%
# Multi-modal input format: never error alone due to many-to-many dilemma
df["text"] = (
    df["student_code"].astype(str) + 
    " [ERR] " + df["error_message"].fillna("(none)").astype(str) + 
    " [OUT] " + df["wrong_output"].fillna("(none)").astype(str)
)

labels = sorted(df["misconception_id"].unique())
lab2id = {l: i for i, l in enumerate(labels)}
id2lab = {i: l for l, i in lab2id.items()}
df["label"] = df["misconception_id"].map(lab2id)

print(f"Total Cognitive Classes: {len(labels)}")
print("Label mapping:", lab2id)

# %% [markdown]
# ### Step 5: Stratified Train / Test Split
# 75% training, 25% held-out test set evaluated on paired hard negatives.

# %%
from sklearn.model_selection import train_test_split
from datasets import Dataset  # type: ignore

train_df, test_df = train_test_split(
    df, test_size=0.25, random_state=42, stratify=df["label"]
)

print(f"Training Samples: {len(train_df)} | Held-Out Test Samples: {len(test_df)}")

# %% [markdown]
# ### Step 6: Tokenize & Prepare Transformer Datasets
# Uses `distilbert-base-uncased` tokenizer with max sequence length 256.

# %%
from transformers import AutoTokenizer  # type: ignore

MODEL_NAME = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_batch(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=256
    )

train_ds = Dataset.from_pandas(train_df).map(tokenize_batch, batched=True)
test_ds = Dataset.from_pandas(test_df).map(tokenize_batch, batched=True)

# %% [markdown]
# ### Step 7: Train Misconception Classifier with Trainer API
# 5 epochs, AdamW optimizer with warmup, linear learning rate decay.

# %%
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer  # type: ignore
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(labels),
    id2label=id2lab,
    label2id=lab2id
)

def compute_metrics(eval_pred):
    logits, y_true = eval_pred
    y_pred = np.argmax(logits, axis=-1)
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="macro")
    return {"accuracy": acc, "macro_f1": f1}

# Dynamic compatibility with both transformers 4.x and 5.x
strategy_key = "eval_strategy" if hasattr(TrainingArguments, "eval_strategy") else "evaluation_strategy"
train_kwargs = {
    "output_dir": "./relearn_distilbert_checkpoints",
    "num_train_epochs": 5,
    "per_device_train_batch_size": 8,
    "per_device_eval_batch_size": 8,
    "learning_rate": 3e-5,
    "weight_decay": 0.01,
    strategy_key: "epoch",
    "save_strategy": "epoch",
    "load_best_model_at_end": True,
    "metric_for_best_model": "macro_f1",
    "report_to": [],
    "seed": 42
}
training_args = TrainingArguments(**train_kwargs)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=test_ds,
    compute_metrics=compute_metrics
)

print("Starting transformer fine-tuning on Colab GPU...")
trainer.train()

# %% [markdown]
# ### Step 8: Comprehensive Evaluation & Pitch Confusion Matrix
# Generates classification report and pitch-ready dark-mode confusion matrix.

# %%
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

preds = trainer.predict(test_ds)
y_pred = preds.predictions.argmax(-1)
y_true = preds.label_ids

print("=" * 65)
print("             RE:LEARN CLASSIFICATION REPORT (HELD-OUT TEST)       ")
print("=" * 65)
target_names = [id2lab[i] for i in range(len(labels))]
print(classification_report(y_true, y_pred, target_names=target_names, zero_division=0))

# Pitch-Ready Dark Mode Confusion Matrix
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(9, 8), dpi=150)
fig.patch.set_facecolor("#0b0f19")
ax.set_facecolor("#0b0f19")

cm = confusion_matrix(y_true, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)
disp.plot(cmap="Blues", ax=ax, xticks_rotation=45, colorbar=True)

plt.title("Re:Learn IDE — DistilBERT Misconception Classifier\n(Fine-Tuned on Executable Hard Negatives)", 
          fontsize=13, fontweight="bold", pad=15, color="#f1f5f9")
plt.xlabel("Predicted Misconception Label", fontsize=11, labelpad=10, color="#cbd5e1")
plt.ylabel("Ground Truth Cognitive Misconception", fontsize=11, labelpad=10, color="#cbd5e1")
plt.tight_layout()

plt.savefig("confusion_matrix_distilbert.png", facecolor=fig.get_facecolor(), edgecolor="none")
print("✅ Saved high-res confusion matrix: confusion_matrix_distilbert.png")
plt.show()

# %% [markdown]
# ### Step 9: Save Production Model & Tokenizer
# Saves weights for local deployment in Re:Learn backend.

# %%
SAVE_DIR = "./relearn_distilbert_prod"
model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)
print(f"🎉 Model exported successfully to: {SAVE_DIR}")
print("You can copy these weights into backend/ for local PyTorch transformer inference!")
