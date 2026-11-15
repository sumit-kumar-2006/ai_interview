import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure root directory on path
sys.path.insert(0, os.path.abspath("."))

FEATURES_DIR = "ml/datasets/features"
TRAIN_FILE = os.path.join(FEATURES_DIR, "train_scored.csv")
VAL_FILE = os.path.join(FEATURES_DIR, "val_scored.csv")
TEST_FILE = os.path.join(FEATURES_DIR, "test_scored.csv")

MODEL_DIR = "ml/models"
MODEL_FILE = os.path.join(MODEL_DIR, "interview_scoring_model.pkl")
METRICS_FILE = os.path.join(MODEL_DIR, "scoring_model_metrics.json")

print("========================================")
print("  TRAINING MULTI-CRITERIA SCORING MODEL")
print("  With 5-Fold Cross-Validation")
print("========================================")

# 1. Load Scored Datasets
train_df = pd.read_csv(TRAIN_FILE)
val_df = pd.read_csv(VAL_FILE) if os.path.exists(VAL_FILE) else None
test_df = pd.read_csv(TEST_FILE) if os.path.exists(TEST_FILE) else None

print(f"Training records   : {len(train_df)}")
if val_df is not None:
    print(f"Validation records : {len(val_df)}")
if test_df is not None:
    print(f"Test records       : {len(test_df)}")

# 2. Multi-Criteria Features
FEATURE_COLUMNS = [
    "semantic_similarity",
    "question_length",
    "answer_length",
    "concept_coverage",
    "keyword_alignment",
    "technical_depth"
]

X_train = train_df[FEATURE_COLUMNS]
y_train = train_df["target_score"]

print("\nFeatures used in training:")
for idx, f in enumerate(FEATURE_COLUMNS, 1):
    print(f"  {idx}. {f}")

# 3. 5-Fold Cross-Validation
print("\n----------------------------------------")
print("Executing 5-Fold Cross-Validation...")
print("----------------------------------------")

kf = KFold(n_splits=5, shuffle=True, random_state=42)

cv_maes = []
cv_rmses = []
cv_r2s = []

for fold, (train_idx, val_idx) in enumerate(kf.split(X_train, y_train), 1):
    X_f_train, X_f_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
    y_f_train, y_f_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

    fold_model = RandomForestRegressor(
        n_estimators=250,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42 + fold,
        n_jobs=-1
    )
    fold_model.fit(X_f_train, y_f_train)
    fold_preds = fold_model.predict(X_f_val)

    f_mae = mean_absolute_error(y_f_val, fold_preds)
    f_rmse = mean_squared_error(y_f_val, fold_preds) ** 0.5
    f_r2 = r2_score(y_f_val, fold_preds)

    cv_maes.append(f_mae)
    cv_rmses.append(f_rmse)
    cv_r2s.append(f_r2)

    print(f"  Fold {fold}: MAE = {f_mae:.4f} | RMSE = {f_rmse:.4f} | R² = {f_r2:.4f}")

mean_cv_mae = float(np.mean(cv_maes))
mean_cv_rmse = float(np.mean(cv_rmses))
mean_cv_r2 = float(np.mean(cv_r2s))

print(f"\nCV Average (5 Folds):")
print(f"  Mean MAE  : {mean_cv_mae:.4f} (+/- {np.std(cv_maes):.4f})")
print(f"  Mean RMSE : {mean_cv_rmse:.4f} (+/- {np.std(cv_rmses):.4f})")
print(f"  Mean R²   : {mean_cv_r2:.4f} (+/- {np.std(cv_r2s):.4f})")

# 4. Train Final Model on Full Training Set
print("\n----------------------------------------")
print("Training Final Model on Full Training Set...")
print("----------------------------------------")

final_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=8,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
final_model.fit(X_train, y_train)

# Evaluate on Full Train Set
train_preds = final_model.predict(X_train)
train_mae = float(mean_absolute_error(y_train, train_preds))
train_rmse = float(mean_squared_error(y_train, train_preds) ** 0.5)
train_r2 = float(r2_score(y_train, train_preds))

print(f"Train Set Metrics:")
print(f"  MAE  : {train_mae:.4f}")
print(f"  RMSE : {train_rmse:.4f}")
print(f"  R²   : {train_r2:.4f}")

# 5. Evaluate on Validation Set
val_metrics = {}
if val_df is not None:
    X_val = val_df[FEATURE_COLUMNS]
    y_val = val_df["target_score"]
    val_preds = final_model.predict(X_val)
    val_metrics = {
        "mae": float(mean_absolute_error(y_val, val_preds)),
        "rmse": float(mean_squared_error(y_val, val_preds) ** 0.5),
        "r2": float(r2_score(y_val, val_preds))
    }
    print(f"\nHeld-Out Validation Set Metrics ({len(val_df)} records):")
    print(f"  MAE  : {val_metrics['mae']:.4f}")
    print(f"  RMSE : {val_metrics['rmse']:.4f}")
    print(f"  R²   : {val_metrics['r2']:.4f}")

# 6. Evaluate on Held-Out Test Set
test_metrics = {}
if test_df is not None:
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target_score"]
    test_preds = final_model.predict(X_test)
    test_metrics = {
        "mae": float(mean_absolute_error(y_test, test_preds)),
        "rmse": float(mean_squared_error(y_test, test_preds) ** 0.5),
        "r2": float(r2_score(y_test, test_preds))
    }
    print(f"\nHeld-Out Test Set Metrics ({len(test_df)} records):")
    print(f"  MAE  : {test_metrics['mae']:.4f}")
    print(f"  RMSE : {test_metrics['rmse']:.4f}")
    print(f"  R²   : {test_metrics['r2']:.4f}")

# 7. Feature Importances
print("\n----------------------------------------")
print("Feature Importances:")
print("----------------------------------------")
importances = dict(zip(FEATURE_COLUMNS, [float(v) for v in final_model.feature_importances_]))
for feat, imp in sorted(importances.items(), key=lambda x: x[1], reverse=True):
    bar = "█" * int(imp * 40)
    print(f"  {feat:20s}: {imp:6.4f}  {bar}")

# 8. Save Artifacts
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(final_model, MODEL_FILE)
print(f"\nSaved Model : {MODEL_FILE}")

metrics_data = {
    "model_type": "RandomForestRegressor",
    "n_estimators": 300,
    "max_depth": 8,
    "feature_columns": FEATURE_COLUMNS,
    "rubric_weights": {
        "concept_coverage": 0.30,
        "technical_depth": 0.25,
        "semantic_similarity": 0.25,
        "keyword_alignment": 0.20
    },
    "cross_validation_5_fold": {
        "mean_mae": round(mean_cv_mae, 4),
        "mean_rmse": round(mean_cv_rmse, 4),
        "mean_r2": round(mean_cv_r2, 4),
        "fold_maes": [round(m, 4) for m in cv_maes],
        "fold_r2s": [round(r, 4) for r in cv_r2s]
    },
    "train_metrics": {
        "mae": round(train_mae, 4),
        "rmse": round(train_rmse, 4),
        "r2": round(train_r2, 4)
    },
    "validation_metrics": {k: round(v, 4) for k, v in val_metrics.items()},
    "test_metrics": {k: round(v, 4) for k, v in test_metrics.items()},
    "feature_importances": {k: round(v, 4) for k, v in importances.items()}
}

with open(METRICS_FILE, "w", encoding="utf-8") as f:
    json.dump(metrics_data, f, indent=4)
print(f"Saved Metrics: {METRICS_FILE}")

print("\n========================================")
print("       MODEL TRAINING COMPLETE")
print("========================================")
