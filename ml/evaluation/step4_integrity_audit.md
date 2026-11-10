# Step 4 Final Data Integrity & Audit Verification Report

**Module:** Machine Learning Data Integrity Audit (Post-Step 4 Verification)  
**Project:** AI Interview Analyzer  
**Workspace:** `D:\AI-Interview-Analyzer`  
**Execution Date:** 2026-11-05  
**Audit Status:** Complete — Read-Only Verification — Zero Datasets/Models Overwritten  

---

## 1. Actual Test Class Distribution vs. Previous Reports

The primary test dataset file `ml/datasets/processed/test_processed.csv` was verified in memory:

### Actual Test Support Ground Truth:
- **Total Test Records:** **272**
- **Actual Class 0 ("Needs Improvement"):** **231** ($84.93\%$)
- **Actual Class 1 ("Proficient"):** **41** ($15.07\%$)
- **Cross-Verification:** $231 + 41 = 272$ ($100.0\%$)

### Cross-Report Audit Reconciliation:

| Document / Asset | Stated Class 0 Count | Stated Class 1 Count | Total | Verification Status |
| :--- | :---: | :---: | :---: | :--- |
| **`test_processed.csv` (Actual Data File)** | **231** ($84.93\%$) | **41** ($15.07\%$) | 272 | **Ground Truth** |
| **`ml/preprocessing_summary.json` (Machine JSON)** | **231** ($84.93\%$) | **41** ($15.07\%$) | 272 | **100% Match with Ground Truth** |
| **Step 4 `test_results.csv`** | **231** | **41** | 272 | **100% Match with Ground Truth** |
| **Step 4 `model_evaluation_report.md`** | **231** | **41** | 272 | **100% Match with Ground Truth** |
| **Step 4 Confusion Matrix PNGs** | **231** ($TN+FP$) | **41** ($FN+TP$) | 272 | **100% Match with Ground Truth** |
| **Step 3 EDA Report (`eda_report.md`)** | *N/A (Train Only)* | *N/A (Train Only)* | 1,264 | **Correctly Isolated (Did not touch test data)** |
| **Step 2 Report Markdown / Summary Text** | 228 ($83.82\%$) | 44 ($16.18\%$) | 272 | **Minor Text Discrepancy (Explained Below)** |

---

## 2. Root Cause Analysis of the Step 2 Text Discrepancy

**Why did the Step 2 text report state 228 / 44 while the actual CSV has 231 / 41?**

