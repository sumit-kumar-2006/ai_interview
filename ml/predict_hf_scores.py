import json
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_FILE = "ml/models/interview_scoring_model.pkl"
HF_VAL_FILE = "ml/datasets/qa/hf_val.jsonl"


print("Loading scoring model...")
model = joblib.load(MODEL_FILE)

print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


with open(HF_VAL_FILE, "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f if line.strip()]


questions = [x["question"] for x in data]
answers = [x["answer"] for x in data]


print("Calculating semantic similarity...")

question_embeddings = embedding_model.encode(
    questions,
    show_progress_bar=True
)

answer_embeddings = embedding_model.encode(
    answers,
    show_progress_bar=True
)


from sklearn.metrics.pairwise import cosine_similarity

similarities = np.diag(
    cosine_similarity(
        question_embeddings,
        answer_embeddings
    )
)


features = np.column_stack([
    similarities,
    [len(q) for q in questions],
    [len(a) for a in answers]
])


predictions = model.predict(features)


print("\n========================================")
print("       HF ANSWER SCORE PREDICTION")
print("========================================")

print("Records:", len(predictions))

print(
    "Average Predicted Score:",
    round(float(np.mean(predictions)), 2),
    "%"
)

print(
    "Minimum Predicted Score:",
    round(float(np.min(predictions)), 2),
    "%"
)

print(
    "Maximum Predicted Score:",
    round(float(np.max(predictions)), 2),
    "%"
)

print(
    "Median Predicted Score:",
    round(float(np.median(predictions)), 2),
    "%"
)


print("\n========================================")
print("SAMPLE PREDICTIONS")
print("========================================")


for i in range(min(10, len(data))):

    print("\nQuestion:")
    print(questions[i])

    print(
        "Semantic Similarity:",
        round(float(similarities[i]), 4)
    )

    print(
        "Predicted Score:",
        round(float(predictions[i]), 2),
        "%"
    )


print("\n========================================")
print("HF SCORE PREDICTION COMPLETE")
print("========================================")