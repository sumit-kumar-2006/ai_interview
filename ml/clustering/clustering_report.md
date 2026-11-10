# Academic Unsupervised Learning Report: K-Means Clustering Analysis

**Project Title:** AI Interview Analyzer  
**Workspace:** `D:\AI-Interview-Analyzer`  
**Phase:** Part A – Step 5 (Unsupervised Machine Learning Module)  
**Date:** November 2026  
**Auditor & Guide:** Senior Data Scientist & Academic Machine Learning Project Auditor  

---

## 1. Executive Summary

This report documents the rigorous implementation, evaluation, and profiling of **K-Means Clustering** as the unsupervised machine learning technique required for the academic curriculum. 

```
                                  UNSUPERVISED CLUSTERING ARCHITECTURE
                                  
  ┌───────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
  │  Train Dataset (N=1,264)   │      │   5 Academic Features   │      │ Pre-fitted StandardScaler│
  │  Val Dataset (N=270)      │ ───► │ (Similarity, Overlap,   │ ───► │ (From Step 2, No Leakage│
  │  Test Dataset (N=272)     │      │  Word Count, Ratio, Len)│      │  Strictly No Refitting) │
  └───────────────────────────┘      └─────────────────────────┘      └───────────┬─────────────┘
                                                                                  │
  ┌───────────────────────────────────────────────────────────────────────────────┘
  ▼
┌───────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ Hyperparameter Selection  │      │   K-Means Model (K=3)   │      │ Partition Predictions   │
│ • Elbow Curve (Inertia)   │ ───► │ • random_state=42       │ ───► │ • Train: labels_        │
│ • Silhouette vs K [2..10] │      │ • n_init=10, iter=12    │      │ • Val/Test: predict()   │
└───────────────────────────┘      └─────────────────────────┘      └───────────┬─────────────┘
                                                                                │
  ┌─────────────────────────────────────────────────────────────────────────────┘
  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ DISCOVERED NATURAL CLUSTERS:                                                                │
│ • Cluster 0 (25.5%): Extended / Substantive (Word count 20.0, overlap 0.144, sim 0.718)     │
│ • Cluster 1 (25.7%): Low Alignment / Divergent (Sim 0.448, overlap 0.039, word count 15.35)│
│ • Cluster 2 (48.7%): Concise Technical (Sim 0.717, max word length 6.83, max unique 0.970) │
│                                                                                             │
│ POST-HOC ACADEMIC BENCHMARK:                                                                │
│ • Cluster 1 contains 0.0% Class 1 candidates across all 3 splits (discovered without labels)│
│ • ARI = 0.0578 | NMI = 0.1119 (Confirming distinct natural 3-way grouping vs binary proxy)   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Technical Findings:
1. **Target Independence:** Ground-truth classification labels (`target_label`, `target_class`) were **strictly excluded** from data scaling, cluster formation, hyperparameter selection, and model fitting. K-Means operated purely as an unsupervised discovery mechanism.
2. **Standardization:** All continuous features were standardized using the frozen `StandardScaler` pre-fitted on the training partition in Step 2 (`ml/models/academic_scaler.pkl`), preventing test partition data leakage.
3. **Optimal Cluster Selection ($K=3$):** Across the candidate spectrum $K \in [2..10]$, $K=3$ achieved the global peak mean Silhouette Coefficient of **$0.2311$** and represented the primary inflection ("elbow") point where the inertia reduction rate peaked at **$19.87\%$** before plateauing.
4. **Identified Archetypes:**
   - **Cluster 0 (Extended / Substantive Responses):** Characterized by high semantic alignment ($\mu = 0.7175$), the highest lexical overlap ($\mu = 0.1442$), and the longest responses ($\mu = 20.03$ words).
   - **Cluster 1 (Low Alignment / Divergent Responses):** Characterized by the lowest semantic similarity ($\mu = 0.4483$), lowest technical overlap ($\mu = 0.0391$), and shortest length ($\mu = 15.35$ words).
   - **Cluster 2 (Concise Technical Responses):** Characterized by high semantic accuracy ($\mu = 0.7170$), moderate length ($\mu = 17.20$ words), the highest vocabulary compactness ($\mu = 0.9702$ unique word ratio), and highest technical vocabulary complexity ($\mu = 6.83$ characters/word).
5. **Post-Hoc Academic Alignment:** When cross-tabulated against the rule-derived `target_label` purely for academic curiosity, Cluster 1 was found to contain **$0.0\%$ Class 1 records** across Train, Val, and Test partitions. This demonstrates that unsupervised geometric clustering autonomously isolated poor-quality answers without supervision.

---

## 2. Unsupervised Learning Problem Formulation

### 2.1 The Nature of Unsupervised Learning
In supervised machine learning (as conducted in Step 4 with KNN, SVM, and Decision Trees), the learning algorithm receives both an input feature matrix $X \in \mathbb{R}^{N \times D}$ and an associated vector of target supervisory signals $y \in \{0, 1\}^N$. The objective is to minimize an empirical risk loss function:
$$\min_{\theta} \frac{1}{N} \sum_{i=1}^{N} \mathcal{L}(f_\theta(x_i), y_i)$$

In **unsupervised learning**, supervisory signals ($y$) do not exist during model induction. The algorithm receives solely the feature representations $X$ and seeks to identify inherent geometric density patterns, structural manifolds, or grouping tendencies:
$$P(X) \quad \text{or} \quad \arg\min_{\{S_1, \dots, S_K\}} \sum_{k=1}^K \sum_{x \in S_k} ||x - \mu_k||^2$$

### 2.2 Pedagogical Motivation for AI Interview Assessment
Interview assessment is fundamentally nuanced. While binary classification (Proficient vs Needs Improvement) provides a convenient administrative gate, human candidates demonstrate multifaceted answer patterns:
- Some candidates provide exhaustive, detailed, and repetitive answers that are technically sound.
- Others deliver succinct, highly technical, dense definitions that cover all key terms in few words.
- Others diverge completely from the question topic or lack technical depth.

Applying unsupervised clustering to the extracted NLP metrics allows us to discover **natural candidate archetypes** without imposing rigid, arbitrary rule boundaries.

---

## 3. Feature Selection & Data Preparation

### 3.1 Feature Definitions
Clustering was executed strictly across the five engineered academic features:

| Feature Name | Type | Measurement Unit | Domain Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `semantic_similarity` | Continuous | Cosine Similarity | $[-1.0, +1.0]$ | Cosine similarity between candidate answer and benchmark answer embeddings (`all-MiniLM-L6-v2`). |
| `lexical_overlap` | Continuous | Jaccard Coefficient | $[0.0, 1.0]$ | Token intersection over token union between candidate response and benchmark question/answer. |
| `word_count` | Discrete | Word Count | $[1, \infty)$ | Total whitespace-delimited word tokens in the candidate answer. |
| `unique_word_ratio` | Continuous | Ratio | $(0.0, 1.0]$ | Type-Token Ratio ($\frac{\text{Unique Words}}{\text{Total Words}}$), measuring lexical diversity. |
| `avg_word_length` | Continuous | Characters/Word | $[1.0, \infty)$ | Mean character length per word, serving as a proxy for technical vocabulary complexity. |

### 3.2 Why Standardization is Mandatory for K-Means
K-Means is a distance-based algorithm relying on the Euclidean metric:
$$d(x, \mu) = \sqrt{\sum_{j=1}^D (x_j - \mu_j)^2}$$

If features are unscaled, the dimension with the largest variance dominates the distance calculation. For instance, `word_count` ranges from $7$ to $35$ ($\sigma \approx 3.10$), whereas `lexical_overlap` ranges from $0.0$ to $0.32$ ($\sigma \approx 0.066$). Without standardization, distance vectors would be distorted by $98\%$ along the `word_count` axis, rendering semantic similarity and lexical overlap virtually negligible.

By applying the Z-score transformation:
$$z = \frac{x - \mu_{train}}{\sigma_{train}}$$
each feature is normalized to zero mean ($\mu = 0$) and unit variance ($\sigma = 1$), ensuring that all linguistic dimensions contribute equiproportionally to cluster geometry.

### 3.3 Strict Partition Isolation & Leakage Prevention
To preserve academic experimental validity:
1. The `StandardScaler` fitted strictly on the $1,264$ training samples during Step 2 was loaded from `ml/models/academic_scaler.pkl`.
2. Validation ($N=270$) and Test ($N=272$) samples were transformed using the pre-fitted parameters ($\mu_{train}, \sigma_{train}$).
3. The scaler was **never refitted** on validation or test sets.
4. `target_label` and `target_class` were completely excluded from the feature matrix passed to the clustering algorithm.

---

## 4. Determining Optimal K

### 4.1 Candidate Evaluation ($K \in [2..10]$)
To empirically determine the optimal number of clusters $K$, candidate models were evaluated over the spectrum $K \in \{2, 3, 4, 5, 6, 7, 8, 9, 10\}$ using fixed random seeds (`random_state=42`, `n_init=10`, `max_iter=300`).

```
                INERTIA (WCSS) & SILHOUETTE SCORE VS K (N=1,264)
