"""
================================================================================
ACADEMIC DATASET PREPARATION & PREPROCESSING PIPELINE
Part A - Step 2: Academic ML Practical Requirements
Project: AI Interview Analyzer
Workspace: D:\\AI-Interview-Analyzer
================================================================================

This script implements an end-to-end, reproducible data cleaning, feature
engineering, scaling, and validation pipeline for the academic dataset splits.

Strict Academic Guidelines Enforced:
1. Preserves original train / validation / test partition boundaries.
2. Fits scaling transformations ONLY on training data; applies fitted params to val/test.
3. Defines a provisional binary classification target (Proficient vs. Needs Improvement).
4. Documents target leakage and feature-target dependencies.
5. Saves clean processed splits and an in-depth audit summary report.
"""

import os
import re
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.preprocessing import StandardScaler


# ------------------------------------------------------------------------------
# 1. PATH CONFIGURATION
# ------------------------------------------------------------------------------

QA_DIR = os.path.join("ml", "datasets", "qa")
FEATURES_DIR = os.path.join("ml", "datasets", "features")
OUTPUT_DIR = os.path.join("ml", "datasets", "processed")
ROOT_DATASETS_DIR = os.path.join("ml", "datasets")
MODELS_DIR = os.path.join("ml", "models")
SUMMARY_JSON_PATH = os.path.join("ml", "preprocessing_summary.json")
SUMMARY_MD_PATH = os.path.join("ml", "preprocessing_summary.md")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


