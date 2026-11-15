# AI INTERVIEW ANALYZER — ML MODEL VALIDATION & CORRECTION REPORT
**Project Name:** AI Interview Analyzer  
**Workspace:** `D:\AI-Interview-Analyzer`  
**Review Date:** 2026-11-15  
**Review Scope:** Classification Models, Random Forest Regressor, Semantic Similarity Bounds, K-Means Clustering & Multimodal Architecture  
**Status:** Validated, Reconciled & Documented  

---

## 1. Executive Summary

This report delivers a thorough mathematical and architectural audit of all machine learning models implemented in the **AI Interview Analyzer** platform. It addresses and resolves prior documentation ambiguities regarding target leakage, regression target interpretation, similarity metric boundaries, clustering parameters, and multimodal system boundaries.

---

## 2. Academic Classification & Target Leakage Resolution (Phase 3)

### 2.1. Diagnosis of Target Leakage
In the academic curriculum component (`ml/prepare_academic_dataset.py`), the classification label was defined using a deterministic rule:
$$\text{Class 1 (Proficient)} = (\text{semantic\_similarity} \ge 0.70) \land (\text{word\_count} \ge 20)$$
$$\text{Class 0 (Needs Improvement)} = \text{Otherwise}$$

When `semantic_similarity` and `word_count` were included as input features in **Experiment A**, the Decision Tree achieved **100% accuracy, precision, and recall** on the held-out test set by isolating this rectangular partition. While serving as an effective educational demonstration of rule extraction, it represents **target leakage** if treated as human-evaluated ground truth.

### 2.2. Experiment A vs. Experiment B (Ablation Analysis)
To provide complete academic transparency, two experiments were formally evaluated on the held-out test set ($N=272$):
- **Experiment A (Proxy Rule Learning):** Full 5 features (`semantic_similarity`, `lexical_overlap`, `word_count`, `unique_word_ratio`, `avg_word_length`).
- **Experiment B (Ablated Non-Leakage Features):** Removes the two defining features (`semantic_similarity` and `word_count`), training strictly on:
  1. `lexical_overlap` (Jaccard token intersection)
  2. `unique_word_ratio` (Type-Token Ratio / vocabulary richness)
  3. `avg_word_length` (Mean characters per token / technical density)

### 2.3. Test Set Performance Comparison ($N=272$, 41 Positive, 231 Negative)

| Experiment | Model | Accuracy | Precision | Recall | Macro F1 | Weighted F1 | ROC-AUC | PR-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | Dummy Majority Classifier | 0.8493 | 0.0000 | 0.0000 | 0.4592 | 0.7800 | 0.5000 | 0.1507 |
| **Exp A (Proxy)** | KNN ($k=5$) | 0.9596 | 0.8750 | 0.8537 | 0.9202 | 0.9594 | 0.9906 | 0.9341 |
| **Exp A (Proxy)** | SVM (RBF, $C=10.0$) | 0.9706 | 1.0000 | 0.8049 | 0.9374 | 0.9692 | 0.9984 | 0.9907 |
| **Exp A (Proxy)** | Decision Tree ($depth=5$) | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **Exp B (Ablated)**| KNN ($k=5$) | 0.8309 | 0.3333 | 0.1220 | 0.5422 | 0.7961 | 0.6603 | 0.2310 |
| **Exp B (Ablated)**| SVM (RBF, $C=10.0$) | 0.6471 | 0.2477 | 0.6585 | 0.5582 | 0.6966 | 0.6989 | 0.2790 |
| **Exp B (Ablated)**| Decision Tree ($depth=5$) | **0.8603** | **0.5484** | **0.4146** | **0.6959** | **0.8521** | **0.7330** | **0.4420** |

### 2.4. Key Findings from Classification Evaluation
1. In Experiment A, Decision Tree achieves 1.0000 because it literally discovers the axis-aligned boundary $[\ge 0.70, \ge 20]$.
2. In Experiment B, when `semantic_similarity` and `word_count` are removed, Decision Tree achieves a realistic **Macro F1 of 0.6959**, ROC-AUC of **0.7330**, and PR-AUC of **0.4420** (substantially outperforming the 0.1507 no-skill baseline).
3. This proves that linguistic features (lexical overlap, vocabulary richness, and average word length) carry genuine predictive signal even in the absence of semantic embeddings.

