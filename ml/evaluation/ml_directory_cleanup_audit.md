# ML Directory Cleanup Audit Report

**Project:** AI Interview Analyzer  
**Workspace:** `D:\AI-Interview-Analyzer`  
**Audit Date:** November 6, 2026  
**Status:** Read-Only Audit – No files modified, moved, or deleted  
**Total files in `ml/`:** 208 files | **Total size:** 94.30 MB  

---

## 1. Existing Directory Tree

```
ml/
├── __pycache__/                          # 21 compiled .pyc files (Aug 2026 — stale)
│   ├── check_hf_dataset.cpython-311.pyc
│   ├── check_qa_dataset.cpython-311.pyc
│   ├── check_videos.cpython-311.pyc
│   ├── convert_hf_dataset.cpython-311.pyc
│   ├── create_target_scores.cpython-311.pyc
│   ├── create_training_features.cpython-311.pyc
│   ├── evaluate_hf_qa.cpython-311.pyc
│   ├── evaluate_qa.cpython-311.pyc
│   ├── evaluate_scoring_model.cpython-311.pyc
│   ├── extract_audio.cpython-311.pyc
│   ├── extract_qa.cpython-311.pyc
│   ├── extract_text_features.cpython-311.pyc
│   ├── predict_hf_scores.cpython-311.pyc
│   ├── predict_score.cpython-311.pyc
│   ├── qa_analyzer.cpython-311.pyc
│   ├── qa_engine.cpython-311.pyc
│   ├── scoring.cpython-311.pyc
│   ├── semantic_similarity.cpython-311.pyc
│   ├── train_scoring_model.cpython-311.pyc
│   └── transcribe.cpython-311.pyc
│
├── clustering/                           # Part A Step 5 – K-Means Clustering
│   ├── plots/
│   │   ├── cluster_feature_heatmap.png   (184.8 KB)
│   │   ├── cluster_size_distribution.png (147.3 KB)
│   │   ├── elbow_curve.png               (191.3 KB)
│   │   ├── feature_distribution_by_cluster.png (425.6 KB)
│   │   ├── pca_cluster_visualization.png (584.0 KB)
│   │   ├── silhouette_analysis.png       (197.2 KB)
│   │   └── silhouette_comparison.png     (157.7 KB)
│   ├── cluster_assignments_test.csv      (59.9 KB)
│   ├── cluster_assignments_train.csv     (276.0 KB)
│   ├── cluster_assignments_val.csv       (58.5 KB)
│   ├── cluster_contingency.csv           (0.5 KB)
│   ├── cluster_metadata.json             (2.4 KB)
│   ├── cluster_profiles.csv              (1.3 KB)
│   ├── clustering_report.md              (35.8 KB)
│   ├── elbow_results.csv                 (0.3 KB)
│   ├── kmeans_analysis.py                (30.2 KB)
│   ├── kmeans_model.pkl                  (5.8 KB)
│   └── silhouette_results.csv            (0.1 KB)
│
├── datasets/
│   ├── audio/                            # 19 WAV audio files extracted from MP4
│   │   └── [19x *.wav files]             (8.87 MB total)
│   ├── features/                         # Legacy RF scoring model features
│   │   ├── test_features.csv             (55.9 KB)
│   │   ├── train_features.csv            (257.7 KB)
│   │   ├── train_scored.csv              (264.9 KB)
│   │   └── val_features.csv              (54.6 KB)
│   ├── processed/                        # Part A canonical train/val/test splits
│   │   ├── test_processed.csv            (72.3 KB)
│   │   ├── train_processed.csv           (334.7 KB)
│   │   └── val_processed.csv             (70.6 KB)
│   ├── qa/                               # QA source datasets
│   │   ├── hf_train.jsonl                (2244.4 KB) — original HuggingFace download
│   │   ├── hf_val.jsonl                  (239.5 KB)  — original HuggingFace download
│   │   ├── qa_pairs.json                 (1.7 KB)
│   │   ├── questions.json                (2.1 KB)    — curated_seed (10 records)
│   │   ├── test.jsonl                    (56.0 KB)
│   │   ├── train.jsonl                   (258.5 KB)
│   │   └── val.jsonl                     (54.7 KB)
│   ├── raw/
│   │   ├── .cache/
│   │   │   └── huggingface/
│   │   │       ├── .gitignore
│   │   │       ├── CACHEDIR.TAG
│   │   │       └── download/train/
│   │   │           └── [19x *.mp4.metadata files] (0.1 KB each)
│   │   └── train/
│   │       └── [19x *.mp4 video files]   (64.50 MB total)
│   ├── transcripts/                      # Whisper transcript text files
│   │   └── [19x *.txt files]             (< 0.5 KB each)
│   ├── README.md                         (0.4 KB)
│   ├── test_processed.csv                (72.3 KB) — DUPLICATE of processed/
│   ├── text_features.csv                 (5.3 KB)  — legacy early-phase feature file
│   ├── train_processed.csv               (334.7 KB) — DUPLICATE of processed/
│   └── val_processed.csv                 (70.6 KB)  — DUPLICATE of processed/
│
├── eda/                                  # Part A Step 3 – EDA
│   ├── plots/
│   │   ├── avg_word_length_distribution.png     (141.8 KB)
│   │   ├── feature_correlation_heatmap.png      (169.3 KB)
│   │   ├── feature_pairplot.png                 (1090.1 KB)
│   │   ├── feature_vs_target.png                (238.5 KB)
│   │   ├── lexical_overlap_distribution.png     (132.5 KB)
│   │   ├── semantic_similarity_distribution.png (133.8 KB)
│   │   ├── target_distribution.png              (89.6 KB)
│   │   ├── target_leakage_decision_boundary.png (524.5 KB)
│   │   ├── unique_word_ratio_distribution.png   (119.9 KB)
│   │   └── word_count_distribution.png          (135.6 KB)
│   ├── correlation_matrix.csv            (0.4 KB)
│   ├── eda_analysis.py                   (26.6 KB)
│   ├── eda_report.md                     (9.6 KB)
│   └── statistical_summary.csv          (0.6 KB)
│
├── evaluation/                           # Reports, metrics, and visualizations
│   ├── confusion_matrices/
│   │   ├── confusion_matrix_baseline_(dummy)_test.png   (72.6 KB)
│   │   ├── confusion_matrix_decision_tree_test.png      (71.5 KB)
│   │   ├── confusion_matrix_knn_classifier_test.png     (72.1 KB)
│   │   └── confusion_matrix_svm_classifier_test.png     (72.4 KB)
│   ├── precision_recall_curves/
│   │   ├── comparative_pr_test_experiment_a_(full_features).png   (169.1 KB)
│   │   ├── comparative_pr_test_experiment_b_(feature_ablation).png (232.0 KB)
│   │   ├── pr_curve_baseline_(dummy)_test.png           (108.0 KB)
│   │   ├── pr_curve_decision_tree_test.png              (73.7 KB)
│   │   ├── pr_curve_knn_classifier_test.png             (87.1 KB)
│   │   └── pr_curve_svm_classifier_test.png             (78.1 KB)
│   ├── roc_curves/
│   │   ├── comparative_roc_test_experiment_a_(full_features).png  (177.5 KB)
│   │   ├── comparative_roc_test_experiment_b_(feature_ablation).png (228.4 KB)
│   │   ├── roc_curve_baseline_(dummy)_test.png          (143.6 KB)
│   │   ├── roc_curve_decision_tree_test.png             (118.4 KB)
│   │   ├── roc_curve_knn_classifier_test.png            (126.1 KB)
│   │   └── roc_curve_svm_classifier_test.png            (120.9 KB)
│   ├── classification_reports.txt        (3.6 KB)
│   ├── model_comparison.csv              (0.9 KB)
│   ├── model_evaluation_report.md        (9.4 KB)
│   ├── part_a_final_audit_report.md      (26.3 KB)
│   ├── part_b_step1_application_audit.md (26.0 KB)
│   ├── part_b_step2_dataset_migration_report.md      (15.6 KB)
│   ├── part_b_step2_final_verification_audit.md      (15.5 KB)
│   ├── part_b_step3_secure_question_engine_report.md (12.4 KB)
│   ├── step4_integrity_audit.md          (7.0 KB)
│   ├── test_results.csv                  (0.8 KB)
│   ├── train_results.csv                 (0.8 KB)
│   ├── validation_results.csv            (0.8 KB)
│   └── vif_analysis.csv                  (0.3 KB)
│
├── features/                             — EMPTY DIRECTORY
├── models/                               # Trained model artifacts
│   ├── academic_scaler.pkl               (1.0 KB)
│   ├── decision_tree_model.pkl           (2.0 KB)
│   ├── interview_scoring_model.pkl       (9411.8 KB) — live backend model
│   ├── knn_model.pkl                     (127.1 KB)
│   ├── model_metadata.json               (4.4 KB)
│   └── svm_model.pkl                     (9.4 KB)
│
├── notebooks/                            — EMPTY DIRECTORY
├── preprocessing/                        — EMPTY DIRECTORY
├── saved_models/                         — EMPTY DIRECTORY
├── training/                             — EMPTY DIRECTORY
│
├── check_hf_dataset.py                   (1.5 KB)  — Phase 0: audit HF jsonl
├── check_qa_dataset.py                   (2.3 KB)  — Phase 0: audit QA jsonl
├── check_videos.py                       (0.7 KB)  — Phase 0: audit MP4 integrity
├── convert_hf_dataset.py                 — Phase 0: HF -> JSONL conversion
├── create_target_scores.py               — Phase 1: score computation
├── create_training_features.py           — Phase 1: feature engineering
├── evaluate_hf_qa.py                     — Phase 1: HF model evaluation
├── evaluate_qa.py                        — Phase 1: QA model evaluation
├── evaluate_scoring_model.py             — Phase 1: RF scoring evaluation
├── extract_audio.py                      (1.2 KB)  — Phase 0: MP4->WAV extraction
├── extract_qa.py                         (2.6 KB)  — Phase 0: transcript->QA pairs
├── extract_text_features.py             (2.6 KB)  — Phase 0: text feature extraction
├── predict_hf_scores.py                  (2.3 KB)  — Phase 1: HF score prediction
├── predict_score.py                      (3.2 KB)  — Phase 1: score prediction demo
├── prepare_academic_dataset.py           (16.9 KB) — Part A Step 2: preprocessing
├── preprocessing_summary.json            (7.5 KB)  — Part A Step 2 output
├── preprocessing_summary.md             (3.2 KB)  — Part A Step 2 output
├── qa_analyzer.py                        (1.4 KB)  — Phase 0: manual QA analysis
├── qa_engine.py                          (3.3 KB)  — Phase 0: manual QA engine
├── scoring.py                            (1.3 KB)  — Phase 0: scoring formula
├── semantic_similarity.py               (0.7 KB)  — Phase 0: similarity demo
├── train_academic_models.py              (33.7 KB) — Part A Step 4: ML training
└── train_scoring_model.py               (1.8 KB)  — Phase 1: RF model training
```