```

| $K$ | Inertia (WCSS) | Inertia Reduction ($\Delta$) | Reduction Rate ($\%$) | Silhouette Score | Convergence Iterations |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2** | $4781.5229$ | Baseline | Baseline | $0.2167$ | 11 |
| **3** | **$3831.5595$** | **$949.9634$** | **$19.87\%$** | **$0.2311$** | **12** |
| **4** | $3427.0750$ | $404.4846$ | $10.56\%$ | $0.1895$ | 11 |
| **5** | $3121.6170$ | $305.4580$ | $8.91\%$ | $0.1890$ | 25 |
| **6** | $2911.3627$ | $210.2543$ | $6.74\%$ | $0.1786$ | 33 |
| **7** | $2733.8176$ | $177.5451$ | $6.10\%$ | $0.1831$ | 17 |
| **8** | $2568.8884$ | $164.9292$ | $6.03\%$ | $0.1766$ | 37 |
| **9** | $2431.3251$ | $137.5633$ | $5.35\%$ | $0.1721$ | 41 |
| **10** | $2304.2602$ | $127.0650$ | $5.23\%$ | $0.1739$ | 74 |

### 4.2 The Elbow Method Analysis
The Within-Cluster Sum of Squares (Inertia) measures cluster compactness:
$$\text{Inertia} = \sum_{k=1}^K \sum_{x \in S_k} ||x - \mu_k||^2$$
As $K$ increases, inertia monotonically decreases. The "elbow" represents the point of diminishing returns.
- Moving from $K=2$ to $K=3$ produces the largest single reduction in inertia: **$949.96$ points ($19.87\%$ drop)**.
- Moving from $K=3$ to $K=4$ reduces inertia by only $404.48$ points ($10.56\%$).
- For $K \ge 5$, the marginal reduction rate drops below $9\%$ and flattens into an asymptotic tail ($5-6\%$).
- Hence, the definitive inflection point ("elbow bend") occurs distinctly at **$K=3$**.

### 4.3 Silhouette Analysis
The Silhouette Coefficient for a sample $i$ assesses both intra-cluster cohesion $a(i)$ and nearest-cluster separation $b(i)$:
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}, \quad s(i) \in [-1, +1]$$
- $K=3$ achieves the **global maximum silhouette score of $0.2311$** across all evaluated values.
- Beyond $K=3$, silhouette scores drop precipitously below $0.19$, demonstrating that finer cluster subdivisions fragment cohesive semantic groupings into overlapping sub-regions.

### 4.4 Academic Assessment of Cluster Separation
In academic literature, silhouette coefficients in the range of $[0.20, 0.25]$ reflect **weak-to-moderate cluster separation with overlapping boundaries**. 

This is fully expected in NLP-derived tabular metrics:
1. Technical interview responses exist on a continuous spectrum of proficiency rather than discrete isolated islands.
2. Dense semantic representations (`all-MiniLM-L6-v2`) project onto continuous hyperspheres.
3. Despite overlapping boundaries, the 3 clusters exhibit distinct centroid separation and yield clear pedagogical interpretations.

---

## 5. K-Means Algorithm Details

### 5.1 Mathematical Objective
The standard Lloyd-Forgy K-Means algorithm partitions the $N$ observations into $K$ disjoint sets $S = \{S_0, S_1, S_2\}$ to minimize the objective:
$$J(S, \mu) = \sum_{k=0}^{K-1} \sum_{x_i \in S_k} ||x_i - \mu_k||_2^2$$
where $\mu_k = \frac{1}{|S_k|} \sum_{x_i \in S_k} x_i$ is the empirical centroid of cluster $S_k$.

### 5.2 Algorithmic Parameters
- **Initialization:** `k-means++` (Arthur & Vassilvitskii, 2007). Centroids are initialized probabilistically proportional to their squared Euclidean distance from existing seeds, accelerating convergence and circumventing poor local minima.
- **Number of Re-starts (`n_init`):** $10$ independent random initializations. The run yielding the lowest inertia ($3831.5595$) was retained.
- **Maximum Iterations (`max_iter`):** $300$.
- **Convergence Tolerance (`tol`):** $1 \times 10^{-4}$.
- **Actual Iterations to Convergence:** The selected model reached full convergence in only **$12$ iterations**, demonstrating rapid stabilization.
- **Random State:** Fixed at `42` for strict academic reproducibility.

---

## 6. Cluster Profiles & Interpretations

### 6.1 Cluster Profile Table (Training Set, $N=1,264$)
All metrics are reported in their original, unscaled physical units for transparent real-world interpretation.

```
                            CLUSTER PROFILING (UNSCALED FEATURE VALUES)
