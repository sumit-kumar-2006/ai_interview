import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


QUESTION_FILE = "ml/datasets/qa/questions.json"


print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

with open(QUESTION_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)


question = questions[0]

candidate_answer = """
Polymorphism means that the same method or interface
can behave differently for different objects.
"""


reference_answer = question["reference_answer"]


question_embedding = model.encode([question["question"]])
answer_embedding = model.encode([candidate_answer])
reference_embedding = model.encode([reference_answer])


question_similarity = cosine_similarity(
    question_embedding,
    answer_embedding
)[0][0]


reference_similarity = cosine_similarity(
    reference_embedding,
    answer_embedding
)[0][0]


print("\n==============================")
print("QUESTION")
print(question["question"])

print("\nCANDIDATE ANSWER")
print(candidate_answer.strip())

print("\nREFERENCE ANSWER")
print(reference_answer)

print("\n==============================")
print(
    "Question Relevance:",
    round(float(question_similarity), 4)
)

print(
    "Reference Similarity:",
    round(float(reference_similarity), 4)
)

print("==============================")