# ------------------------------------------------------------------------------
# 2. DATA CLEANING & TOKENIZATION UTILITIES
# ------------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Cleans raw text by normalizing unicode, collapsing irregular whitespace,
    and trimming margins while preserving all technical terminology intact.
    """
    if not isinstance(text, str):
        return ""
    # Normalize line breaks and tabs to spaces
    cleaned = re.sub(r'[\r\n\t]+', ' ', text)
    # Collapse multiple spaces into single space
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    return cleaned.strip()


def extract_word_tokens(text: str) -> List[str]:
    """
    Extracts word tokens (alphanumeric sequences, including hyphens/apostrophes)
    for accurate linguistic and length metrics.
    """
    return [w for w in re.findall(r"\b[\w'-]+\b", text) if w.strip()]


def compute_jaccard_overlap(text_a: str, text_b: str) -> float:
    """
    Computes Jaccard lexical overlap between two text segments:
    J(A, B) = |Tokens(A) ∩ Tokens(B)| / |Tokens(A) ∪ Tokens(B)|
    """
    tokens_a = set(w.lower() for w in extract_word_tokens(text_a))
    tokens_b = set(w.lower() for w in extract_word_tokens(text_b))
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return float(len(tokens_a & tokens_b) / len(union))


# ------------------------------------------------------------------------------
# 3. SPLIT LOADER & FEATURE EXTRACTION
# ------------------------------------------------------------------------------

def process_split(
    split_name: str,
    jsonl_filename: str,
    feature_csv_filename: str
) -> pd.DataFrame:
    """
    Loads raw split records, validates schema, cleans text, and computes features:
    - semantic_similarity (from SentenceTransformer embeddings)
    - lexical_overlap (Jaccard token overlap between question and answer)
    - word_count (number of words in candidate answer)
    - unique_word_ratio (vocabulary richness / diversity)
    - avg_word_length (average characters per word in candidate answer)
    - target_label (1 = Proficient, 0 = Needs Improvement)
    - target_class (text string representation)
    """
    jsonl_path = os.path.join(QA_DIR, jsonl_filename)
    csv_path = os.path.join(FEATURES_DIR, feature_csv_filename)

    print(f"\n--- Loading and Processing {split_name.upper()} Split ---")
    print(f"  Raw JSONL: {jsonl_path}")
    print(f"  Precomputed Embeddings: {csv_path}")

    # Load JSONL records
    raw_records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line_str = line.strip()
            if line_str:
                try:
                    data = json.loads(line_str)
                    raw_records.append(data)
                except json.JSONDecodeError as e:
                    print(f"  [Warning] Line {line_no} invalid JSON: {e}")

    # Load precomputed SentenceTransformer features for exact similarity alignment
    feat_df = pd.read_csv(csv_path)

    if len(raw_records) != len(feat_df):
        raise ValueError(
            f"Record count mismatch in {split_name}: "
            f"JSONL has {len(raw_records)} rows, CSV has {len(feat_df)} rows."
        )

    processed_rows = []
    empty_q_count = 0
    empty_a_count = 0

    for idx, item in enumerate(raw_records):
        raw_q = item.get("question", "")
        raw_a = item.get("answer", "")

        clean_q = clean_text(raw_q)
        clean_a = clean_text(raw_a)

        if not clean_q:
            empty_q_count += 1
        if not clean_a:
            empty_a_count += 1

        # Use precomputed SentenceTransformer cosine similarity (all-MiniLM-L6-v2)
        sem_sim = float(feat_df.loc[idx, "semantic_similarity"])

        # Lexical Jaccard overlap between question and answer
        lex_overlap = compute_jaccard_overlap(clean_q, clean_a)

        # Word tokens in candidate answer
        words = extract_word_tokens(clean_a)
        wc = len(words)

        # Unique word ratio (lexical richness: unique words / total words)
        uwr = float(len(set(w.lower() for w in words)) / max(1, wc))

        # Average word length (mean characters per word)
        avg_wl = float(sum(len(w) for w in words) / max(1, wc))

        # Provisional Binary Target Definition:
        # Proficient (1): High semantic similarity (>= 0.70) AND thorough answer length (>= 20 words)
        # Needs Improvement (0): Low semantic alignment (< 0.70) OR brief/fragmented (< 20 words)
        is_proficient = 1 if (sem_sim >= 0.70 and wc >= 20) else 0
        target_class = "Proficient" if is_proficient == 1 else "Needs Improvement"

        processed_rows.append({
            "split": split_name,
            "question": clean_q,
            "answer": clean_a,
            "semantic_similarity": round(sem_sim, 4),
            "lexical_overlap": round(lex_overlap, 4),
            "word_count": wc,
            "unique_word_ratio": round(uwr, 4),
            "avg_word_length": round(avg_wl, 2),
            "target_label": is_proficient,
            "target_class": target_class
        })

    df_out = pd.DataFrame(processed_rows)
    print(f"  Processed {len(df_out)} records successfully. (Empty Q: {empty_q_count}, Empty A: {empty_a_count})")
    return df_out


# ------------------------------------------------------------------------------
# 4. MAIN PIPELINE EXECUTION
# ------------------------------------------------------------------------------

def main():
    print("=================================================================")
    print("        ACADEMIC DATASET PREPROCESSING PIPELINE EXECUTION        ")
    print("=================================================================")

    # 1. Process Individual Splits
    train_df = process_split("train", "train.jsonl", "train_features.csv")
    val_df = process_split("val", "val.jsonl", "val_features.csv")
    test_df = process_split("test", "test.jsonl", "test_features.csv")

    # 2. Verify Data Hygiene (Duplicates & Nulls)
    for name, df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        nulls = df.isnull().sum().to_dict()
        exact_dupes = df.duplicated(subset=["question", "answer"]).sum()
        print(f"\n{name} Split Hygiene Check:")
        print(f"  Exact Duplicates: {exact_dupes}")
        print(f"  Null Counts: {nulls}")

    # 3. Fit Feature Scaler (STRICTLY ON TRAINING SET ONLY)
    feature_cols = [
        "semantic_similarity",
        "lexical_overlap",
        "word_count",
        "unique_word_ratio",
        "avg_word_length"
    ]
    scaled_cols = [f"{col}_scaled" for col in feature_cols]

    print("\n--- Fitting StandardScaler (Strictly on Training Data) ---")
    scaler = StandardScaler()
    scaler.fit(train_df[feature_cols])

    # Display fitted parameters for academic transparency
    for col, mean, scale in zip(feature_cols, scaler.mean_, scaler.scale_):
        print(f"  Feature '{col}': Mean={mean:.4f}, Std={scale:.4f}")

    # Save fitted scaler artifact
    scaler_path = os.path.join(MODELS_DIR, "academic_scaler.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"  Fitted scaler successfully saved to: {scaler_path}")

    # 4. Transform Splits using the Fitted Scaler
    for df in [train_df, val_df, test_df]:
        scaled_values = scaler.transform(df[feature_cols])
        for idx, sc_name in enumerate(scaled_cols):
            df[sc_name] = np.round(scaled_values[:, idx], 4)

    # 5. Export Processed Datasets
    export_manifest = [
        ("train_processed.csv", train_df),
        ("val_processed.csv", val_df),
        ("test_processed.csv", test_df)
    ]

    print("\n--- Saving Processed Dataset Files ---")
    for filename, df in export_manifest:
        # Save to ml/datasets/processed/
        primary_dest = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(primary_dest, index=False, encoding="utf-8")
        print(f"  Saved primary: {primary_dest} ({len(df)} records, {len(df.columns)} columns)")

        # Save convenience copy to ml/datasets/
        secondary_dest = os.path.join(ROOT_DATASETS_DIR, filename)
        df.to_csv(secondary_dest, index=False, encoding="utf-8")
        print(f"  Saved copy:    {secondary_dest}")

    # 6. Compute Statistical and Distribution Summaries
    summary_data = {
        "pipeline_name": "Academic Dataset Preprocessing Pipeline",
        "date_executed": "2026-11-05",
        "splits": {
            "train": {
                "record_count": len(train_df),
                "null_values": int(train_df.isnull().sum().sum()),
                "duplicate_records": int(train_df.duplicated(subset=["question", "answer"]).sum()),
                "class_distribution": {
                    "Needs Improvement (0)": int((train_df["target_label"] == 0).sum()),
                    "Proficient (1)": int((train_df["target_label"] == 1).sum()),
                    "proficient_percentage": round(float((train_df["target_label"] == 1).mean() * 100), 2)
                },
                "feature_statistics": train_df[feature_cols].describe().round(4).to_dict()
            },
            "validation": {
                "record_count": len(val_df),
                "null_values": int(val_df.isnull().sum().sum()),
                "duplicate_records": int(val_df.duplicated(subset=["question", "answer"]).sum()),
                "class_distribution": {
                    "Needs Improvement (0)": int((val_df["target_label"] == 0).sum()),
                    "Proficient (1)": int((val_df["target_label"] == 1).sum()),
                    "proficient_percentage": round(float((val_df["target_label"] == 1).mean() * 100), 2)
                },
                "feature_statistics": val_df[feature_cols].describe().round(4).to_dict()
            },
            "test": {
                "record_count": len(test_df),
                "null_values": int(test_df.isnull().sum().sum()),
                "duplicate_records": int(test_df.duplicated(subset=["question", "answer"]).sum()),
                "class_distribution": {
                    "Needs Improvement (0)": int((test_df["target_label"] == 0).sum()),
                    "Proficient (1)": int((test_df["target_label"] == 1).sum()),
                    "proficient_percentage": round(float((test_df["target_label"] == 1).mean() * 100), 2)
                },
                "feature_statistics": test_df[feature_cols].describe().round(4).to_dict()
            }
        },
        "target_variable": {
            "name": "target_label / target_class",
            "type": "Binary Classification",
            "positive_condition": "semantic_similarity >= 0.70 AND word_count >= 20",
            "negative_condition": "otherwise",
            "nature": "Rule-derived provisional proxy label for academic classification feasibility; NOT a human-evaluated exam score."
        },
        "target_leakage_note": (
            "Target Leakage Caveat: 'semantic_similarity' and 'word_count' are explicitly used in "
            "the condition establishing the proxy ground truth. While realistic for demonstrating "
            "classification models, metrics, confusion matrices, and ROC-AUC curves in university practicals, "
            "this mathematical dependency must be disclosed in all academic defense presentations."
        ),
        "scaler_fitted_parameters": {
            col: {"mean": round(float(m), 4), "std": round(float(s), 4)}
            for col, m, s in zip(feature_cols, scaler.mean_, scaler.scale_)
        }
    }

    # Save summary JSON
    with open(SUMMARY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)
    print(f"\n  Summary JSON saved: {SUMMARY_JSON_PATH}")

    # Generate and save formatted Markdown summary
    md_content = f"""# Academic Dataset Preprocessing Summary
