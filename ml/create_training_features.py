import json
import os

import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


TRAIN_FILE = "ml/datasets/qa/train.jsonl"
VAL_FILE = "ml/datasets/qa/val.jsonl"
TEST_FILE = "ml/datasets/qa/test.jsonl"

OUTPUT_DIR = "ml/datasets/features"

MODEL_NAME = "all-MiniLM-L6-v2"


print("========================================")
print("   CREATING QA SEMANTIC FEATURES")
print("========================================")

print("\nLoading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")


def load_jsonl(path):

    with open(path, "r", encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f
            if line.strip()
        ]


def create_features(data, dataset_name):

    questions = [item["question"] for item in data]
    answers = [item["answer"] for item in data]

    print(f"\nGenerating embeddings for {dataset_name}...")
    print("Records:", len(data))

    question_embeddings = model.encode(
        questions,
        batch_size=32,
        show_progress_bar=True
    )

    answer_embeddings = model.encode(
        answers,
        batch_size=32,
        show_progress_bar=True
    )

    features = []

    for i in range(len(data)):

        question_embedding = question_embeddings[i]
        answer_embedding = answer_embeddings[i]

        similarity = cosine_similarity(
            [question_embedding],
            [answer_embedding]
        )[0][0]

        question_length = len(questions[i])
        answer_length = len(answers[i])

        features.append({
            "question": questions[i],
            "answer": answers[i],
            "semantic_similarity": float(similarity),
            "question_length": question_length,
            "answer_length": answer_length
        })

    return pd.DataFrame(features)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


train_data = load_jsonl(TRAIN_FILE)
val_data = load_jsonl(VAL_FILE)
test_data = load_jsonl(TEST_FILE)


train_df = create_features(
    train_data,
    "TRAIN"
)

val_df = create_features(
    val_data,
    "VALIDATION"
)

test_df = create_features(
    test_data,
    "TEST"
)


train_output = os.path.join(
    OUTPUT_DIR,
    "train_features.csv"
)

val_output = os.path.join(
    OUTPUT_DIR,
    "val_features.csv"
)

test_output = os.path.join(
    OUTPUT_DIR,
    "test_features.csv"
)


train_df.to_csv(
    train_output,
    index=False
)

val_df.to_csv(
    val_output,
    index=False
)

test_df.to_csv(
    test_output,
    index=False
)


print("\n========================================")
print("       FEATURE CREATION COMPLETE")
print("========================================")

print("TRAIN:", len(train_df))
print("VALIDATION:", len(val_df))
print("TEST:", len(test_df))

print("\nFiles created:")

print(train_output)
print(val_output)
print(test_output)

print("========================================")