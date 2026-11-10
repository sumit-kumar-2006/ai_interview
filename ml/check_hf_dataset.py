import json
from pathlib import Path
from collections import Counter


DATASET_DIR = Path("ml/datasets/qa")


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


for filename in ["hf_train.jsonl", "hf_val.jsonl"]:

    path = DATASET_DIR / filename
    data = load_jsonl(path)

    questions = [x["question"].strip() for x in data]
    answers = [x["answer"].strip() for x in data]

    print("\n========================================")
    print(filename)
    print("========================================")

    print("Records:", len(data))
    print("Unique questions:", len(set(questions)))
    print("Unique answers:", len(set(answers)))

    print("Missing questions:", sum(not x for x in questions))
    print("Missing answers:", sum(not x for x in answers))

    print(
        "Average question length:",
        round(sum(len(x) for x in questions) / len(questions), 2)
    )

    print(
        "Average answer length:",
        round(sum(len(x) for x in answers) / len(answers), 2)
    )

    duplicate_questions = [
        q for q, count in Counter(questions).items()
        if count > 1
    ]

    print("Duplicate questions:", len(duplicate_questions))

    print("\nFirst question:")
    print(questions[0])

    print("\nFirst answer:")
    print(answers[0])

print("\n========================================")
print("HF DATASET CHECK COMPLETED")
print("========================================")