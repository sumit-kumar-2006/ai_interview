import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

VAL_FILE = "ml/datasets/qa/test.jsonl"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# Load validation dataset
# -----------------------------

data = []

with open(VAL_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if line:
            data.append(json.loads(line))


print("Validation records:", len(data))


# -----------------------------
# Prepare questions and answers
# -----------------------------

questions = [item["question"] for item in data]
reference_answers = [item["answer"] for item in data]


print("Generating embeddings...")

question_embeddings = model.encode(
    questions,
    show_progress_bar=True
)

reference_embeddings = model.encode(
    reference_answers,
    show_progress_bar=True
)


# -----------------------------
# Calculate baseline similarity
# -----------------------------

scores = []

for i in range(len(data)):

    score = cosine_similarity(
        [question_embeddings[i]],
        [reference_embeddings[i]]
    )[0][0]

    scores.append(float(score))


scores = np.array(scores)


# -----------------------------
# Results
# -----------------------------

print("\n========================================")
print("       QA DATASET EVALUATION")
print("========================================")

print("Records evaluated:", len(scores))

print(
    "Average Question-Answer Similarity:",
    round(scores.mean() * 100, 2),
    "%"
)

print(
    "Minimum Similarity:",
    round(scores.min() * 100, 2),
    "%"
)

print(
    "Maximum Similarity:",
    round(scores.max() * 100, 2),
    "%"
)

print(
    "Median Similarity:",
    round(np.median(scores) * 100, 2),
    "%"
)

print("========================================")


# -----------------------------
# Show sample results
# -----------------------------

print("\nSAMPLE RESULTS")
print("----------------------------------------")

for i in range(min(10, len(data))):

    print("\nQuestion:")
    print(data[i]["question"])

    print(
        "Similarity:",
        round(scores[i] * 100, 2),
        "%"
    )