# Academic Exploratory Data Analysis (EDA) Report
**Project:** AI Interview Analyzer  
**Module:** Machine Learning Practical Assessment (Step 3)  
**Execution Environment:** Python 3.11, Pandas, NumPy, Matplotlib, Seaborn  
**Dataset Partitions:** Training (N = 1,264), Validation (N = 270), Test (N = 272) — Total: 1,806 records  

---

## 1. Dataset Overview

The analyzed corpus consists of 1,806 verified technical interview question-and-answer pairs partitioned into three isolated sets:
- **Training Set:** 1,264 records (Used strictly for statistical analysis and EDA).
- **Validation Set:** 270 records (Preserved for hyperparameter validation).
- **Test Set:** 272 records (Preserved for final unbiased model evaluation).

Each observation contains 5 core unscaled NLP and linguistic features, 5 standardized counterparts (scaled via training parameters), and a provisional binary target tier.

---

## 2. Statistical Summary Table (Training Set: N = 1,264)

| Feature | Mean | Median | Mode | Std Dev | Variance | Min | 25% | 50% | 75% | Max | Skewness | Kurtosis | Missing | Unique |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`semantic_similarity`** | 0.6481 | 0.6842 | 0.5719 | 0.1536 | 0.0236 | -0.0043 | 0.5752 | 0.6842 | 0.7617 | 0.9128 | -1.1021 | 0.9153 | 0 | 1,110 |
| **`lexical_overlap`** | 0.1068 | 0.1053 | 0.0000 | 0.0662 | 0.0044 | 0.0000 | 0.0526 | 0.1053 | 0.1500 | 0.3200 | 0.3575 | -0.1292 | 0 | 90 |
| **`word_count`** | 17.4462 | 17.0 | 18.0000 | 3.1057 | 9.6456 | 7.0000 | 15.0000 | 17.0000 | 19.0000 | 35.0000 | 0.3886 | 0.6846 | 0 | 22 |
| **`unique_word_ratio`** | 0.9405 | 0.9474 | 1.0000 | 0.0673 | 0.0045 | 0.5000 | 0.9091 | 0.9474 | 1.0000 | 1.0000 | -1.4946 | 3.1924 | 0 | 67 |
| **`avg_word_length`** | 6.3173 | 6.2750 | 6.0000 | 0.9973 | 0.9946 | 3.6500 | 5.6500 | 6.2750 | 7.0000 | 12.7100 | 0.3216 | 0.9068 | 0 | 331 |

---

## 3. Univariate Analysis Findings

1. **`semantic_similarity`**:
   - **Distribution Shape:** Moderately left-skewed (Skewness = `-1.1021`). The distribution peaks near 0.70 with a pronounced left tail descending to 0.0.
   - **Normality:** Non-normal; exhibits negative skew because reference interview answers are semantically aligned with the question topic by design.
   - **Outliers:** 43 outliers (3.40%) exist on the lower boundary ($< 0.2954$), representing vague, tangential, or generic answers.
2. **`lexical_overlap`**:
   - **Distribution Shape:** Slightly right-skewed (Skewness = `0.3575`), centered symmetrically around 0.105.
   - **Interpretation:** Jaccard overlap between question and answer word sets is typically modest (~10%) because answers expand on domain mechanisms rather than merely repeating question keywords.
3. **`word_count`**:
   - **Distribution Shape:** Approximately normal Gaussian bell curve with slight right skewness (Skewness = `0.3886`).
   - **Central Tendency:** Mean of `17.4462` words and median of `17.0` words (IQR: 15 to 19 words).
   - **Outliers:** 13 outliers (1.03%) exist representing exceptionally short answers ($< 9$ words) or unusually detailed answers ($> 25$ words).
4. **`unique_word_ratio`**:
   - **Distribution Shape:** Strongly left-skewed (Skewness = `-1.4946`) with heavy leptokurtic concentration (Kurtosis = 3.19).
   - **Interpretation:** Across short interview answers (~17 words), almost every word is unique, resulting in an exceptionally high mean ratio of `0.9405`.
5. **`avg_word_length`**:
   - **Distribution Shape:** Nearly normal distribution (Skewness = `0.3216`) centered at `6.3173` characters/word.
   - **Interpretation:** Reflects dense technical vocabulary (terms like *architecture*, *concurrency*, *multiprocessing*, *virtualization*). 4 extreme outliers exist up to 12.71 chars/word due to long specialized technical compound terms.

---

## 4. Bivariate Analysis Findings

1. **Semantic Similarity vs. Lexical Overlap ($r = 0.5550$):**
   - **Observation:** A strong, statistically significant positive linear relationship exists. Answers that reuse pertinent technical terms from the prompt achieve higher embedding cosine similarity.
2. **Semantic Similarity vs. Word Count ($r = 0.3284$):**
   - **Observation:** A moderate positive relationship. Extremely short answers ($< 12$ words) fail to provide sufficient context, whereas moderately comprehensive answers ($\ge 20$ words) afford dense conceptual alignment.
3. **Lexical Overlap vs. Word Count ($r = 0.2576$):**
   - **Observation:** Weak-to-moderate positive correlation. Longer answers incorporate more terms from the prompt question.
