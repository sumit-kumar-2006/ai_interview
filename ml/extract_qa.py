import json
import os
import re

QUESTION_FILE = "ml/datasets/qa/questions.json"
TRANSCRIPT_DIR = "ml/datasets/transcripts"
OUTPUT_FILE = "ml/datasets/qa/qa_pairs.json"


# Load questions
with open(QUESTION_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)


def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_question(transcript):
    """
    Find the closest known interview question
    inside the transcript.
    """

    transcript_lower = transcript.lower()

    best_question = None
    best_score = 0

    for q in questions:

        question_text = q["question"].lower()

        # Simple keyword matching
        words = [
            w for w in re.findall(r"\b[a-zA-Z]+\b", question_text)
            if len(w) > 3
        ]

        if not words:
            continue

        matched = sum(
            1 for word in words
            if word in transcript_lower
        )

        score = matched / len(words)

        if score > best_score:
            best_score = score
            best_question = q

    return best_question, best_score


results = []

files = [
    f for f in os.listdir(TRANSCRIPT_DIR)
    if f.endswith(".txt")
]

print("Found transcripts:", len(files))

for filename in files:

    path = os.path.join(
        TRANSCRIPT_DIR,
        filename
    )

    with open(path, "r", encoding="utf-8") as f:
        transcript = clean_text(f.read())

    question, match_score = find_question(transcript)

    if question is None:
        print("No question matched:", filename)
        continue

    result = {
        "video": filename,
        "question_id": question["id"],
        "question": question["question"],
        "reference_answer": question["reference_answer"],
        "candidate_answer": transcript,
        "question_match": round(match_score, 4)
    }

    results.append(result)

    print("\n==============================")
    print("Video:", filename)
    print("Question:", question["question"])
    print("Match:", round(match_score * 100, 2), "%")
    print("==============================")


os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\n==============================")
print("Q&A extraction completed")
print("Records:", len(results))
print("Output:", OUTPUT_FILE)
print("==============================")