import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


QUESTION_FILE = "ml/datasets/qa/questions.json"


print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

with open(QUESTION_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)


def similarity(text1, text2):
    embeddings = model.encode([text1, text2])

    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return float(score)


def calculate_score(question, candidate_answer):

    reference_answer = question["reference_answer"]

    question_relevance = similarity(
        question["question"],
        candidate_answer
    )

    reference_similarity = similarity(
        reference_answer,
        candidate_answer
    )

    final_score = (
        question_relevance * 0.40 +
        reference_similarity * 0.60
    ) * 100

    return {
        "question_relevance": round(question_relevance * 100, 2),
        "reference_similarity": round(reference_similarity * 100, 2),
        "final_score": round(final_score, 2)
    }


# Temporary test answers
candidate_answers = {
    1: "Polymorphism means the same method or interface can behave differently for different objects.",
    2: "Inheritance allows one class to acquire properties and methods from another class.",
    3: "Encapsulation means bundling data and methods together and controlling access to the data.",
    4: "Abstraction hides implementation details and shows only the important functionality.",
    5: "A primary key uniquely identifies every record in a database table.",
    6: "Normalization reduces data redundancy and improves data consistency.",
    7: "An API allows different software applications to communicate with each other.",
    8: "A REST API follows REST principles and uses HTTP methods to work with resources.",
    9: "Machine learning allows computers to learn patterns from data and make predictions.",
    10: "Overfitting happens when a model performs very well on training data but poorly on unseen data."
}


results = []

print("\n========================================")
print("       AI INTERVIEW Q&A ANALYSIS")
print("========================================")


for question in questions:

    question_id = question["id"]

    candidate_answer = candidate_answers.get(
        question_id,
        ""
    )

    if not candidate_answer:
        continue

    result = calculate_score(
        question,
        candidate_answer
    )

    results.append(result)

    print("\nQuestion", question_id)
    print(question["question"])

    print(
        "Question Relevance:",
        result["question_relevance"],
        "%"
    )

    print(
        "Reference Similarity:",
        result["reference_similarity"],
        "%"
    )

    print(
        "Final Score:",
        result["final_score"],
        "%"
    )


if results:

    overall_score = sum(
        r["final_score"] for r in results
    ) / len(results)

    print("\n========================================")
    print(
        "Overall Interview Score:",
        round(overall_score, 2),
        "%"
    )
    print("========================================")