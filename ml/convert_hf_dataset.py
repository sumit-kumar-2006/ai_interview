import json
from datasets import load_dataset


DATASET_NAME = "shimogerald/interview-coach-dataset"
OUTPUT_DIR = "ml/datasets/qa"


def convert_split(dataset, output_file):
    records = []

    for item in dataset:
        messages = item["messages"]

        question = None
        answer = None

        for message in messages:
            if message["role"] == "user":
                question = message["content"]

            elif message["role"] == "assistant":
                answer = message["content"]

        if question and answer:
            records.append({
                "question": question.strip(),
                "answer": answer.strip()
            })

    with open(output_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    print(f"{output_file}: {len(records)} records")


print("Loading Hugging Face dataset...")

dataset = load_dataset(DATASET_NAME)

convert_split(
    dataset["train"],
    f"{OUTPUT_DIR}/hf_train.jsonl"
)

convert_split(
    dataset["validation"],
    f"{OUTPUT_DIR}/hf_val.jsonl"
)

print("\nConversion completed.")