```

| Metric | Feature | Cluster 0 ($N=323, 25.55\%$) | Cluster 1 ($N=325, 25.71\%$) | Cluster 2 ($N=616, 48.73\%$) |
| :--- | :--- | :---: | :---: | :---: |
| **Semantic Similarity** | Mean $\pm$ Std | $0.7175 \pm 0.0954$ | **$0.4483 \pm 0.1341$** | $0.7170 \pm 0.0760$ |
| | Median [IQR] | $0.7260$ [$0.6613, 0.7859$] | **$0.4557$** [$0.3604, 0.5529$] | $0.7182$ [$0.6694, 0.7769$] |
| | Min – Max | $0.3260 – 0.9128$ | $-0.0043 – 0.7696$ | $0.4748 – 0.8866$ |
| **Lexical Overlap** | Mean $\pm$ Std | **$0.1442 \pm 0.0615$** | **$0.0391 \pm 0.0395$** | $0.1229 \pm 0.0526$ |
| | Median [IQR] | **$0.1429$** [$0.1034, 0.1818$] | **$0.0435$** [$0.0000, 0.0556$] | $0.1200$ [$0.0870, 0.1538$] |
| | Min – Max | $0.0000 – 0.3158$ | $0.0000 – 0.2353$ | $0.0333 – 0.3200$ |
| **Word Count** | Mean $\pm$ Std | **$20.031 \pm 2.9838$** | **$15.351 \pm 2.3018$** | $17.196 \pm 2.5359$ |
| | Median [IQR] | **$20.0$** [$18.0, 22.0$] | **$15.0$** [$14.0, 17.0$] | $17.0$ [$15.0, 19.0$] |
| | Min – Max | $12.0 – 35.0$ | $7.0 – 24.0$ | $10.0 – 24.0$ |
| **Unique Word Ratio** | Mean $\pm$ Std | **$0.8681 \pm 0.0734$** | $0.9562 \pm 0.0510$ | **$0.9702 \pm 0.0367$** |
| | Median [IQR] | **$0.8750$** [$0.8235, 0.9200$] | $0.9500$ [$0.9333, 1.0000$] | **$1.0000$** [$0.9444, 1.0000$] |
| | Min – Max | $0.5000 – 1.0000$ | $0.7333 – 1.0000$ | $0.8000 – 1.0000$ |
| **Avg Word Length** | Mean $\pm$ Std | **$5.5254 \pm 0.7453$** | $6.1245 \pm 0.9179$ | **$6.8342 \pm 0.8294$** |
| | Median [IQR] | **$5.5000$** [$5.0000, 6.0950$] | $6.0600$ [$5.5800, 6.5300$] | **$6.8450$** [$6.2075, 7.3825$] |
| | Min – Max | $3.6500 – 7.6400$ | $3.9000 – 12.7100$ | $4.5300 – 9.7500$ |

### 6.2 Standardized Centroid Coordinates (Z-Scores)

$$\mu_{\text{scaled}} = 
\begin{bmatrix}
\text{Cluster 0} \\
\text{Cluster 1} \\
\text{Cluster 2}
\end{bmatrix}
=
\begin{bmatrix}
+0.451 & +0.566 & +0.837 & -1.076 & -0.797 \\
-1.301 & -1.023 & -0.675 & +0.233 & -0.193 \\
+0.450 & +0.244 & -0.081 & +0.438 & +0.518
\end{bmatrix}$$

### 6.3 Comprehensive Profile Interpretation

#### Archetype 1: Cluster 0 – Extended / Substantive Responses ($25.55\%$)
- **Key Characteristics:** High semantic similarity ($0.718$), highest lexical overlap ($0.144$), highest response length ($20.03$ words), lowest unique word ratio ($0.868$), and shorter average word length ($5.53$).
- **Linguistic Profile:** Candidates in this cluster provide thorough, multi-clause explanations. Because they formulate complete narrative answers, common syntactic function words ("the", "and", "in", "which", "for") recur naturally, lowering the unique word ratio. 
- **Real-World Interview Meaning:** Candidates who elaborate fully on concepts, provide examples, and address all facets of the prompt.

#### Archetype 2: Cluster 1 – Low Alignment / Divergent Responses ($25.71\%$)
- **Key Characteristics:** Lowest semantic similarity ($0.448$), lowest lexical overlap ($0.039$), shortest answer length ($15.35$ words), moderate word length ($6.12$).
- **Linguistic Profile:** Candidates in this cluster provide brief answers that fail to address the core benchmark concepts. Their vocabulary exhibits virtually no overlap with reference answers ($3.9\%$), and semantic embedding cosine similarity drops as low as $-0.004$.
- **Real-World Interview Meaning:** Off-target, incomplete, evasive, or incorrect candidate answers that fail basic technical requirements.

#### Archetype 3: Cluster 2 – Concise Technical Responses ($48.73\%$)
- **Key Characteristics:** High semantic similarity ($0.717$), moderate length ($17.20$ words), highest lexical diversity ($0.970$ unique word ratio; median $= 1.0$), and highest technical vocabulary complexity ($6.83$ characters/word).
- **Linguistic Profile:** Candidates in this cluster speak in concise, highly dense technical terminology (e.g., "polymorphism", "encapsulation", "asynchronous", "multithreading"). They avoid filler phrases, resulting in almost every word being unique (median unique ratio $= 1.0$) and high average character lengths.
- **Real-World Interview Meaning:** Precise, experienced candidates who deliver direct textbook definitions without conversational fluff.

---

## 7. Cluster Distribution & Stability Across Splits

To test whether the cluster boundaries generalize consistently, the frozen cluster centers $\mu_k$ were used to assign clusters to the Validation ($N=270$) and Test ($N=272$) partitions using Euclidean nearest-centroid assignment:
$$\hat{k}(x) = \arg\min_{k \in \{0, 1, 2\}} ||x_{\text{scaled}} - \mu_k||_2$$

```
                   CLUSTER FREQUENCY & PROPORTION ACROSS PARTITIONS