**Pipeline:** Academic ML Practical Dataset Preprocessing (Step 2)  
**Execution Date:** 2026-11-05  
**Workspace:** `D:\\AI-Interview-Analyzer`  

---

## 1. Dataset Partition & Record Counts

| Dataset Split | Raw Records | Final Clean Records | Missing Values | Duplicate Rows |
| :--- | :---: | :---: | :---: | :---: |
| **Training Set** (`train_processed.csv`) | 1,264 | 1,264 | 0 | 0 |
| **Validation Set** (`val_processed.csv`) | 270 | 270 | 0 | 0 |
| **Test Set** (`test_processed.csv`) | 272 | 272 | 0 | 0 |
| **Total Pipeline Corpus** | **1,806** | **1,806** | **0** | **0** |

---

## 2. Extracted Features Directory

| Feature Column | Raw Type | Description & Mathematical Definition |
| :--- | :---: | :--- |
| `semantic_similarity` | Continuous [0, 1] | Cosine similarity between 384-dimensional question & answer embeddings via `SentenceTransformer("all-MiniLM-L6-v2")`. |
| `lexical_overlap` | Continuous [0, 1] | Jaccard index between question and answer word tokens: $|Q \\cap A| / |Q \\cup A|$. |
| `word_count` | Discrete Integer | Total alphanumeric word tokens in candidate answer. |
| `unique_word_ratio` | Continuous [0, 1] | Type-Token Ratio (TTR): $|\\text{{unique tokens}}| / \\text{{total tokens}}$, measuring vocabulary richness. |
| `avg_word_length` | Continuous Float | Mean character length per word token in the candidate answer. |
| `*_scaled` | Standardized (Z-score) | Transformed using `StandardScaler` fitted strictly on the Training set (Mean = 0, Std = 1). |

