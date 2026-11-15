import os
import sys
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

sys.path.insert(0, os.path.abspath("."))

MODEL_FILE = "ml/models/interview_scoring_model.pkl"
FEATURES_DIR = "ml/datasets/features"
TRAIN_FILE = os.path.join(FEATURES_DIR, "train_scored.csv")
VAL_FILE = os.path.join(FEATURES_DIR, "val_scored.csv")
TEST_FILE = os.path.join(FEATURES_DIR, "test_scored.csv")

FEATURE_COLUMNS = [
    "semantic_similarity",
    "question_length",
    "answer_length",
    "concept_coverage",
    "keyword_alignment",
    "technical_depth"
]

print("========================================")
print("   MULTI-CRITERIA SCORING EVALUATION")
print("========================================")

print("\nLoading trained model...")
model = joblib.load(MODEL_FILE)
print("Model loaded successfully.")

train_df = pd.read_csv(TRAIN_FILE)
val_df = pd.read_csv(VAL_FILE)
test_df = pd.read_csv(TEST_FILE)


def evaluate(df, dataset_name):
    X = df[FEATURE_COLUMNS]
    y = df["target_score"]

    predictions = model.predict(X).clip(0, 100)

    mae = mean_absolute_error(y, predictions)
    rmse = mean_squared_error(y, predictions) ** 0.5
    r2 = r2_score(y, predictions)

    print("\n========================================")
    print(f"  DATASET: {dataset_name} ({len(df)} records)")
    print("========================================")
    print(f"  MAE  : {mae:.4f}")
    print(f"  RMSE : {rmse:.4f}")
    print(f"  R²   : {r2:.4f}")
    return predictions


train_predictions = evaluate(train_df, "TRAIN")
val_predictions = evaluate(val_df, "VALIDATION")
test_predictions = evaluate(test_df, "TEST")

print("\n========================================")
print("       SAMPLE TEST PREDICTIONS")
print("========================================")
for i in range(min(5, len(test_df))):
    row = test_df.iloc[i]
    print(f"\nQuestion #{i+1}: {row['question'][:70]}...")
    print(f"  Metrics  : Sem={row['semantic_similarity']*100:.1f} | Cov={row['concept_coverage']}% | Align={row['keyword_alignment']}% | Depth={row['technical_depth']}%")
    print(f"  Target   : {row['target_score']:.2f}")
    print(f"  Predicted: {test_predictions[i]:.2f}")

print("\n========================================")
print("       EVALUATION COMPLETE")
print("========================================")
