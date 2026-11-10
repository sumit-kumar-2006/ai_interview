import os
import pandas as pd
import numpy as np


INPUT_FILE = "ml/datasets/features/train_features.csv"
OUTPUT_FILE = "ml/datasets/features/train_scored.csv"


print("========================================")
print("       CREATING TARGET SCORES")
print("========================================")


# Load feature dataset
df = pd.read_csv(INPUT_FILE)

print("Records:", len(df))


# -------------------------------------------------
# Semantic similarity score
# -------------------------------------------------

semantic_score = (
    df["semantic_similarity"]
    .clip(0, 1)
    * 100
)


# -------------------------------------------------
# Answer length score
# -------------------------------------------------
#
# Very short answers should receive less confidence.
# We use 80 characters as a reasonable minimum.
#

length_score = (
    df["answer_length"] / 80
).clip(0, 1) * 100


# -------------------------------------------------
# Final target score
# -------------------------------------------------
#
# Semantic quality is the main signal.
# Answer length provides a smaller contribution.
#

df["target_score"] = (
    semantic_score * 0.85
    + length_score * 0.15
)


# Keep score between 0 and 100

df["target_score"] = (
    df["target_score"]
    .clip(0, 100)
    .round(2)
)


# Save

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n========================================")
print("       TARGET SCORE CREATED")
print("========================================")

print("Records:", len(df))
print("Output:", OUTPUT_FILE)

print("\nTarget Score Statistics")
print("----------------------------------------")

print(
    df["target_score"].describe()
)

print("\nFirst 5 scores")
print("----------------------------------------")

print(
    df[
        [
            "question",
            "semantic_similarity",
            "answer_length",
            "target_score"
        ]
    ].head()
)

print("========================================")