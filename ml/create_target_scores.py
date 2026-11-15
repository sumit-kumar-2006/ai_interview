import os
import sys
import pandas as pd
import numpy as np

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath("."))

from ml.rubric_utils import (
    compute_concept_coverage,
    compute_keyword_alignment,
    compute_technical_depth,
    compute_rubric_target_score
)

FEATURES_DIR = "ml/datasets/features"
TRAIN_INPUT = os.path.join(FEATURES_DIR, "train_features.csv")
TRAIN_OUTPUT = os.path.join(FEATURES_DIR, "train_scored.csv")
VAL_INPUT = os.path.join(FEATURES_DIR, "val_features.csv")
VAL_OUTPUT = os.path.join(FEATURES_DIR, "val_scored.csv")
TEST_INPUT = os.path.join(FEATURES_DIR, "test_features.csv")
TEST_OUTPUT = os.path.join(FEATURES_DIR, "test_scored.csv")

print("========================================")
print("   CREATING MULTI-CRITERIA TARGET SCORES")
print("========================================")
print("Rubric Dimensions:")
print("  1. Concept Coverage   : 30%")
print("  2. Technical Depth    : 25%")
print("  3. Semantic Similarity: 25%")
print("  4. Keyword Alignment  : 20%")
print("========================================")


def process_features_file(input_file: str, output_file: str, split_name: str) -> pd.DataFrame:
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}, skipping.")
        return None

    df = pd.read_csv(input_file)
    print(f"\nProcessing {split_name} ({len(df)} records)...")

    concept_coverages = []
    keyword_alignments = []
    technical_depths = []
    target_scores = []

    for _, row in df.iterrows():
        q = str(row.get("question", ""))
        a = str(row.get("answer", ""))
        sem_sim = float(row.get("semantic_similarity", 0.0))
        a_len = int(row.get("answer_length", len(a.strip())))

        cov = compute_concept_coverage(q, a)
        align = compute_keyword_alignment(q, a)
        depth = compute_technical_depth(a)
        target = compute_rubric_target_score(sem_sim, cov, align, depth, a_len)

        concept_coverages.append(cov)
        keyword_alignments.append(align)
        technical_depths.append(depth)
        target_scores.append(target)

    df["concept_coverage"] = concept_coverages
    df["keyword_alignment"] = keyword_alignments
    df["technical_depth"] = technical_depths
    df["target_score"] = target_scores

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")
    return df


train_df = process_features_file(TRAIN_INPUT, TRAIN_OUTPUT, "TRAIN")
val_df = process_features_file(VAL_INPUT, VAL_OUTPUT, "VAL")
test_df = process_features_file(TEST_INPUT, TEST_OUTPUT, "TEST")

if train_df is not None:
    print("\n========================================")
    print("       TRAIN SCORE STATISTICS")
    print("========================================")
    print(train_df[["concept_coverage", "keyword_alignment", "technical_depth", "target_score"]].describe().round(2))

    print("\nFirst 5 Scored Records:")
    print("----------------------------------------")
    for i in range(min(5, len(train_df))):
        row = train_df.iloc[i]
        print(f"Q: {row['question'][:65]}...")
        print(f"   Sem: {row['semantic_similarity']*100:.1f} | Cov: {row['concept_coverage']}% | Align: {row['keyword_alignment']}% | Depth: {row['technical_depth']}% -> Target: {row['target_score']}")

print("\n========================================")
print("   MULTI-CRITERIA SCORING COMPLETE")
print("========================================")