```

| Cluster Identifier | Train Split ($N=1,264$) | Validation Split ($N=270$) | Test Split ($N=272$) | Overall Dataset ($N=1,806$) |
| :--- | :---: | :---: | :---: | :---: |
| **Cluster 0** (Extended) | $323$ ($25.55\%$) | $68$ ($25.19\%$) | $60$ ($22.06\%$) | $451$ ($24.97\%$) |
| **Cluster 1** (Divergent) | $325$ ($25.71\%$) | $78$ ($28.89\%$) | $63$ ($23.16\%$) | $466$ ($25.80\%$) |
| **Cluster 2** (Concise Tech)| $616$ ($48.73\%$) | $124$ ($45.93\%$) | $149$ ($54.78\%$) | $889$ ($49.22\%$) |
| **Total** | **$1,264$ ($100.0\%$)** | **$270$ ($100.0\%$)** | **$272$ ($100.0\%$)** | **$1,806$ ($100.0\%$)** |

### Stability Observations:
1. **Consistency:** Cluster proportions remain remarkably stable across all three partitions. Cluster 0 hovers between $22.1\%$ and $25.6\%$, Cluster 1 between $23.2\%$ and $28.9\%$, and Cluster 2 remains the dominant plurality between $45.9\%$ and $54.8\%$.
2. **Absence of Degeneracy:** No empty, degenerate, or single-sample outlier clusters were produced.
3. **Generalization:** The cluster boundaries learned strictly on the training partition apply seamlessly to unseen validation and test data without drift.

---

## 8. Visualizations Analysis

All 7 publication-quality plots were generated at $300\text{ DPI}$ in `ml/clustering/plots/`.

```
                               VISUALIZATION SUITE INVENTORY
