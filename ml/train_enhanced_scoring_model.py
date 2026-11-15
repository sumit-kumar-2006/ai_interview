"""
Enhanced Random Forest Training Pipeline
Merges:
1. Original Academic Training Dataset (1,264 records)
2. Hugging Face Interview Coach Dataset (1,227 records from hf_train.jsonl + hf_val.jsonl)
3. Hard Negative & Low-Scoring Samples (160 records: off-topic, one-liners, nonsense)
Total Training Records: ~2,650+ records

Features:
- semantic_similarity
- question_length
- answer_length
- concept_coverage
- keyword_alignment
- technical_depth

Validation:
- 5-Fold Cross Validation
- Evaluation on held-out test set (ml/datasets/features/test_scored.csv)
"""

import os
import sys
import json
import shutil
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.abspath("."))

from ml.rubric_utils import (
    compute_concept_coverage,
    compute_keyword_alignment,
    compute_technical_depth,
    compute_rubric_target_score
)

MODEL_DIR = "ml/models"
MODEL_FILE = os.path.join(MODEL_DIR, "interview_scoring_model.pkl")
METRICS_FILE = os.path.join(MODEL_DIR, "scoring_model_metrics.json")
BACKUP_MODEL_FILE = os.path.join(MODEL_DIR, "interview_scoring_model.pkl.bak")

TRAIN_SCORED_FILE = "ml/datasets/features/train_scored.csv"
TEST_SCORED_FILE = "ml/datasets/features/test_scored.csv"
VAL_SCORED_FILE = "ml/datasets/features/val_scored.csv"

HF_TRAIN_FILE = "ml/datasets/qa/hf_train.jsonl"
HF_VAL_FILE = "ml/datasets/qa/hf_val.jsonl"

FEATURE_COLUMNS = [
    "semantic_similarity",
    "question_length",
    "answer_length",
    "concept_coverage",
    "keyword_alignment",
    "technical_depth"
]

print("=" * 60)
print("  ENHANCED RANDOM FOREST MODEL TRAINING")
print("  Expanded Dataset: Academic + Hugging Face + Hard Negatives")
print("=" * 60)

# Step 1: Load Existing Train Scored Data
print(f"\n[1/6] Loading existing academic training dataset from {TRAIN_SCORED_FILE}...")
df_academic = pd.read_csv(TRAIN_SCORED_FILE)
print(f" -> Academic records: {len(df_academic)}")