---

## 2. File Classification

### 2.1 Essential Files – DO NOT TOUCH

These files are actively used, produced final academic outputs, or serve as live application dependencies.

| File / Directory | Role | Dependency |
| :--- | :--- | :--- |
| `ml/prepare_academic_dataset.py` | Part A Step 2 – preprocessing pipeline | Referenced in audit reports |
| `ml/train_academic_models.py` | Part A Step 4 – KNN, SVM, Decision Tree training | Referenced in audit reports |
| `ml/preprocessing_summary.json` | Step 2 output – preprocessing metadata | Referenced by audit reports |
| `ml/preprocessing_summary.md` | Step 2 output – human-readable summary | Academic audit evidence |
| `ml/datasets/processed/train_processed.csv` | Canonical train split (1,264 records) | Used by `train_academic_models.py`, `eda_analysis.py`, `kmeans_analysis.py` |
| `ml/datasets/processed/val_processed.csv` | Canonical validation split (270 records) | Used by `train_academic_models.py`, `eda_analysis.py`, `kmeans_analysis.py` |
| `ml/datasets/processed/test_processed.csv` | Canonical test split (272 records) | Used by `train_academic_models.py`, `eda_analysis.py`, `kmeans_analysis.py` |
| `ml/datasets/features/train_features.csv` | Pre-computed sentence-transformer features | Required by `prepare_academic_dataset.py` |
| `ml/datasets/features/val_features.csv` | Pre-computed sentence-transformer features | Required by `prepare_academic_dataset.py` |
| `ml/datasets/features/test_features.csv` | Pre-computed sentence-transformer features | Required by `prepare_academic_dataset.py` |
| `ml/datasets/features/train_scored.csv` | Phase 1 scored training data for RF model | Used by `train_scoring_model.py` and `evaluate_scoring_model.py` |
| `ml/datasets/qa/train.jsonl` | QA source for feature generation | Used by `create_training_features.py`, `prepare_academic_dataset.py` |
| `ml/datasets/qa/val.jsonl` | QA source for feature generation | Used by `create_training_features.py`, `prepare_academic_dataset.py` |
| `ml/datasets/qa/test.jsonl` | QA source for feature generation | Used by `create_training_features.py`, `prepare_academic_dataset.py` |
| `ml/datasets/qa/questions.json` | Curated seed bank (10 records) | Used by `qa_analyzer.py`, `qa_engine.py`, `extract_qa.py` |
| `ml/datasets/qa/qa_pairs.json` | QA pairs extracted from transcripts | Produced by `extract_qa.py` |
| `ml/datasets/qa/hf_train.jsonl` | Original HuggingFace dataset (train) | Used by `check_hf_dataset.py`, `evaluate_hf_qa.py`, `predict_hf_scores.py` |
| `ml/datasets/qa/hf_val.jsonl` | Original HuggingFace dataset (val) | Used by `check_hf_dataset.py`, `evaluate_hf_qa.py`, `predict_hf_scores.py` |
| `ml/datasets/README.md` | Dataset directory documentation | Reference document |
| `ml/models/interview_scoring_model.pkl` | **Live production RF scoring model** | Loaded by `backend/app/main.py` at startup |
| `ml/models/academic_scaler.pkl` | StandardScaler fitted on train (Part A) | Loaded by `train_academic_models.py` |
| `ml/models/knn_model.pkl` | Part A tuned KNN classifier | Academic output |
| `ml/models/svm_model.pkl` | Part A tuned SVM classifier | Academic output |
| `ml/models/decision_tree_model.pkl` | Part A tuned Decision Tree | Academic output |
| `ml/models/model_metadata.json` | Hyperparameters and evaluation metrics | Academic audit evidence |
| `ml/eda/eda_analysis.py` | Part A Step 3 – EDA script | Audit-verified academic output |
| `ml/eda/eda_report.md` | Part A Step 3 – EDA report | Academic deliverable |
| `ml/eda/statistical_summary.csv` | Part A Step 3 – statistical outputs | Academic deliverable |
| `ml/eda/correlation_matrix.csv` | Part A Step 3 – correlation output | Academic deliverable |
| `ml/eda/plots/` (all 10 plots) | Part A Step 3 – EDA visualizations | Academic deliverable |
| `ml/clustering/kmeans_analysis.py` | Part A Step 5 – K-Means clustering script | Audit-verified academic output |
| `ml/clustering/kmeans_model.pkl` | Trained K-Means model | Academic output |
| `ml/clustering/clustering_report.md` | Part A Step 5 – clustering report | Academic deliverable |
| `ml/clustering/cluster_*.csv` (5 files) | Cluster assignment and analysis CSVs | Academic deliverable |
| `ml/clustering/cluster_metadata.json` | K-Means model configuration | Academic deliverable |
| `ml/clustering/elbow_results.csv` | Elbow method results | Academic deliverable |
| `ml/clustering/silhouette_results.csv` | Silhouette analysis results | Academic deliverable |
| `ml/clustering/plots/` (all 7 plots) | Part A Step 5 – clustering visualizations | Academic deliverable |
| `ml/evaluation/` (all 29 files) | Evaluation metrics, curves, and all Part A/B audit reports | Academic and project deliverables |