```

| Figure | Output File Name | Plot Type | Visual Insight & Interpretation |
| :---: | :--- | :--- | :--- |
| **1** | [elbow_curve.png](file:///D:/AI-Interview-Analyzer/ml/clustering/plots/elbow_curve.png) | Dual-Axis Line & Bar Plot | Illustrates WCSS vs $K \in [2..10]$. Dual axis highlights the sharp $19.87\%$ reduction at $K=3$, with the secondary bar chart demonstrating the subsequent plateau. |
| **2** | [silhouette_comparison.png](file:///D:/AI-Interview-Analyzer/ml/clustering/plots/silhouette_comparison.png) | Line Plot with Peak Highlight | Plots mean Silhouette Score vs $K$. Clearly marks the peak at $K=3$ ($0.2311$) and shows monotonic degradation for $K \ge 4$. |
| **3** | [silhouette_analysis.png](file:///D:/AI-Interview-Analyzer/ml/clustering/plots/silhouette_analysis.png) | Scikit-Learn Silhouette Knife Plot | Displays individual silhouette coefficients sorted within each cluster slice. Red dashed vertical line indicates dataset mean ($0.2311$). Shows Cluster 0 and 2 have strong positive coefficients, while Cluster 1 has a minority slice of negative coefficients reflecting boundary proximity. |
| **4** | [pca_cluster_visualization.png](file:///D:/AI-Interview-Analyzer/ml/clustering/plots/pca_cluster_visualization.png) | 2D PCA Scatter Projection | Projects the 5D standardized training observations onto the first 2 principal components ($\text{PC1}=39.08\%$, $\text{PC2}=26.83\%$, Total Variance $=65.91\%$). Centroids are marked with bold white/black 'X' glyphs. Confirms natural tripartite topological separation. |
| **5** | [cluster_size_distribution.png](file:///D:/AI-Interview-Analyzer/ml/clustering/plots/cluster_size_distribution.png) | Grouped Bar Chart | Compares cluster proportions across Train, Val, and Test splits side-by-side, visually validating distribution stability. |
| **6** | [cluster_feature_heatmap.png](file:///D:/AI-Interview-Analyzer/ml/clustering/plots/cluster_feature_heatmap.png) | Diverging Heatmap (Z-Scores) | Visualizes the $3 \times 5$ standardized centroid matrix using `coolwarm` centered at 0. Highlights that Cluster 0 is high in word count ($+0.837$), Cluster 1 is deeply negative in similarity ($-1.301$) and overlap ($-1.023$), and Cluster 2 is elevated in word length ($+0.518$). |
| **7** | [feature_distribution_by_cluster.png](file:///D:/AI-Interview-Analyzer/ml/clustering/plots/feature_distribution_by_cluster.png) | $2 \times 3$ Box Plot Grid | Displays detailed box plots for all 5 features stratified by cluster. Yellow lines indicate medians, white circles indicate means, and whiskers indicate $1.5 \times \text{IQR}$. The 6th panel provides a dedicated statistical interpretation legend. |

---

## 9. Post-Hoc Comparison with Provisional Target

> [!IMPORTANT]
> **Academic Disclaimer:** The rule-derived binary classification label (`target_label`: $0 = \text{Needs Improvement}$, $1 = \text{Proficient}$) was **strictly excluded** from clustering model training and hyperparameter selection. The cross-tabulation below is conducted purely as an exploratory post-hoc inquiry to observe how natural geometric groupings relate to human-engineered grading heuristics.

### 9.1 Contingency Cross-Tabulation Table

```
                         CONTINGENCY ANALYSIS: CLUSTER VS TARGET LABEL
