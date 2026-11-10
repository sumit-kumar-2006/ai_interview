import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


TRAIN_FILE = "ml/datasets/features/train_scored.csv"
MODEL_DIR = "ml/models"
MODEL_FILE = os.path.join(
    MODEL_DIR,
    "interview_scoring_model.pkl"
)


print("========================================")
print("       TRAINING INTERVIEW MODEL")
print("========================================")


# Load training data
df = pd.read_csv(TRAIN_FILE)

print("Training records:", len(df))


# Features
FEATURE_COLUMNS = [
    "semantic_similarity",
    "question_length",
    "answer_length"
]

X = df[FEATURE_COLUMNS]
y = df["target_score"]


# Create model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    max_depth=10,
    min_samples_leaf=2,
    n_jobs=-1
)


print("\nTraining model...")

model.fit(X, y)


# Predictions on training data
predictions = model.predict(X)


# Metrics
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


# Save model
os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_FILE
)


print("\n========================================")
print("       MODEL TRAINING COMPLETE")
print("========================================")

print("Model:", MODEL_FILE)

print("\nTraining Metrics")
print("----------------------------------------")
print("MAE :", round(mae, 4))
print("RMSE:", round(rmse, 4))
print("R²  :", round(r2, 4))

print("\nFeatures used:")
for feature in FEATURE_COLUMNS:
    print("-", feature)

print("========================================")