---

### 2.2 Duplicate Files – Exact MD5 Matches Confirmed

These three files in `ml/datasets/` are bit-for-bit identical to their counterparts in `ml/datasets/processed/`. They are created intentionally by `prepare_academic_dataset.py` as "convenience copies" (lines 253–256).

| Duplicate Location | Canonical Location | MD5 Match |
| :--- | :--- | :---: |
| `ml/datasets/train_processed.csv` | `ml/datasets/processed/train_processed.csv` | True |
| `ml/datasets/val_processed.csv` | `ml/datasets/processed/val_processed.csv` | True |
| `ml/datasets/test_processed.csv` | `ml/datasets/processed/test_processed.csv` | True |

**Root cause:** `prepare_academic_dataset.py` lines 253–256 deliberately save a secondary copy to `ml/datasets/` root, calling it a "convenience copy."  
**Risk of deleting root copies:** LOW — no active Part A or B scripts read from `ml/datasets/*.csv` root path. `train_academic_models.py`, `eda_analysis.py`, and `kmeans_analysis.py` all read from `ml/datasets/processed/`.

---

### 2.3 Empty Directories – No Content

These five directories exist but contain zero files:

| Empty Directory | Notes |
| :--- | :--- |
| `ml/features/` | Likely a planned but unused location; `datasets/features/` is used instead |
| `ml/notebooks/` | No Jupyter notebooks were created for this project |
| `ml/preprocessing/` | Planned directory; preprocessing output goes to `ml/datasets/processed/` |
| `ml/saved_models/` | Unused duplicate of `ml/models/` |
| `ml/training/` | Unused — training scripts sit at `ml/` root level |