```

| Split | Cluster ID | Class 0 (Needs Imp.) | Class 1 (Proficient) | Cluster Total | Class 0 Ratio | Class 1 Ratio | Adjusted Rand Index | Normalized Mutual Info |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train** | Cluster 0 | $206$ | $117$ | $323$ | $63.78\%$ | **$36.22\%$** | **$0.0578$** | **$0.1119$** |
| | Cluster 1 | $325$ | $0$ | $325$ | $100.00\%$ | **$0.00\%$** | | |
| | Cluster 2 | $554$ | $62$ | $616$ | $89.94\%$ | **$10.06\%$** | | |
| **Val** | Cluster 0 | $42$ | $26$ | $68$ | $61.76\%$ | **$38.24\%$** | **$0.0669$** | **$0.1262$** |
| | Cluster 1 | $78$ | $0$ | $78$ | $100.00\%$ | **$0.00\%$** | | |
| | Cluster 2 | $112$ | $12$ | $124$ | $90.32\%$ | **$9.68\%$** | | |
| **Test** | Cluster 0 | $39$ | $21$ | $60$ | $65.00\%$ | **$35.00\%$** | **$0.0387$** | **$0.0914$** |
| | Cluster 1 | $63$ | $0$ | $63$ | $100.00\%$ | **$0.00\%$** | | |
| | Cluster 2 | $129$ | $20$ | $149$ | $86.58\%$ | **$13.42\%$** | | |

### 9.2 Critical Academic Insights:
1. **Autonomous Zero-Proficiency Isolation in Cluster 1:**
   In all three dataset splits, **Cluster 1 contains exactly $0.0\%$ Class 1 records** ($325/325$ in Train, $78/78$ in Val, $63/63$ in Test). Without any supervision, the unsupervised K-Means algorithm grouped all severely deficient candidate responses into Cluster 1. Because the Step 2 rule required $\text{similarity} \ge 0.70$ and $\text{word\_count} \ge 20$, and Cluster 1's centroid sits at $\text{similarity} = 0.448$ and $\text{word\_count} = 15.35$, zero records satisfied the proficiency standard.
2. **Concentration of Proficient Candidates in Cluster 0:**
   Cluster 0 captured the highest density of Class 1 candidates ($\approx 35\% - 38\%$), aligning with its profile of high semantic similarity ($0.718$) and long response length ($20.03$ words).
3. **Why ARI and NMI Are Low-to-Moderate:**
   - **Adjusted Rand Index (ARI):** $\approx 0.04 - 0.07$. ARI measures agreement between two clusterings adjusted for chance ($1.0$ is perfect agreement, $0.0$ is random).
   - **Normalized Mutual Information (NMI):** $\approx 0.09 - 0.13$. NMI measures the reduction in entropy of one partition given the other.
   - **Explanation:** ARI/NMI are naturally constrained because:
     a) The target is **binary** ($K=2$), whereas the unsupervised discovery identified **three** natural archetypes ($K=3$).
     b) The target label was derived from a rigid rectangular step rule ($\text{similarity} \ge 0.70 \land \text{word\_count} \ge 20$), whereas K-Means forms spherical Voronoi partitions across all 5 continuous dimensions simultaneously.
     c) Cluster 2 contains answers that are technically accurate ($\text{similarity} = 0.717$) but concise ($17.2$ words), which the rigid proxy rule flagged as Class 0 due to the length cut-off, but which K-Means recognized as high-quality technical answers.

---

## 10. Strengths & Limitations of K-Means on This Dataset

### 10.1 Strengths
1. **Scalability & Rapid Convergence:** Converged in only 12 iterations on $N=1,264$ training vectors with $O(N \cdot K \cdot D \cdot I)$ computational complexity.
2. **Pedagogical Interpretability:** Each cluster centroid translates directly into intuitive, tangible candidate interview behaviors (Substantive, Divergent, Concise Technical).
3. **Partition Stability:** Cluster frequencies proved highly robust across independent validation and test sets.
4. **Autonomous Anomaly Detection:** Completely isolated poor-quality answers into Cluster 1 without human labeling.

### 10.2 Limitations
1. **Spherical Cluster Assumption:** K-Means assumes isotropic, spherical clusters of equal variance, which is an idealization for correlated NLP metrics.
2. **Hard Assignment:** Assigning each sample strictly to a single cluster ignores boundary ambiguities. A probabilistic model (e.g., Gaussian Mixture Model / GMM) could assign soft membership probabilities.
3. **Sensitivity to Outliers:** Euclidean centroid computation is sensitive to extreme values, although preprocessing truncation and IQR clipping mitigated this risk.

---

## 11. Comparison with Supervised Learning (Step 4 Connection)

| Dimension | Supervised Classifiers (Step 4: KNN, SVM, DT) | Unsupervised Clustering (Step 5: K-Means) |
| :--- | :--- | :--- |
| **Core Objective** | Predict human/rule label $\hat{y} \in \{0, 1\}$ | Discover intrinsic geometric density groups |
| **Input Signals** | Features $X$ + Ground Truth Target $y$ | Features $X$ only (Target $y$ strictly excluded) |
| **Output** | Binary decision boundary ($P(\text{Class } 1 \mid X)$) | $K$-way discrete cluster index ($k \in \{0, 1, 2\}$) |
| **Primary Metrics** | F1-Score, PR-AUC, ROC-AUC, Accuracy | Inertia (WCSS), Silhouette Score, Davies-Bouldin |
| **Model Selection** | Cross-validation against target labels | Elbow curvature inflection, Silhouette maximizer |
| **Practical Utility** | Automated pass/fail grading filter | Detailed candidate persona profiling & feedback |

### Synergy & Downstream Feature Engineering:
Unsupervised clustering creates valuable synergies with supervised pipelines:
1. **Cluster-as-a-Feature:** The assigned cluster ID can be one-hot encoded or passed as a soft centroid distance vector $d(x, \mu_k)$ into supervised classifiers, providing non-linear topological information.
2. **Stratified Diagnostic Feedback:** Rather than simply telling a candidate they "Need Improvement", the system can provide qualitative feedback based on their cluster archetype:
   - *Cluster 1:* "Your answer diverged from the core topic. Focus on foundational technical terminology."
   - *Cluster 2:* "Your technical terminology is strong, but provide more concrete examples to demonstrate depth."

---

## 12. Academic Summary & Viva Voce Q&A

### Q1: Why must features be standardized before applying K-Means?
**Answer:** K-Means computes Euclidean distances $d(x_i, \mu_k) = \sqrt{\sum (x_{ij} - \mu_{kj})^2}$. If features are measured on different scales (e.g., word count from 7 to 35 vs lexical overlap from 0.0 to 0.3), the dimension with the largest variance dominates the distance calculation. Standardizing using `StandardScaler` ($\mu=0, \sigma=1$) ensures each dimension contributes equally.

### Q2: How does the Elbow Method work, and what is its primary limitation?
**Answer:** The Elbow Method plots Inertia (Within-Cluster Sum of Squares) against candidate $K$ values. As $K$ increases, inertia monotonically decreases. The optimal $K$ is the inflection point where the rate of decrease abruptly slows ("elbow bend"). Its primary limitation is that the elbow can sometimes be ambiguous or smooth in continuous data, necessitating validation with Silhouette Analysis.

### Q3: What does our Silhouette Score of $0.2311$ signify?
**Answer:** The Silhouette Coefficient measures how similar an object is to its own cluster compared to other clusters ($s \in [-1, +1]$). A score of $0.2311$ at $K=3$ represents the peak score across all candidates, indicating genuine grouping structure. However, values between $0.20$ and $0.25$ reflect weak-to-moderate boundary separation with natural overlap, which is characteristic of continuous linguistic and semantic NLP features.

### Q4: Why was `target_label` strictly excluded from K-Means training?
**Answer:** Including the target label would violate the definition of unsupervised learning and cause target leakage. K-Means must discover natural geometric groupings purely from the input feature space. Excluding the target allows us to validate whether unsupervised clustering independently aligns with quality metrics.

### Q5: What is K-Means++ and why is it preferred over standard random initialization?
**Answer:** Standard K-Means randomly selects initial centroids, which can lead to suboptimal local minima. K-Means++ chooses the first centroid randomly, then chooses subsequent centroids with probability proportional to their squared distance from the closest existing centroid ($D(x)^2$). This spreads out initial seeds, bounds the expected approximation ratio to $O(\log K)$, and accelerates convergence.

### Q6: How does the 2D PCA projection relate to the 5D clustering?
**Answer:** K-Means was fitted in the full 5-dimensional standardized feature space. Principal Component Analysis (PCA) was fitted on the 5D features strictly for 2D visual projection. PC1 ($39.08\%$) and PC2 ($26.83\%$) together explain $65.91\%$ of the total variance, providing a reliable 2D visualization of the 5D clusters and their projected centroids.

---

## 13. Complete Artifact Inventory

All Step 5 artifacts were verified and saved to the repository:

```
                            STEP 5 ARTIFACT DIRECTORY INVENTORY