4. **Unique Word Ratio vs. Average Word Length ($r = 0.3270$):**
   - **Observation:** Positive correlation. Candidates using longer, sophisticated words tend to employ a broader, non-repetitive vocabulary.
5. **Feature vs. Target Class Distributions:**
   - As visualized in `plots/feature_vs_target.png`, the **Proficient** group exhibits dramatically higher medians for both `word_count` (median 22 vs 16) and `semantic_similarity` (median 0.77 vs 0.65) compared to the **Needs Improvement** group.

---

## 5. Correlation Analysis Findings

### Pearson Correlation Matrix Table:
| Feature | `semantic_similarity` | `lexical_overlap` | `word_count` | `unique_word_ratio` | `avg_word_length` | `target_label` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`semantic_similarity`** | **1.0000** | 0.5550 | 0.3284 | -0.1071 | 0.0884 | 0.3410 |
| **`lexical_overlap`** | 0.5550 | **1.0000** | 0.2576 | -0.2281 | 0.0240 | 0.2412 |
| **`word_count`** | 0.3284 | 0.2576 | **1.0000** | -0.3070 | -0.2436 | **0.5673** |
| **`unique_word_ratio`** | -0.1071 | -0.2281 | -0.3070 | **1.0000** | 0.3270 | -0.2270 |
| **`avg_word_length`** | 0.0884 | 0.0240 | -0.2436 | 0.3270 | **1.0000** | -0.0901 |
| **`target_label`** | 0.3410 | 0.2412 | **0.5673** | -0.2270 | -0.0901 | **1.0000** |

- **Top Positive Correlate with Target:** `word_count` ($r = 0.5673$), followed by `semantic_similarity` ($r = 0.3410$).
- **Multicollinearity Check:** The highest inter-feature correlation is between `semantic_similarity` and `lexical_overlap` ($r = 0.5550$). Because all $|r| < 0.70$, there is no severe multicollinearity that would destabilize linear or tree-based classifiers.

---

## 6. Class Imbalance Analysis

- **Dominant Class:** **Needs Improvement (Class 0)** comprising **1,085 samples (85.84%)**.
- **Minority Class:** **Proficient (Class 1)** comprising **179 samples (14.16%)**.
- **Imbalance Ratio:** **~5.45 : 1**.

### Academic Implications for Modeling:
1. **Accuracy Paradox:** A trivial baseline model predicting Class 0 for every sample would attain 84.49% accuracy despite learning zero actual predictive logic.
2. **Required Evaluation Metrics:** Accuracy must be supplemented with **Precision, Recall, F1-Score (Macro & Weighted), and ROC-AUC** in Step 4.
3. **Class Weighting:** Algorithms like SVM and Decision Trees should utilize `class_weight='balanced'` during training to avoid minority class starvation.

---

## 7. Outlier Analysis (Interquartile Range Method)

Using $IQR = Q_3 - Q_1$ with bounds $[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$:
- **`semantic_similarity`**: 43 outliers (3.40%) on the lower bound ($< 0.2954$). Valid real-world phenomena reflecting non-responsive answers.
- **`lexical_overlap`**: 6 outliers (0.47%) on the upper bound ($> 0.2961$).
- **`word_count`**: 13 outliers (1.03%) with lengths exceeding 25 words or below 9 words.
- **`unique_word_ratio`**: 33 outliers (2.61%) below 0.7728.
- **`avg_word_length`**: 4 outliers (0.32%) exceeding 9.025 characters/word.

*Academic Decision:* All outliers represent genuine linguistic and semantic variation in candidate answers and must be retained rather than truncated.

---

## 8. Target Dependency & Leakage Disclosure

As documented in `plots/target_leakage_decision_boundary.png`:
- The target boundary is governed by:
  $$\text{Proficient} \iff (\text{semantic\_similarity} \ge 0.70) \land (\text{word\_count} \ge 20)$$
- **Academic Limitation:** Models provided with `semantic_similarity` and `word_count` will easily learn this rectangular boundary. This experiment demonstrates the mathematical functioning of classification algorithms and evaluation metrics for the university syllabus, but should not be conflated with subjective human evaluations.

---

## 9. Important Visual Observations Summary

| Visualization File | Key Graphical Finding |
| :--- | :--- |
| `plots/target_distribution.png` | Highlights the 5.45:1 imbalance (85.84% vs 14.16%). |
| `plots/semantic_similarity_distribution.png` | Shows the left-skewed density peak at ~0.70 with lower tail. |
| `plots/word_count_distribution.png` | Demonstrates the bell curve centered around 17 words. |
| `plots/feature_correlation_heatmap.png` | Confirms moderate positive correlation ($r = 0.555$) between lexical overlap and semantic similarity. |
| `plots/feature_pairplot.png` | Clear green clustering in the upper-right corner of the word_count vs. semantic_similarity plane. |
| `plots/feature_vs_target.png` | Marked separation in median box plots for word count and semantic similarity between classes. |
| `plots/target_leakage_decision_boundary.png` | Exact rectangular quadrant boundary separating Proficient from Needs Improvement. |

---

## 10. Conclusion

The processed dataset exhibits robust statistical properties, clean distributions, zero missing values, and well-behaved variance across all features. The feature space is fully prepared for model training, cross-validation, and performance comparison in Step 4.