---

### 2.4 Stale Compiled Python Cache

The `ml/__pycache__/` directory contains 21 `.pyc` compiled bytecode files, all timestamped **August 27, 2026**. These correspond to Phase 0/1 development-era scripts at the `ml/` root. None of the Phase A/B academic scripts (`prepare_academic_dataset.py`, `train_academic_models.py`, `eda_analysis.py`, `kmeans_analysis.py`) are in `__pycache__` as they were run as standalone scripts after the cache was last updated.

**Risk of deleting:** Zero — Python automatically regenerates `.pyc` files from their `.py` source when needed.

---

### 2.5 Phase 0/1 Development Scripts – Provenance Chain

These scripts at the `ml/` root predate the Part A/B academic work. They were part of the initial exploration and data pipeline development (August 2026). They are **not imported** by any backend, test, or Part A/B academic script. Each is a standalone runnable script.

| Script | Phase | Purpose | Last Used |
| :--- | :---: | :--- | :--- |
| `check_videos.py` | 0 | Validates MP4 video file integrity via OpenCV | Aug 2026 |
| `check_qa_dataset.py` | 0 | Audits `qa/train.jsonl`, `val.jsonl`, `test.jsonl` structure | Aug 2026 |
| `check_hf_dataset.py` | 0 | Audits HuggingFace `hf_train.jsonl` / `hf_val.jsonl` | Aug 2026 |
| `convert_hf_dataset.py` | 0 | Downloaded HuggingFace dataset to `hf_train.jsonl` / `hf_val.jsonl` | Aug 2026 |
| `extract_audio.py` | 0 | Extracted WAV audio from MP4 videos | Aug 2026 |
| `transcribe.py` | 0 | Whisper transcription of WAV files to `transcripts/*.txt` | Aug 2026 |
| `extract_qa.py` | 0 | Built `qa_pairs.json` from transcripts + questions | Aug 2026 |
| `extract_text_features.py` | 0 | Computed early text features to `datasets/text_features.csv` | Aug 2026 |
| `semantic_similarity.py` | 0 | One-off demo script for semantic similarity testing | Aug 2026 |
| `scoring.py` | 0 | Standalone scoring formula prototype | Aug 2026 |
| `qa_analyzer.py` | 0 | Manual QA similarity analysis demo | Aug 2026 |
| `qa_engine.py` | 0 | Early QA similarity engine prototype | Aug 2026 |
| `create_training_features.py` | 1 | Generated `datasets/features/*.csv` via SentenceTransformer | Aug 2026 |
| `create_target_scores.py` | 1 | Added `score` column to `train_scored.csv` | Aug 2026 |
| `train_scoring_model.py` | 1 | Trained initial RandomForest to `interview_scoring_model.pkl` | Aug 2026 |
| `evaluate_scoring_model.py` | 1 | Evaluated RF model on features CSVs | Aug 2026 |
| `predict_score.py` | 1 | Demo prediction using `interview_scoring_model.pkl` | Aug 2026 |
| `predict_hf_scores.py` | 1 | Demo prediction on HF validation data | Aug 2026 |
| `evaluate_qa.py` | 1 | Evaluated QA similarity on `qa/test.jsonl` | Aug 2026 |
| `evaluate_hf_qa.py` | 1 | Evaluated QA similarity on `hf_train.jsonl` / `hf_val.jsonl` | Aug 2026 |