---

## 3. Random Forest Regression Validation (Phase 4)

### 3.1. Model Architecture & Hyperparameters
- **Algorithm:** `sklearn.ensemble.RandomForestRegressor`
- **Model File:** `ml/models/interview_scoring_model.pkl` (Metadata: `ml/models/scoring_model_metrics.json`)
- **Number of Estimators:** 350 Decision Trees
- **Maximum Depth:** 10
- **Random State:** 42
- **Training Samples:** 2,651 multi-source Q&A pairs

### 3.2. Continuous Target Variable Interpretation
The continuous target score $[0, 100]$ in the training set is generated via the multi-criteria institutional rubric formula:
$$\text{Target Score} = 0.30 \times \text{Concept Coverage} + 0.25 \times \text{Technical Depth} + 0.25 \times \text{Semantic Similarity} + 0.20 \times \text{Keyword Alignment}$$

Adversarial answers (< 3 words, off-topic statements, evasions) receive an automatic zero-floor penalty. The Random Forest model therefore acts as a **fast, non-linear function approximator** of this composite institutional grading rubric.

### 3.3. Empirical Performance Metrics
Evaluated on the independent, held-out test split ($N=272$):
- **Mean Absolute Error (MAE):** 0.4798 points (on a 0–100 scale)
- **Root Mean Squared Error (RMSE):** 0.6596 points
- **Coefficient of Determination ($R^2$):** 0.9985
- **5-Fold Cross-Validation Metrics:**
  - Fold MAEs: `[0.4828, 0.4558, 0.4532, 0.4963, 0.4718]` $\rightarrow$ **Mean MAE = 0.472**
  - Fold $R^2$s: `[0.9976, 0.9990, 0.9984, 0.9940, 0.9990]` $\rightarrow$ **Mean $R^2$ = 0.9976**
  - Mean RMSE: 0.9436

### 3.4. Feature Importance Breakdown

| Feature Name | Importance Weight | Percentage | Explanation |
| :--- | :---: | :---: | :--- |
| `semantic_similarity` | 0.4187 | **41.87%** | Dominant driver reflecting conceptual relevance to expected answer |
| `keyword_alignment` | 0.2843 | **28.43%** | Alignment between question domain terms and candidate response |
| `concept_coverage` | 0.2529 | **25.29%** | Percentage of essential technical entities articulated |
| `answer_length` | 0.0400 | **4.00%** | Length calibration preventing overly brief answers |
| `technical_depth` | 0.0040 | **0.40%** | Vocabulary sophistication and technical keyword density |
| `question_length` | 0.0002 | **0.02%** | Minimal weight as expected (question context invariant) |

---

## 4. Semantic Similarity Range & Metric Boundaries (Phase 5)

### 4.1. Mathematical Definition
The semantic similarity between question embedding $\mathbf{u}$ and candidate answer embedding $\mathbf{v}$ generated by `SentenceTransformer("all-MiniLM-L6-v2")` is calculated using Cosine Similarity:
$$\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$

### 4.2. Range Clarification: $[-1.0, 1.0]$ vs. $[0.0, 1.0]$
1. **Mathematical Reality:** Unconstrained cosine similarity between two unit vectors in $\mathbb{R}^{384}$ mathematically spans $[-1.0, 1.0]$.
2. **Empirical Verification:** In the training dataset (`ml/datasets/features/train_scored.csv`):
   - Minimum Value: **$-0.004260$** (rounded to $-0.0043$ in `train_processed.csv`)
   - Maximum Value: **$0.933595$**
   - Mean Value: **$0.635210$**
3. **Resolution:** Early documentation informally stated that similarity was in $[0, 1]$. In production inference (`backend/app/evaluator.py`), cosine similarity is safely clamped:
   $$\text{similarity}_{\text{clamped}} = \max(0.0, \min(1.0, \text{raw\_similarity}))$$
   This resolves the discrepancy without altering the underlying mathematics.

---

## 5. Unsupervised K-Means Clustering Validation (Phase 6)

