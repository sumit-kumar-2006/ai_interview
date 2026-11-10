import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_FILE = "ml/models/interview_scoring_model.pkl"


print("========================================")
print("       INTERVIEW SCORE PREDICTION")
print("========================================")


# Load scoring model
print("\nLoading scoring model...")
model = joblib.load(MODEL_FILE)
print("Scoring model loaded.")


# Load embedding model
print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model loaded.")


# ----------------------------------------
# Test question
# ----------------------------------------

question = "What is polymorphism in object oriented programming?"


# ----------------------------------------
# Candidate answer
# ----------------------------------------

candidate_answer = """
Polymorphism means the same method or interface
can behave differently for different objects.
"""


# ----------------------------------------
# Reference answer
# ----------------------------------------

reference_answer = """
Polymorphism allows the same interface or method
to behave differently for different objects.
"""


# ----------------------------------------
# Calculate semantic similarity
# ----------------------------------------

print("\nCalculating semantic similarity...")

reference_embedding = embedding_model.encode(
    [reference_answer]
)

candidate_embedding = embedding_model.encode(
    [candidate_answer]
)

semantic_similarity = cosine_similarity(
    reference_embedding,
    candidate_embedding
)[0][0]


# ----------------------------------------
# Calculate text features
# ----------------------------------------

question_length = len(question)

answer_length = len(candidate_answer.strip())


# ----------------------------------------
# Prepare features with correct names
# ----------------------------------------

features = np.array([[
    semantic_similarity,
    question_length,
    answer_length
]])


# ----------------------------------------
# Predict score
# ----------------------------------------

predicted_score = model.predict(features)[0]

predicted_score = max(
    0,
    min(100, predicted_score)
)


# ----------------------------------------
# Display result
# ----------------------------------------

print("\n========================================")
print("QUESTION")
print(question)

print("\nCANDIDATE ANSWER")
print(candidate_answer.strip())

print("\nREFERENCE ANSWER")
print(reference_answer.strip())

print("\n========================================")
print("FEATURES")
print("----------------------------------------")

print(
    "Semantic Similarity:",
    round(float(semantic_similarity), 4)
)

print(
    "Question Length:",
    question_length
)

print(
    "Answer Length:",
    answer_length
)

print("\n========================================")
print(
    "Predicted Interview Answer Score:",
    round(float(predicted_score), 2),
    "%"
)
print("========================================")