> **Important:** These scripts are the full provenance chain. They document exactly how raw MP4 videos -> WAV audio -> transcripts -> QA pairs -> feature CSVs -> scored training data -> `interview_scoring_model.pkl` was built. The live production model `ml/models/interview_scoring_model.pkl` was produced by `train_scoring_model.py`. Deleting these would sever the reproducibility chain.

---

### 2.6 Raw Media Dataset – Large, Completed Provenance Role

| Directory | File Count | Total Size | Description |
| :--- | :---: | :---: | :--- |
| `ml/datasets/raw/train/` | 19 MP4 | 64.50 MB | Original downloaded HuggingFace interview videos |
| `ml/datasets/audio/` | 19 WAV | 8.87 MB | Extracted WAV audio (produced by `extract_audio.py`) |
| `ml/datasets/transcripts/` | 19 TXT | ~4 KB | Whisper transcriptions (produced by `transcribe.py`) |
| `ml/datasets/raw/.cache/` | 21 files | ~2 KB | HuggingFace download metadata files |

**Current active use:** `check_videos.py` and `extract_audio.py` reference the MP4 files. No Part A/B academic scripts use these directly — all Part A work reads from `datasets/processed/*.csv`.  
**Provenance:** These are the original source data for the entire project pipeline. Their provenance is documented in the Part A Final Audit Report.