1. **Tokenization Refinement:**
   - During the preliminary exploratory check in Step 2, a simple whitespace regex `re.findall(r'\b\w+\b')` was drafted, which split hyphenated and apostrophe words into multiple standalone tokens (e.g., `cpu-bound` was split into `['cpu', 'bound']`, and `trade-off` into `['trade', 'off']`). This caused 3 borderline test answers to hit exactly 20 tokens, giving 44 positives ($44 + 228 = 272$).
   - When the production script `ml/prepare_academic_dataset.py` was authored, a more accurate linguistic tokenization function was used:
     $$\text{Token Pattern} = \verb|\b[\w'-]+\b|$$
   - Under this correct tokenization, compound hyphenated technical terms remained single words. Consequently, exactly 3 borderline answers dropped from 20 to 19 words, shifting them to Class 0 ($41$ positives, $231$ negatives).
2. **File Generation Sequence:**
   - The dataset exporter and the machine-readable summary `ml/preprocessing_summary.json` dynamically computed and wrote the **actual 231 / 41 distribution**.
   - However, the static markdown summary template in `prepare_academic_dataset.py` contained an un-updated placeholder string `228 / 44` from the initial exploratory regex run.
3. **Data Integrity Conclusion:**
   - The actual dataset on disk (`test_processed.csv`) was generated with **231 / 41**.
   - Step 4 model training loaded `test_processed.csv` directly and evaluated on the actual ground truth ($231 / 41$). Zero data corruption occurred.

---

## 3. Confusion Matrix Verification

Predictions were regenerated in memory directly from the serialized model artifacts (`knn_model.pkl`, `svm_model.pkl`, `decision_tree_model.pkl`) and `test_processed.csv`:

$$TN + FP = \text{Actual Class 0 Support} = 231$$
$$FN + TP = \text{Actual Class 1 Support} = 41$$
$$\text{Total Support} = TN + FP + FN + TP = 272$$

### Model-by-Model Verification:

| Model | $TN$ | $FP$ | $FN$ | $TP$ | $TN + FP$ (Class 0) | $FN + TP$ (Class 1) | Total ($N$) | Integrity Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline (Dummy)** | 231 | 0 | 41 | 0 | **231** | **41** | **272** | **Verified (100% Match)** |
| **KNN Classifier** | 226 | 5 | 6 | 35 | **231** | **41** | **272** | **Verified (100% Match)** |
| **SVM Classifier** | 231 | 0 | 8 | 33 | **231** | **41** | **272** | **Verified (100% Match)** |
| **Decision Tree** | 231 | 0 | 0 | 41 | **231** | **41** | **272** | **Verified (100% Match)** |

All four models satisfy $TN + FP = 231$ and $FN + TP = 41$ exactly.

---

## 4. Evaluation Metrics Verification

All evaluation metrics were recalculated in memory and compared against the values recorded in `ml/evaluation/test_results.csv` and `ml/evaluation/model_evaluation_report.md`:

### Comparison: Saved Results vs. Independent Recalculation

| Model | Metric | Value in Saved CSV / Report | Value Recalculated from Predictions | Match? |
| :--- | :--- | :---: | :---: | :---: |
| **Baseline** | Accuracy | 0.8493 | 0.8493 | **Exact Match** |
| | Macro F1 | 0.4592 | 0.4592 | **Exact Match** |
| | ROC-AUC | 0.5000 | 0.5000 | **Exact Match** |
| | PR-AUC | 0.1507 | 0.1507 | **Exact Match** |
| **KNN** | Accuracy | 0.9596 | 0.9596 | **Exact Match** |
| | Precision | 0.8750 | 0.8750 | **Exact Match** |
| | Recall | 0.8537 | 0.8537 | **Exact Match** |
| | F1-Score | 0.8642 | 0.8642 | **Exact Match** |
| | Macro F1 | 0.9202 | 0.9202 | **Exact Match** |
| | ROC-AUC | 0.9906 | 0.9906 | **Exact Match** |
| | PR-AUC | 0.9341 | 0.9341 | **Exact Match** |
| **SVM** | Accuracy | 0.9706 | 0.9706 | **Exact Match** |
| | Precision | 1.0000 | 1.0000 | **Exact Match** |
| | Recall | 0.8049 | 0.8049 | **Exact Match** |
| | F1-Score | 0.8919 | 0.8919 | **Exact Match** |
| | Macro F1 | 0.9374 | 0.9374 | **Exact Match** |
| | ROC-AUC | 0.9984 | 0.9984 | **Exact Match** |
| | PR-AUC | 0.9907 | 0.9907 | **Exact Match** |
| **Decision Tree** | Accuracy | 1.0000 | 1.0000 | **Exact Match** |
| | Precision | 1.0000 | 1.0000 | **Exact Match** |
| | Recall | 1.0000 | 1.0000 | **Exact Match** |
| | F1-Score | 1.0000 | 1.0000 | **Exact Match** |
| | Macro F1 | 1.0000 | 1.0000 | **Exact Match** |
| | ROC-AUC | 1.0000 | 1.0000 | **Exact Match** |
| | PR-AUC | 1.0000 | 1.0000 | **Exact Match** |

Every metric in the Step 4 reports matches the predictions to four decimal places.

---

## 5. Data Identity & Source File Confirmation

- **Primary Source File Used:** `D:\AI-Interview-Analyzer\ml\datasets\processed\test_processed.csv`
- **Secondary Root Mirror:** `D:\AI-Interview-Analyzer\ml\datasets\test_processed.csv`
- **File Equality Check:** Both files are identical bit-for-bit (same shape `272 rows x 15 columns`, same MD5 hash/content).
- **Stale Data Check:** Zero stale test files were used. No test data leaked into the training set.

---

## 6. Audit Conclusion

1. The test dataset on disk has always had **231 Class 0 and 41 Class 1** samples.
2. The Step 4 model training, evaluation, confusion matrices, and ROC/PR curves were executed on `test_processed.csv` ($231 / 41$).
3. The discrepancy in the Step 2 text summary was a static markdown documentation artifact caused by an earlier regex draft.
4. All metrics, confusion matrices, and model artifacts are verified.