# Step 2: Load and Score Hugging Face Dataset
print(f"\n[2/6] Loading Hugging Face Interview dataset ({HF_TRAIN_FILE} & {HF_VAL_FILE})...")
hf_records = []
for hf_path in [HF_TRAIN_FILE, HF_VAL_FILE]:
    if os.path.exists(hf_path):
        with open(hf_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    hf_records.append(json.loads(line))
print(f" -> Loaded {len(hf_records)} raw Hugging Face Q&A records.")

print("Loading SentenceTransformer embedding model (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

hf_questions = [r["question"] for r in hf_records]
hf_answers = [r["answer"] for r in hf_records]

print("Encoding Hugging Face Q&A embeddings for semantic similarity...")
q_embs = embedder.encode(hf_questions, batch_size=64, show_progress_bar=False)
a_embs = embedder.encode(hf_answers, batch_size=64, show_progress_bar=False)

hf_rows = []
for i in range(len(hf_records)):
    q = hf_questions[i]
    a = hf_answers[i]
    sim = float(cosine_similarity([q_embs[i]], [a_embs[i]])[0][0])
    sim = max(0.0, min(1.0, sim))
    q_len = len(q)
    a_len = len(a.strip())

    cov = compute_concept_coverage(q, a)
    align = compute_keyword_alignment(q, a)
    depth = compute_technical_depth(a)
    target = compute_rubric_target_score(sim, cov, align, depth, a_len)

    hf_rows.append({
        "question": q,
        "answer": a,
        "semantic_similarity": sim,
        "question_length": q_len,
        "answer_length": a_len,
        "concept_coverage": cov,
        "keyword_alignment": align,
        "technical_depth": depth,
        "target_score": target
    })

df_hf = pd.DataFrame(hf_rows)
print(f" -> Hugging Face scored records: {len(df_hf)}")

# Step 3: Generate Hard Negative & Low-Scoring Samples
print("\n[3/6] Synthesizing Hard Negative & Low-Scoring Samples (off-topic, nonsense, brief)...")
nonsense_answers = [
    "I like to eat pizza and watch movies on weekends.",
    "The weather is very sunny today and the sky is blue.",
    "I don't know the answer to this question.",
    "Not sure about this topic, let me skip it.",
    "Yes, absolutely correct.",
    "No idea honestly.",
    "margin: 0; padding: 0; display: flex; justify-content: center;",
    "SELECT * FROM users WHERE id = 1;",
    "Just basic coding and stuff like that.",
    "I have never heard of this technology before in my life."
]

negative_rows = []
sample_questions = list(df_academic["question"].sample(n=min(160, len(df_academic)), random_state=42))

for idx, q in enumerate(sample_questions):
    bad_a = nonsense_answers[idx % len(nonsense_answers)]
    q_len = len(q)
    a_len = len(bad_a)

    cov = compute_concept_coverage(q, bad_a)
    align = compute_keyword_alignment(q, bad_a)
    depth = compute_technical_depth(bad_a)
    
    # Calculate genuine low semantic similarity
    q_emb = embedder.encode([q])
    a_emb = embedder.encode([bad_a])
    sim = max(0.0, float(cosine_similarity(q_emb, a_emb)[0][0]))
    
    # Target score heavily penalized (0 to 18 points)
    target = max(0.0, min(20.0, sim * 15.0 + cov * 0.1 + align * 0.05))

    negative_rows.append({
        "question": q,
        "answer": bad_a,
        "semantic_similarity": sim,
        "question_length": q_len,
        "answer_length": a_len,
        "concept_coverage": cov,
        "keyword_alignment": align,
        "technical_depth": depth,
        "target_score": target
    })

df_neg = pd.DataFrame(negative_rows)
print(f" -> Hard Negative records created: {len(df_neg)} (mean target score: {df_neg['target_score'].mean():.1f}%)")

# Step 4: Combine Everything into Expanded Training Dataset
print("\n[4/6] Merging into unified expanded training dataset...")
df_combined = pd.concat([df_academic, df_hf, df_neg], ignore_index=True).drop_duplicates(subset=["question", "answer"])
print(f" -> Total Expanded Training Set: {len(df_combined)} records (was {len(df_academic)})")

# Save updated train_scored
df_combined.to_csv(TRAIN_SCORED_FILE, index=False)

X_train = df_combined[FEATURE_COLUMNS]
y_train = df_combined["target_score"]

# Step 5: 5-Fold Cross-Validation
print("\n[5/6] Executing 5-Fold Cross-Validation on Expanded Dataset...")
kf = KFold(n_splits=5, shuffle=True, random_state=42)

cv_maes = []
cv_rmses = []
cv_r2s = []

for fold, (train_idx, val_idx) in enumerate(kf.split(X_train, y_train), 1):
    X_f_tr, X_f_va = X_train.iloc[train_idx], X_train.iloc[val_idx]
    y_f_tr, y_f_va = y_train.iloc[train_idx], y_train.iloc[val_idx]

    fold_rf = RandomForestRegressor(
        n_estimators=300,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42 + fold,
        n_jobs=-1
    )
    fold_rf.fit(X_f_tr, y_f_tr)
    preds = fold_rf.predict(X_f_va)

    f_mae = mean_absolute_error(y_f_va, preds)
    f_rmse = mean_squared_error(y_f_va, preds) ** 0.5
    f_r2 = r2_score(y_f_va, preds)

    cv_maes.append(f_mae)
    cv_rmses.append(f_rmse)
    cv_r2s.append(f_r2)
    print(f"  Fold {fold}: MAE = {f_mae:.4f} | RMSE = {f_rmse:.4f} | R² = {f_r2:.4f}")

mean_mae = float(np.mean(cv_maes))
mean_rmse = float(np.mean(cv_rmses))
mean_r2 = float(np.mean(cv_r2s))

print(f"\nCV 5-Fold Results on Expanded Dataset ({len(df_combined)} samples):")
print(f"  Mean MAE  : {mean_mae:.4f}")
print(f"  Mean RMSE : {mean_rmse:.4f}")
print(f"  Mean R²   : {mean_r2:.4f}")

# Step 6: Train Final Model on All Data
print("\n[6/6] Training Final Enhanced Model & Evaluating on Test Set...")
enhanced_model = RandomForestRegressor(
    n_estimators=350,
    max_depth=10,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
enhanced_model.fit(X_train, y_train)

# Evaluate on Held-Out Test Set
test_metrics = {}
if os.path.exists(TEST_SCORED_FILE):
    df_test = pd.read_csv(TEST_SCORED_FILE)
    X_test = df_test[FEATURE_COLUMNS]
    y_test = df_test["target_score"]
    test_preds = enhanced_model.predict(X_test)
    test_metrics = {
        "mae": round(float(mean_absolute_error(y_test, test_preds)), 4),
        "rmse": round(float(mean_squared_error(y_test, test_preds) ** 0.5), 4),
        "r2": round(float(r2_score(y_test, test_preds)), 4),
        "sample_count": len(df_test)
    }
    print(f"Held-Out Test Set ({len(df_test)} samples):")
    print(f"  Test MAE  : {test_metrics['mae']}")
    print(f"  Test RMSE : {test_metrics['rmse']}")
    print(f"  Test R²   : {test_metrics['r2']}")

# Backup old model and save new
if os.path.exists(MODEL_FILE):
    shutil.copyfile(MODEL_FILE, BACKUP_MODEL_FILE)
joblib.dump(enhanced_model, MODEL_FILE)
print(f"\nSaved Enhanced Model to {MODEL_FILE}")

# Feature importances
importances = {
    col: round(float(imp), 4)
    for col, imp in zip(FEATURE_COLUMNS, enhanced_model.feature_importances_)
}

# Save updated metadata
metrics_data = {
    "model_type": "EnhancedRandomForestRegressor",
    "training_records": len(df_combined),
    "dataset_breakdown": {
        "academic_records": len(df_academic),
        "huggingface_interview_coach_records": len(df_hf),
        "hard_negative_records": len(df_neg)
    },
    "n_estimators": 350,
    "max_depth": 10,
    "feature_columns": FEATURE_COLUMNS,
    "cross_validation_5_fold": {
        "mean_mae": round(mean_mae, 4),
        "mean_rmse": round(mean_rmse, 4),
        "mean_r2": round(mean_r2, 4),
        "fold_maes": [round(m, 4) for m in cv_maes],
        "fold_r2s": [round(r, 4) for r in cv_r2s]
    },
    "test_metrics": test_metrics,
    "feature_importances": importances
}

with open(METRICS_FILE, "w", encoding="utf-8") as f:
    json.dump(metrics_data, f, indent=4)
print(f"Saved Metadata & Metrics to {METRICS_FILE}")

print("\n" + "=" * 60)
print("TRAINING COMPLETE! THE RANDOM FOREST MODEL IS NOW MUCH SMARTER.")
print("=" * 60)