---

### 2.7 Legacy Feature File

| File | Size | Produced by | Referenced by |
| :--- | :---: | :--- | :--- |
| `ml/datasets/text_features.csv` | 5.3 KB | `extract_text_features.py` (Aug 2026) | Only `extract_text_features.py` itself |

This is an early-phase text feature CSV produced from transcripts, predating the SentenceTransformer feature pipeline. It is **not** used by any Part A/B academic scripts or backend code.

---

## 3. Proposed Clean Structure

The proposed structure preserves all files but introduces clarity through reorganization. Files are grouped by their academic phase and function.

> **Important:** This is a proposed target state only. No files have been moved. Approval is required before any action is taken.

```
ml/
│
├── datasets/
│   ├── processed/                   # KEEP AS-IS — canonical Part A splits
│   │   ├── train_processed.csv
│   │   ├── val_processed.csv
│   │   └── test_processed.csv
│   ├── features/                    # KEEP AS-IS — SentenceTransformer features
│   │   ├── train_features.csv
│   │   ├── val_features.csv
│   │   ├── test_features.csv
│   │   └── train_scored.csv
│   ├── qa/                          # KEEP AS-IS — QA source datasets
│   │   ├── train.jsonl
│   │   ├── val.jsonl
│   │   ├── test.jsonl
│   │   ├── hf_train.jsonl
│   │   ├── hf_val.jsonl
│   │   ├── questions.json
│   │   └── qa_pairs.json
│   ├── raw/                         # KEEP AS-IS — original source provenance
│   │   ├── train/ [19x *.mp4]
│   │   └── .cache/ [HF metadata]
│   ├── audio/                       # KEEP AS-IS — extracted WAVs
│   │   └── [19x *.wav]
│   ├── transcripts/                 # KEEP AS-IS — Whisper transcripts
│   │   └── [19x *.txt]
│   └── README.md
│
├── models/                          # KEEP AS-IS — all trained model artifacts
│   ├── interview_scoring_model.pkl  # Live backend model — do not move
│   ├── academic_scaler.pkl
│   ├── knn_model.pkl
│   ├── svm_model.pkl
│   ├── decision_tree_model.pkl
│   └── model_metadata.json
│
├── eda/                             # KEEP AS-IS — Part A Step 3
│   ├── plots/ [10 PNG files]
│   ├── eda_analysis.py
│   ├── eda_report.md
│   ├── statistical_summary.csv
│   └── correlation_matrix.csv
│
├── clustering/                      # KEEP AS-IS — Part A Step 5
│   ├── plots/ [7 PNG files]
│   ├── kmeans_analysis.py
│   ├── kmeans_model.pkl
│   ├── clustering_report.md
│   ├── cluster_assignments_train.csv
│   ├── cluster_assignments_val.csv
│   ├── cluster_assignments_test.csv
│   ├── cluster_contingency.csv
│   ├── cluster_profiles.csv
│   ├── cluster_metadata.json
│   ├── elbow_results.csv
│   └── silhouette_results.csv
│
├── evaluation/                      # KEEP AS-IS — all reports and metrics
│   ├── confusion_matrices/ [4 PNGs]
│   ├── precision_recall_curves/ [6 PNGs]
│   ├── roc_curves/ [6 PNGs]
│   ├── [all existing .csv, .txt, .md reports]
│   └── ml_directory_cleanup_audit.md  <- this file
│
├── scripts/                         # PROPOSED — group all Phase 0/1 root scripts
│   ├── pipeline/                    # Data pipeline provenance scripts
│   │   ├── convert_hf_dataset.py
│   │   ├── extract_audio.py
│   │   ├── transcribe.py
│   │   ├── extract_qa.py
│   │   ├── extract_text_features.py
│   │   ├── create_training_features.py
│   │   ├── create_target_scores.py
│   │   └── train_scoring_model.py
│   ├── audit/                       # Data and model audit scripts
│   │   ├── check_videos.py
│   │   ├── check_qa_dataset.py
│   │   └── check_hf_dataset.py
│   └── analysis/                    # Exploration and analysis demos
│       ├── scoring.py
│       ├── semantic_similarity.py
│       ├── qa_analyzer.py
│       ├── qa_engine.py
│       ├── evaluate_qa.py
│       ├── evaluate_hf_qa.py
│       ├── evaluate_scoring_model.py
│       ├── predict_score.py
│       └── predict_hf_scores.py
│
├── prepare_academic_dataset.py      # KEEP AT ROOT — Part A Step 2
├── train_academic_models.py         # KEEP AT ROOT — Part A Step 4
├── preprocessing_summary.json       # KEEP AT ROOT — Part A Step 2 output
└── preprocessing_summary.md         # KEEP AT ROOT — Part A Step 2 output
```

