import json
import os

DATASETS = {
    "train": "ml/datasets/qa/train.jsonl",
    "validation": "ml/datasets/qa/val.jsonl",
    "test": "ml/datasets/qa/test.jsonl"
}


def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):

            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
                records.append(data)

            except json.JSONDecodeError as e:
                print(
                    f"Invalid JSON: {path} "
                    f"line {line_number}: {e}"
                )

    return records


print("\n========================================")
print("       QA DATASET INSPECTION")
print("========================================")

all_data = {}

for name, path in DATASETS.items():

    if not os.path.exists(path):
        print(f"\n{name}: FILE NOT FOUND")
        continue

    records = load_jsonl(path)

    all_data[name] = records

    print(f"\n{name.upper()}")
    print("-" * 40)
    print("Records:", len(records))

    if records:

        print("Fields:", list(records[0].keys()))

        print("\nFirst question:")
        print(records[0].get("question"))

        print("\nFirst answer:")
        print(records[0].get("answer"))


print("\n========================================")
print("       DATA QUALITY CHECK")
print("========================================")

for name, records in all_data.items():

    missing_question = 0
    missing_answer = 0
    empty_question = 0
    empty_answer = 0

    for record in records:

        question = record.get("question")
        answer = record.get("answer")

        if "question" not in record:
            missing_question += 1

        if "answer" not in record:
            missing_answer += 1

        if not question or not str(question).strip():
            empty_question += 1

        if not answer or not str(answer).strip():
            empty_answer += 1

    print(f"\n{name.upper()}")

    print("Missing question:", missing_question)
    print("Missing answer:", missing_answer)
    print("Empty question:", empty_question)
    print("Empty answer:", empty_answer)


print("\n========================================")
print("Inspection completed")
print("========================================")