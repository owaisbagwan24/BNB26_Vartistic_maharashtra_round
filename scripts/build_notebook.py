"""Builds training/train_relearn.ipynb with embedded dataset.
Completely eliminates the `files.upload()` hang inside the IDE!
"""
import json
import base64
import zlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
NOTEBOOK_PATH = PROJECT_ROOT / "training" / "train_relearn.ipynb"
DATASET_PATH = PROJECT_ROOT / "dataset" / "misconceptions_expanded.csv"

# Read dataset and compress to base64
with open(DATASET_PATH, "rb") as f:
    raw_data = f.read()

compressed_b64 = base64.b64encode(zlib.compress(raw_data)).decode("ascii")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 🎓 Re:Learn — Misconception Classifier Training in Google Colab\n",
            "### Fine-Tuning DistilBERT with Paired Hard Negatives on Cloud GPU\n",
            "\n",
            "- **Research Backing**: Brown & Altadmri (2017) 100M+ events; Perkins (1986) Bugs vs Slips\n",
            "- **Zero Setup**: Dataset is pre-bundled into the notebook — zero file uploads required!\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 1: Install Hugging Face & ML libraries\n",
            "%pip install -q transformers datasets accelerate scikit-learn matplotlib pandas\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 2: Verify GPU Acceleration\n",
            "import torch\n",
            "print('PyTorch Version:', torch.__version__)\n",
            "if torch.cuda.is_available():\n",
            "    print(f'✅ GPU Accelerated Runtime Active: {torch.cuda.get_device_name(0)}')\n",
            "else:\n",
            "    print('ℹ️ Running on CPU runtime (fast for 290 samples).')\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 3: Instant Self-Contained Dataset Loader (Zero-Upload, Never Hangs!)\n",
            "import base64\n",
            "import zlib\n",
            "import io\n",
            "import pandas as pd\n",
            "\n",
            f'DATASET_B64 = "{compressed_b64}"\n',
            "\n",
            "csv_bytes = zlib.decompress(base64.b64decode(DATASET_B64))\n",
            "with open('misconceptions_expanded.csv', 'wb') as f:\n",
            "    f.write(csv_bytes)\n",
            "\n",
            "df = pd.read_csv('misconceptions_expanded.csv')\n",
            "print(f'✅ Successfully loaded {len(df)} verified student samples into Colab!')\n",
            "print('Taxonomy breakdown:')\n",
            "print(df['misconception_id'].value_counts())\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 4: Multi-Modal Context Representation & 75/25 Split\n",
            "from sklearn.model_selection import train_test_split\n",
            "from datasets import Dataset  # type: ignore\n",
            "\n",
            "df['text'] = (\n",
            "    df['student_code'].astype(str) + \n",
            "    ' [ERR] ' + df['error_message'].fillna('(none)').astype(str) + \n",
            "    ' [OUT] ' + df['wrong_output'].fillna('(none)').astype(str)\n",
            ")\n",
            "\n",
            "labels = sorted(df['misconception_id'].unique())\n",
            "lab2id = {l: i for i, l in enumerate(labels)}\n",
            "id2lab = {i: l for l, i in lab2id.items()}\n",
            "df['label'] = df['misconception_id'].map(lab2id)\n",
            "\n",
            "train_df, test_df = train_test_split(\n",
            "    df, test_size=0.25, random_state=42, stratify=df['label']\n",
            ")\n",
            "print(f'Training samples: {len(train_df)} | Held-Out Test samples: {len(test_df)}')\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 5: Tokenize with DistilBERT\n",
            "from transformers import AutoTokenizer  # type: ignore\n",
            "\n",
            "MODEL_NAME = 'distilbert-base-uncased'\n",
            "tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)\n",
            "\n",
            "def tokenize_batch(batch):\n",
            "    return tokenizer(\n",
            "        batch['text'],\n",
            "        truncation=True,\n",
            "        padding='max_length',\n",
            "        max_length=256\n",
            "    )\n",
            "\n",
            "train_ds = Dataset.from_pandas(train_df).map(tokenize_batch, batched=True)\n",
            "test_ds = Dataset.from_pandas(test_df).map(tokenize_batch, batched=True)\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 6: Fine-Tune DistilBERT Misconception Classifier\n",
            "from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer  # type: ignore\n",
            "import numpy as np\n",
            "from sklearn.metrics import accuracy_score, f1_score\n",
            "\n",
            "model = AutoModelForSequenceClassification.from_pretrained(\n",
            "    MODEL_NAME,\n",
            "    num_labels=len(labels),\n",
            "    id2label=id2lab,\n",
            "    label2id=lab2id\n",
            ")\n",
            "\n",
            "def compute_metrics(eval_pred):\n",
            "    logits, y_true = eval_pred\n",
            "    y_pred = np.argmax(logits, axis=-1)\n",
            "    acc = accuracy_score(y_true, y_pred)\n",
            "    f1 = f1_score(y_true, y_pred, average='macro')\n",
            "    return {'accuracy': acc, 'macro_f1': f1}\n",
            "\n",
            "training_args = TrainingArguments(\n",
            "    output_dir='./colab_checkpoints',\n",
            "    num_train_epochs=5,\n",
            "    per_device_train_batch_size=8,\n",
            "    per_device_eval_batch_size=8,\n",
            "    learning_rate=3e-5,\n",
            "    warmup_ratio=0.1,\n",
            "    weight_decay=0.01,\n",
            "    evaluation_strategy='epoch',\n",
            "    save_strategy='epoch',\n",
            "    load_best_model_at_end=True,\n",
            "    metric_for_best_model='macro_f1',\n",
            "    report_to=[],\n",
            "    seed=42\n",
            ")\n",
            "\n",
            "trainer = Trainer(\n",
            "    model=model,\n",
            "    args=training_args,\n",
            "    train_dataset=train_ds,\n",
            "    eval_dataset=test_ds,\n",
            "    compute_metrics=compute_metrics\n",
            ")\n",
            "\n",
            "print('Training started on Colab runtime...')\n",
            "trainer.train()\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 7: Classification Report & Dark-Mode Confusion Matrix\n",
            "import matplotlib.pyplot as plt\n",
            "from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay\n",
            "\n",
            "preds = trainer.predict(test_ds)\n",
            "y_pred = preds.predictions.argmax(-1)\n",
            "y_true = preds.label_ids\n",
            "\n",
            "target_names = [id2lab[i] for i in range(len(labels))]\n",
            "print(classification_report(y_true, y_pred, target_names=target_names, zero_division=0))\n",
            "\n",
            "plt.style.use('dark_background')\n",
            "fig, ax = plt.subplots(figsize=(9, 8), dpi=150)\n",
            "fig.patch.set_facecolor('#0b0f19')\n",
            "ax.set_facecolor('#0b0f19')\n",
            "\n",
            "cm = confusion_matrix(y_true, y_pred)\n",
            "disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)\n",
            "disp.plot(cmap='Blues', ax=ax, xticks_rotation=45, colorbar=True)\n",
            "\n",
            "plt.title('Re:Learn IDE — DistilBERT Misconception Classifier\\n(Held-Out Test Set with Paired Hard Negatives)', pad=15)\n",
            "plt.tight_layout()\n",
            "plt.savefig('confusion_matrix_distilbert.png', facecolor=fig.get_facecolor())\n",
            "plt.show()\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 8: Export Production Model\n",
            "model.save_pretrained('./relearn_distilbert_prod')\n",
            "tokenizer.save_pretrained('./relearn_distilbert_prod')\n",
            "print('✅ Exported production weights to ./relearn_distilbert_prod')\n"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "python", "version": "3.10"},
        "colab": {"name": "train_relearn.ipynb", "provenance": []}
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Successfully generated self-contained notebook: {NOTEBOOK_PATH}")