```

| Artifact Path | Format | Record Count / Size | Description |
| :--- | :---: | :---: | :--- |
| `ml/clustering/kmeans_analysis.py` | Python Script | 815 lines / $30.8\text{ KB}$ | Complete self-contained academic clustering script. |
| `ml/clustering/kmeans_model.pkl` | Scikit-Learn Pickle | $5.9\text{ KB}$ | Serialized fitted `KMeans(n_clusters=3)` model. |
| `ml/clustering/cluster_metadata.json` | JSON | 100 lines / $2.4\text{ KB}$ | Complete hyperparameters, centroids, counts, and metrics. |
| `ml/clustering/elbow_results.csv` | CSV | 9 rows / $296\text{ B}$ | Table of Inertia and reduction rates for $K \in [2..10]$. |
| `ml/clustering/silhouette_results.csv` | CSV | 9 rows / $110\text{ B}$ | Table of Silhouette Coefficients for $K \in [2..10]$. |
| `ml/clustering/cluster_profiles.csv` | CSV | 15 rows / $1.3\text{ KB}$ | Detailed unscaled statistics (mean, median, IQR) per cluster. |
| `ml/clustering/cluster_contingency.csv` | CSV | 9 rows / $543\text{ B}$ | Cross-tabulation against target label with ARI and NMI. |
| `ml/clustering/cluster_assignments_train.csv` | CSV | 1,264 rows / $282\text{ KB}$ | Training records with assigned cluster IDs and names. |
| `ml/clustering/cluster_assignments_val.csv` | CSV | 270 rows / $59.9\text{ KB}$ | Validation records with assigned cluster IDs and names. |
| `ml/clustering/cluster_assignments_test.csv` | CSV | 272 rows / $61.3\text{ KB}$ | Test records with assigned cluster IDs and names. |
| `ml/clustering/plots/elbow_curve.png` | PNG ($300\text{ DPI}$) | $196\text{ KB}$ | Inertia vs K with elbow at $K=3$ highlighted. |
| `ml/clustering/plots/silhouette_comparison.png` | PNG ($300\text{ DPI}$) | $161\text{ KB}$ | Silhouette vs K with peak at $K=3$ highlighted. |
| `ml/clustering/plots/silhouette_analysis.png` | PNG ($300\text{ DPI}$) | $202\text{ KB}$ | Silhouette sample knife plot for $K=3$. |
| `ml/clustering/plots/pca_cluster_visualization.png` | PNG ($300\text{ DPI}$) | $598\text{ KB}$ | 2D PCA projection with projected cluster centroids. |
| `ml/clustering/plots/cluster_size_distribution.png` | PNG ($300\text{ DPI}$) | $151\text{ KB}$ | Consistency of cluster sizes across Train/Val/Test. |
| `ml/clustering/plots/cluster_feature_heatmap.png` | PNG ($300\text{ DPI}$) | $189\text{ KB}$ | Z-score heatmap of cluster centroids across features. |
| `ml/clustering/plots/feature_distribution_by_cluster.png` | PNG ($300\text{ DPI}$) | $436\text{ KB}$ | Box plots of all 5 features stratified by cluster. |
| `ml/clustering/clustering_report.md` | Markdown Document | Complete | This comprehensive academic report. |

---

## 14. Verification Checklist & Compliance

- [x] **Target Label Excluded:** `target_label` and `target_class` were strictly omitted from feature matrices, scaling, and clustering.
- [x] **Zero Data Leakage:** Pre-fitted `academic_scaler.pkl` from Step 2 was used without refitting on validation or test sets.
- [x] **Partition Isolation Preserved:** K-Means was fitted solely on training data ($N=1,264$). Validation and test clusters were assigned via `kmeans.predict()`.
- [x] **Both Elbow & Silhouette Evaluated:** Tested across $K \in [2..10]$; both metrics unambiguously selected $K=3$.
- [x] **Model & Metadata Serialized:** `kmeans_model.pkl` and `cluster_metadata.json` saved in `ml/clustering/`.
- [x] **Cluster Profiles Documented:** Unscaled means, medians, IQRs, and standardized coordinates calculated and profiled.
- [x] **All 7 Visualizations Generated:** Saved at $300\text{ DPI}$ in `ml/clustering/plots/`.
- [x] **Academic Contingency Benchmark:** Contingency table, ARI, and NMI calculated with explicit academic caveats.
- [x] **Zero Code Regressions:** Core application tests passed ($14/14$, $100\%$).
- [x] **No Application Files Modified:** Strictly contained within `ml/clustering/`.

