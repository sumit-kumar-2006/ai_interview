import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


TRAIN_FILE = "ml/datasets/qa/hf_train.jsonl"
VAL_FILE = "ml/datasets/qa/hf_val.jsonl"


print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate(path, name):
    data = load_jsonl(path)

    questions = [x["question"] for x in data]
    answers = [x["answer"] for x in data]

    print("\n========================================")
    print(name)
    print("========================================")
    print("Records:", len(data))
    print("Generating embeddings...")

    q_embeddings = model.encode(
        questions,
        show_progress_bar=True
    )

    a_embeddings = model.encode(
        answers,
        show_progress_bar=True
    )

    similarities = cosine_similarity(
        q_embeddings,
        a_embeddings
    )

    scores = np.diag(similarities)

    print("\nAverage Similarity:",
          round(float(np.mean(scores) * 100), 2), "%")

    print("Minimum Similarity:",
          round(float(np.min(scores) * 100), 2), "%")

    print("Maximum Similarity:",
          round(float(np.max(scores) * 100), 2), "%")

    print("Median Similarity:",
          round(float(np.median(scores) * 100), 2), "%")


evaluate(TRAIN_FILE, "HF TRAIN")
evaluate(VAL_FILE, "HF VALIDATION")


print("\n========================================")
print("HF DATASET EVALUATION COMPLETE")
print("========================================")