---

## 4. Proposed Action Plan

### Action A – Safe to Delete (Zero Risk)

| Item | Rationale | Risk |
| :--- | :--- | :---: |
| `ml/__pycache__/` (entire directory, 21 `.pyc` files) | Auto-generated bytecode; Python regenerates these on demand. Last compiled August 2026. | None |

---

### Action B – Safe to Delete (Confirmed Exact Duplicates)

| File to Delete | Duplicate of | Risk |
| :--- | :--- | :---: |
| `ml/datasets/train_processed.csv` | `ml/datasets/processed/train_processed.csv` (MD5 match confirmed) | None — no script reads this root path |
| `ml/datasets/val_processed.csv` | `ml/datasets/processed/val_processed.csv` (MD5 match confirmed) | None |
| `ml/datasets/test_processed.csv` | `ml/datasets/processed/test_processed.csv` (MD5 match confirmed) | None |

> **Warning:** If this cleanup is approved, the `prepare_academic_dataset.py` script (lines 253–256) should also be updated to remove the "convenience copy" logic. Otherwise these duplicates will be recreated on the next preprocessing run.

---

### Action C – Safe to Remove (Empty Directories)

| Directory | Reason |
| :--- | :--- |
| `ml/features/` | Has never contained files; actual features are in `ml/datasets/features/` |
| `ml/notebooks/` | No notebooks were created for this project |
| `ml/preprocessing/` | Unused; actual preprocessing output is in `ml/datasets/processed/` |
| `ml/saved_models/` | Unused; models live in `ml/models/` |
| `ml/training/` | Unused; training scripts are at `ml/` root |

---

### Action D – Uncertain / Requires Explicit Decision

| Item | Issue | Recommendation |
| :--- | :--- | :--- |
| `ml/datasets/text_features.csv` | Only referenced by `extract_text_features.py` itself; not used by any Part A/B code | Mark as archivable; confirm before deleting |
| `ml/datasets/raw/train/` (19x MP4, 64.5 MB) | Pipeline complete; original source data | **Keep for provenance** unless storage is a constraint |
| `ml/datasets/audio/` (19x WAV, 8.87 MB) | Intermediate; re-extractable from MP4 using `extract_audio.py` | **Keep for now**; small deletion benefit |
| `ml/datasets/transcripts/` (19x TXT, ~4 KB) | Re-generatable from WAV using `transcribe.py` | **Keep** — negligible size |
| `ml/datasets/raw/.cache/` (21 metadata files, ~2 KB) | HuggingFace download artifacts; no functional use | Low priority; safe to delete |

