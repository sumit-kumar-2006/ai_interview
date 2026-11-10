import os
import glob
import re
import csv

TRANSCRIPT_DIR = "ml/datasets/transcripts"
OUTPUT_FILE = "ml/datasets/text_features.csv"

# Common filler words
FILLER_WORDS = [
    "um",
    "uh",
    "erm",
    "hmm",
    "like",
    "you know",
    "actually",
    "basically",
    "so"
]


def calculate_features(text):
    text = text.strip()

    words = re.findall(r"\b[a-zA-Z']+\b", text.lower())

    word_count = len(words)

    sentences = [
        s.strip()
        for s in re.split(r"[.!?]+", text)
        if s.strip()
    ]

    sentence_count = len(sentences)

    unique_words = set(words)

    unique_word_ratio = (
        len(unique_words) / word_count
        if word_count > 0
        else 0
    )

    avg_word_length = (
        sum(len(word) for word in words) / word_count
        if word_count > 0
        else 0
    )

    filler_count = 0

    for filler in FILLER_WORDS:
        if " " in filler:
            filler_count += len(
                re.findall(
                    r"\b" + re.escape(filler) + r"\b",
                    text.lower()
                )
            )
        else:
            filler_count += words.count(filler)

    filler_ratio = (
        filler_count / word_count
        if word_count > 0
        else 0
    )

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length, 3),
        "unique_word_ratio": round(unique_word_ratio, 3),
        "filler_count": filler_count,
        "filler_ratio": round(filler_ratio, 3),
    }


files = glob.glob(
    os.path.join(TRANSCRIPT_DIR, "*.txt")
)

print("Found transcripts:", len(files))

rows = []

for file in files:

    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    features = calculate_features(text)

    features["file"] = os.path.basename(file)
    features["transcript"] = text

    rows.append(features)

fieldnames = [
    "file",
    "word_count",
    "sentence_count",
    "avg_word_length",
    "unique_word_ratio",
    "filler_count",
    "filler_ratio",
    "transcript",
]

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)

print("\n==============================")
print("Feature extraction completed")
print("Records:", len(rows))
print("Output:", OUTPUT_FILE)
print("==============================")