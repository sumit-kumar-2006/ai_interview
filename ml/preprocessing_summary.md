# Academic Dataset Preprocessing Summary
**Pipeline:** Academic ML Practical Dataset Preprocessing (Step 2)  
**Execution Date:** 2026-11-05  
**Workspace:** `D:\AI-Interview-Analyzer`  

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
| `lexical_overlap` | Continuous [0, 1] | Jaccard index between question and answer word tokens: $|Q \cap A| / |Q \cup A|$. |
| `word_count` | Discrete Integer | Total alphanumeric word tokens in candidate answer. |
| `unique_word_ratio` | Continuous [0, 1] | Type-Token Ratio (TTR): $|\text{unique tokens}| / \text{total tokens}$, measuring vocabulary richness. |
| `avg_word_length` | Continuous Float | Mean character length per word token in the candidate answer. |
| `*_scaled` | Standardized (Z-score) | Transformed using `StandardScaler` fitted strictly on the Training set (Mean = 0, Std = 1). |

---

## 3. Target Variable & Class Distribution

- **Definition:** Provisional binary quality tier:
  - **Class 1 ("Proficient"):** $\text{semantic\_similarity} \ge 0.70 \land \text{word\_count} \ge 20$
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