### 5.1. Model Configuration
- **Algorithm:** K-Means (`sklearn.cluster.KMeans`)
- **Evaluated Range:** $k \in [2, 10]$
- **Convergence:** 12 iterations (`inertia = 3831.56`)
- **Optimal $k$:** $k=3$ (selected via Elbow heuristic and Silhouette maximum)
- **Silhouette Peak:** **0.2311** at $k=3$ (verified via `ml/clustering/silhouette_results.csv`)

### 5.2. Silhouette Analysis Curve ($k=2 \dots 10$)

| $k$ Value | Silhouette Score | Status |
| :---: | :---: | :--- |
| $k=2$ | 0.2167 | Sub-optimal separation |
| $\mathbf{k=3}$ | **0.2311** | **Global Silhouette Peak (Optimal)** |
| $k=4$ | 0.1895 | Dropping cohesion |
| $k=5$ | 0.1890 | Fragmented clusters |
| $k=6$ | 0.1786 | High within-cluster variance |
| $k=7$ | 0.1831 | Local plateau |
| $k=8$ | 0.1766 | Oversplit clusters |
| $k=9$ | 0.1721 | Overfitting |
| $k=10$| 0.1739 | Unstable clusters |

### 5.3. Cluster Centroids & Profiles ($N=1,264$ Training Samples)

| Cluster ID & Label | Sample Count | Semantic Sim | Lexical Overlap | Word Count | Unique Word Ratio | Avg Word Length |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cluster 0: Substantive** | 323 (25.6%) | 0.7173 | 0.1442 | 20.04 | 0.8681 | 5.52 |
| **Cluster 1: Divergent** | 325 (25.7%) | 0.4483 | 0.0391 | 15.35 | 0.9562 | 6.12 |
| **Cluster 2: Concise Tech** | 616 (48.7%) | 0.7171 | 0.1229 | 17.19 | 0.9700 | 6.83 |

### 5.4. Principal Component Analysis (PCA) Variance
To visualize the 5-dimensional standardized feature space in 2 dimensions, PCA was performed strictly on the standardized training data:
- **Principal Component 1 (PC1):** Explains **39.08%** of total variance.
- **Principal Component 2 (PC2):** Explains **26.83%** of total variance.
- **Total 2D Explained Variance:** **65.91%**

---

## 6. Multimodal Architecture Verification (Phase 7)

A crucial architectural principle enforced in this project is **strict modality decoupling**:

```
                       ┌──────────────────────────────┐
                       │     CANDIDATE INTERVIEW      │
                       └──────────────┬───────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
     [ Audio Stream ]        [ Video Frames ]         [ Text Transcript ]
              │                       │                       │
     ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
     │ Faster-Whisper │      │ MediaPipe Face │      │ Sentence-      │
     │ STT Engine     │      │ Mesh (478 pts) │      │ Transformer    │
     └────────┬───────┘      └────────┬───────┘      └────────┬───────┘
              │                       │                       │
      WPM & Fillers           Head Pose & Gaze         6 Text Features
              │                       │                       │
              │                       │              ┌────────┴───────┐
              │                       │              │ Random Forest  │
              │                       │              │ Regressor (RF) │
              │                       │              └────────┬───────┘
              │                       │                       │
              ▼                       ▼                       ▼
      [Speech Metrics]        [Vision Metrics]        [Technical Score]
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │   FastAPI Gateway Summary    │
                       │   Interactive PDF Report     │
                       └──────────────────────────────┘
```

### Decoupled Subsystem Responsibilities:
1. **Random Forest Model (Text Only):** Takes strictly 6 tabular text features derived from candidate answer text and reference question text. It does **not** ingest raw audio waveforms or raw video frames.
2. **Faster-Whisper (Audio Only):** Validates audio containers, transcribes speech to text, and computes speech pacing (Words Per Minute) and filler word occurrences.
3. **MediaPipe (Vision Only):** Tracks facial landmarks, head pose angles, and eye contact percentages to measure visual engagement.
4. **FastAPI Application Gateway:** Synthesizes the three independent assessment pillars into the final interactive report and PDF export.

---

## 7. Conclusion
All mathematical models, metrics, boundaries, and architectural boundaries in the AI Interview Analyzer system are verified, cross-checked against disk artifacts, and transparently documented.
