import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


MODEL_FILE = "ml/models/interview_scoring_model.pkl"

TRAIN_FILE = "ml/datasets/features/train_scored.csv"
VAL_FILE = "ml/datasets/features/val_features.csv"
TEST_FILE = "ml/datasets/features/test_features.csv"


FEATURE_COLUMNS = [
    "semantic_similarity",
    "question_length",
    "answer_length"
]


def create_target(df):

    semantic_score = (
        df["semantic_similarity"]
        .clip(0, 1)
        * 100
    )

    length_score = (
        df["answer_length"] / 80
    ).clip(0, 1) * 100

    target = (
        semantic_score * 0.85
        + length_score * 0.15
    )

    return target.clip(0, 100)


print("========================================")
print("       SCORING MODEL EVALUATION")
print("========================================")


# Load model
print("\nLoading trained model...")

model = joblib.load(MODEL_FILE)

print("Model loaded.")


# Load datasets
train_df = pd.read_csv(TRAIN_FILE)
val_df = pd.read_csv(VAL_FILE)
test_df = pd.read_csv(TEST_FILE)


# Create targets for validation and test
val_df["target_score"] = create_target(val_df)
test_df["target_score"] = create_target(test_df)


def evaluate(df, dataset_name):

    X = df[FEATURE_COLUMNS]
    y = df["target_score"]

    predictions = model.predict(X)

    predictions = predictions.clip(0, 100)

    mae = mean_absolute_error(
        y,
        predictions
    )

    rmse = mean_squared_error(
        y,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y,
        predictions
    )

    print("\n========================================")
    print(dataset_name)
    print("========================================")

    print("Records:", len(df))
    print("MAE :", round(mae, 4))
    print("RMSE:", round(rmse, 4))
    print("R²  :", round(r2, 4))

    return predictions


train_predictions = evaluate(
    train_df,
    "TRAIN"
)

val_predictions = evaluate(
    val_df,
    "VALIDATION"
)

test_predictions = evaluate(
    test_df,
    "TEST"
)


print("\n========================================")
print("       SAMPLE TEST PREDICTIONS")
print("========================================")

for i in range(min(10, len(test_df))):

    print("\nQuestion:")
    print(test_df.iloc[i]["question"])

    print(
        "Target Score:",
        round(test_df.iloc[i]["target_score"], 2)
    )

    print(
        "Predicted Score:",
        round(test_predictions[i], 2)
    )


print("\n========================================")
print("       EVALUATION COMPLETE")
print("========================================")