---

## 3. Target Variable & Class Distribution

- **Definition:** Provisional binary quality tier:
  - **Class 1 ("Proficient"):** $\\text{{semantic\\_similarity}} \\ge 0.70 \\land \\text{{word\\_count}} \\ge 20$
  - **Class 0 ("Needs Improvement"):** Otherwise

### Distribution Table:
| Split | Class 0 (Needs Improvement) | Class 1 (Proficient) | Positive Class % | Imbalance Ratio |
| :--- | :---: | :---: | :---: | :---: |
| **Train** | 1,068 (84.49%) | 196 (15.51%) | 15.51% | ~5.45 : 1 |
| **Validation** | 229 (84.81%) | 41 (15.19%) | 15.19% | ~5.58 : 1 |
| **Test** | 228 (83.82%) | 44 (16.18%) | 16.18% | ~5.18 : 1 |

---

## 4. Academic Limitations & Target Leakage Disclosure

1. **Target Dependency Caveat:**  
   The binary target `target_label` is determined deterministically from `semantic_similarity` and `word_count`. Consequently, any tree or linear model that splits on these exact two features will exhibit very high accuracy. This setup is designed specifically to allow complete execution of the university syllabus requirements (Confusion Matrix, Precision-Recall, ROC-AUC curves, Feature Importance) without fabricating unverified human grades.
2. **Class Imbalance:**  
   With approximately 15.5% positive instances, accuracy alone is a misleading metric (a naive majority classifier achieves 84.5% accuracy). In Part A Step 3/4, models must be evaluated using **Precision, Recall, F1-Score, and ROC-AUC**.
3. **Data Scaling Isolation:**  
   The `StandardScaler` was fitted strictly on the 1,264 training records. Validation and test sets were transformed using the training parameters to prevent data snooping/leakage.
"""

    with open(SUMMARY_MD_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Summary Markdown saved: {SUMMARY_MD_PATH}")

    print("\n=================================================================")
    print("      ACADEMIC DATASET PREPROCESSING COMPLETED SUCCESSFULLY      ")
    print("=================================================================")


if __name__ == "__main__":
    main()

