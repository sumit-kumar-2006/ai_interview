from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


question = """
What is polymorphism in object oriented programming?
"""


answer = """
Polymorphism allows the same interface or method
to behave differently depending on the object.
"""


question_embedding = model.encode([question])
answer_embedding = model.encode([answer])


score = cosine_similarity(
    question_embedding,
    answer_embedding
)[0][0]


print("==============================")
print("Question:", question.strip())
print("Answer:", answer.strip())
print("Semantic Similarity:", round(float(score), 4))
print("==============================")