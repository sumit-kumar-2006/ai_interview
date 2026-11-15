import os
import sys
import joblib
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.abspath("."))

from ml.rubric_utils import (
    compute_concept_coverage,
    compute_keyword_alignment,
    compute_technical_depth,
    compute_rubric_target_score
)

MODEL_FILE = "ml/models/interview_scoring_model.pkl"

print("========================================")
print("  MULTI-CRITERIA SCORE PREDICTION")
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
# Test sample
# ----------------------------------------
question = "What is polymorphism in object oriented programming?"
candidate_answer = """
Polymorphism allows the same method or interface to behave differently for different objects.
It enables dynamic method dispatch and subclass method overriding at runtime.
"""
reference_answer = """
Polymorphism allows the same interface or method to behave differently for different objects.
It enables dynamic dispatch and code reusability through inheritance and interfaces.
"""

# Calculate semantic similarity
reference_embedding = embedding_model.encode([reference_answer])
candidate_embedding = embedding_model.encode([candidate_answer])
semantic_similarity = float(cosine_similarity(reference_embedding, candidate_embedding)[0][0])

# Calculate multi-criteria rubric features
cov = compute_concept_coverage(question, candidate_answer)
align = compute_keyword_alignment(question, candidate_answer)
depth = compute_technical_depth(candidate_answer)
q_len = len(question)
a_len = len(candidate_answer.strip())

features_df = pd.DataFrame([{
    "semantic_similarity": max(0.0, min(1.0, semantic_similarity)),
    "question_length": q_len,
    "answer_length": a_len,
    "concept_coverage": cov,
    "keyword_alignment": align,
    "technical_depth": depth
}])

predicted_score = float(np.clip(model.predict(features_df)[0], 0, 100))
rule_target = compute_rubric_target_score(semantic_similarity, cov, align, depth, a_len)

print("\n========================================")
print("QUESTION:")
print(question)
print("\nCANDIDATE ANSWER:")
print(candidate_answer.strip())
print("\nREFERENCE ANSWER:")
print(reference_answer.strip())

print("\n========================================")
print("MULTI-CRITERIA RUBRIC BREAKDOWN:")
print("----------------------------------------")
print(f"  Concept Coverage    : {cov:.2f}% (Weight: 30%)")
print(f"  Technical Depth     : {depth:.2f}% (Weight: 25%)")
print(f"  Semantic Similarity : {semantic_similarity*100:.2f}% (Weight: 25%)")
print(f"  Keyword Alignment   : {align:.2f}% (Weight: 20%)")
print(f"  Question Length     : {q_len} chars")
print(f"  Answer Length       : {a_len} chars")

print("\n========================================")
print(f"  Predicted ML Model Score: {predicted_score:.2f}%")
print(f"  Rubric Formula Baseline : {rule_target:.2f}%")
print("========================================")