---

### Action E – Structural Reorganization (Optional, Requires Path Review)

| Proposed Change | Benefit | Risk |
| :--- | :--- | :--- |
| Move 20 Phase 0/1 root scripts into `ml/scripts/` subdirectory | Removes clutter from `ml/` root | Medium — scripts use hardcoded relative paths like `"ml/datasets/..."` designed for execution from project root. Moving the files does not break execution as long as they are still run from `D:\AI-Interview-Analyzer`. Internal paths do not need updating. |
| Remove "convenience copy" code from `prepare_academic_dataset.py` | Prevents future duplicate creation | Low — simple two-line removal |

---

## 5. Dependency Risk Register

| File | Depended On By | Move Risk | Delete Risk |
| :--- | :--- | :---: | :---: |
| `ml/models/interview_scoring_model.pkl` | `backend/app/main.py` (startup load) | Critical | Critical |
| `ml/datasets/processed/*.csv` (3 files) | `train_academic_models.py`, `eda_analysis.py`, `kmeans_analysis.py` | High | High |
| `ml/datasets/features/*.csv` (4 files) | `prepare_academic_dataset.py`, `train_scoring_model.py`, `evaluate_scoring_model.py` | Medium | Medium |
| `ml/datasets/qa/*.jsonl` / `*.json` | Multiple Phase 0/1 scripts | Medium | Medium |
| `ml/models/academic_scaler.pkl` | `train_academic_models.py` | Medium | Medium |
| `ml/models/knn_model.pkl`, `svm_model.pkl`, `decision_tree_model.pkl` | Academic evaluation only | Low | Medium |
| `ml/preprocessing_summary.json` | Audit reports reference it | Medium | Medium |
| `ml/__pycache__/` | Nothing | None | None |
| `ml/datasets/train_processed.csv` (root copy) | Nothing active | None | None |
| Empty directories (5) | Nothing | None | None |
| `ml/datasets/text_features.csv` | `extract_text_features.py` only | Low | Low |

---

## 6. Summary of Findings

| Category | Count | Size |
| :--- | :---: | :--- |
| Essential files (must keep) | ~160 | ~93 MB |
| Exact duplicate CSVs (safe to delete) | 3 | 477.6 KB |
| Empty directories (safe to remove) | 5 | 0 B |
| Stale `__pycache__` bytecode (safe to delete) | 21 | ~56 KB |
| Legacy media pipeline (keep for provenance) | 60 files | ~73 MB |
| Uncertain items (need decision) | 2 | ~3.5 KB |

**Immediate recoverable space (Actions A + B + C):** ~534 KB  
**Potential additional space (Action D — delete raw/audio if provenance not required):** ~73 MB

> **Note:** The vast majority of `ml/` disk usage (~73 MB of 94.3 MB total) is raw media data: 19 MP4 videos (64.5 MB) and 19 WAV files (8.87 MB). All academic and application logic fits in approximately 21 MB.

---

## 7. Approval Checklist

Before any cleanup action is executed, please explicitly approve each item:

- [ ] **Action A:** Delete `ml/__pycache__/` (21 stale `.pyc` files, ~56 KB)
- [ ] **Action B:** Delete 3 duplicate CSVs from `ml/datasets/` root (477.6 KB) + suppress convenience copy in `prepare_academic_dataset.py`
- [ ] **Action C:** Delete 5 empty directories (`features/`, `notebooks/`, `preprocessing/`, `saved_models/`, `training/`)
- [ ] **Action D (optional):** Decision on `text_features.csv`, raw MP4s, WAV files, HF cache metadata
- [ ] **Action E (optional):** Reorganize Phase 0/1 root scripts into `ml/scripts/` subdirectory

---

*Audit performed by: AI Interview Analyzer – Antigravity Agent*  
*Report path: `ml/evaluation/ml_directory_cleanup_audit.md`*  
*Audit scope: Read-only inspection only. No files were modified, moved, renamed, or deleted.*

