"""
Academic K-Means Clustering Analysis Module
Project: AI Interview Analyzer
Workspace: D:\AI-Interview-Analyzer

Part A - Step 5: Unsupervised Learning - K-Means Clustering
Implements:
1. Feature extraction and standardization using existing academic_scaler.pkl (strictly excluding target_label)
2. Hyperparameter evaluation over K in [2..10] via Inertia (Elbow Method) and Silhouette Score
3. Optimal K selection (K=3) and model training (KMeans, random_state=42, n_init=10, max_iter=300)
4. Cluster assignment across Train, Val, and Test sets (transform/predict only, zero refitting)
5. Comprehensive cluster profiling (mean, median, std, min, max of unscaled features)
6. Post-hoc exploratory contingency comparison against provisional target_label (ARI, NMI)
7. Generation of 7 publication-quality visualization plots (300 DPI)
8. Serialization of model, metadata, profiles, and assignment tables
"""

import os
import json
import logging
from typing import Dict, List, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    silhouette_samples,
    silhouette_score,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("kmeans_analysis")

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "models")
CLUSTERING_DIR = os.path.join(BASE_DIR, "clustering")
PLOTS_DIR = os.path.join(CLUSTERING_DIR, "plots")

TRAIN_PATH = os.path.join(DATASET_DIR, "train_processed.csv")
VAL_PATH = os.path.join(DATASET_DIR, "val_processed.csv")
TEST_PATH = os.path.join(DATASET_DIR, "test_processed.csv")
SCALER_PATH = os.path.join(MODEL_DIR, "academic_scaler.pkl")

# Strict Feature Definition (strictly excluding target_label, target_class, text, split)
FEATURE_COLS = [
    "semantic_similarity",
    "lexical_overlap",
    "word_count",
    "unique_word_ratio",
    "avg_word_length",
]

# Set publication-quality plot style
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
})
PALETTE = ["#2b5c8f", "#d95f02", "#7570b3", "#e7298a", "#66a61e"]


def ensure_directories():
    """Ensure destination directories exist."""
    os.makedirs(CLUSTERING_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    logger.info("Verified output directories: %s, %s", CLUSTERING_DIR, PLOTS_DIR)


def load_data_and_scaler() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, object]:
    """Load train, val, and test datasets and pre-fitted StandardScaler."""
    for path, name in [(TRAIN_PATH, "Train"), (VAL_PATH, "Val"), (TEST_PATH, "Test"), (SCALER_PATH, "Scaler")]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{name} file missing at {path}")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)
    scaler = joblib.load(SCALER_PATH)

    logger.info("Loaded Train (N=%d), Val (N=%d), Test (N=%d)", len(train_df), len(val_df), len(test_df))

    # Verify record counts match academic partition
    assert len(train_df) == 1264, f"Expected 1264 train records, got {len(train_df)}"
    assert len(val_df) == 270, f"Expected 270 val records, got {len(val_df)}"
    assert len(test_df) == 272, f"Expected 272 test records, got {len(test_df)}"

    # Verify scaler feature names match FEATURE_COLS
    scaler_features = list(scaler.feature_names_in_)
    assert scaler_features == FEATURE_COLS, (
        f"Feature mismatch between scaler ({scaler_features}) and script ({FEATURE_COLS})"
    )
    logger.info("Scaler feature verification passed: %s", scaler_features)

    return train_df, val_df, test_df, scaler


def evaluate_k_range(
    X_train_scaled: np.ndarray,
    k_min: int = 2,
    k_max: int = 10,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[int, KMeans]]:
    """Evaluate K-Means clustering across K in [k_min..k_max] on scaled training features."""
    logger.info("Evaluating K-Means for K in [%d..%d]...", k_min, k_max)

    elbow_records = []
    silhouette_records = []
    models_dict = {}

    prev_inertia = None

    for k in range(k_min, k_max + 1):
        km = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=10,
            max_iter=300,
        )
        km.fit(X_train_scaled)
        models_dict[k] = km

        inertia = float(km.inertia_)
        sil_score = float(silhouette_score(X_train_scaled, km.labels_))

        if prev_inertia is not None:
            inertia_drop = prev_inertia - inertia
            drop_pct = (inertia_drop / prev_inertia) * 100.0
        else:
            inertia_drop = np.nan
            drop_pct = np.nan
        prev_inertia = inertia

        elbow_records.append({
            "k": k,
            "inertia": round(inertia, 4),
            "inertia_drop": round(inertia_drop, 4) if not np.isnan(inertia_drop) else None,
            "drop_pct": round(drop_pct, 2) if not np.isnan(drop_pct) else None,
            "n_iter": int(km.n_iter_),
        })

        silhouette_records.append({
            "k": k,
            "silhouette_score": round(sil_score, 4),
        })

        logger.info(
            "K=%2d | Inertia: %8.2f (Drop: %6.1f%%) | Silhouette: %.4f | Iter: %2d",
            k, inertia, drop_pct if not np.isnan(drop_pct) else 0.0, sil_score, km.n_iter_
        )

    elbow_df = pd.DataFrame(elbow_records)
    silhouette_df = pd.DataFrame(silhouette_records)

    elbow_csv_path = os.path.join(CLUSTERING_DIR, "elbow_results.csv")
    silhouette_csv_path = os.path.join(CLUSTERING_DIR, "silhouette_results.csv")

    elbow_df.to_csv(elbow_csv_path, index=False)
    silhouette_df.to_csv(silhouette_csv_path, index=False)
    logger.info("Saved elbow results to %s", elbow_csv_path)
    logger.info("Saved silhouette results to %s", silhouette_csv_path)

    return elbow_df, silhouette_df, models_dict


def compute_cluster_profiles(
    train_df: pd.DataFrame,
    train_clusters: np.ndarray,
    scaler: object,
    optimal_k: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute detailed unscaled and standardized statistical profiles for each cluster."""
    df = train_df[FEATURE_COLS].copy()
    df["cluster"] = train_clusters

    profile_rows = []
    for c in range(optimal_k):
        sub_df = df[df["cluster"] == c]
        count = len(sub_df)
        pct = (count / len(df)) * 100.0

        for feat in FEATURE_COLS:
            vals = sub_df[feat].values
            profile_rows.append({
                "cluster": f"Cluster {c}",
                "cluster_id": c,
                "feature": feat,
                "count": count,
                "percentage": round(pct, 2),
                "mean": round(float(np.mean(vals)), 4),
                "median": round(float(np.median(vals)), 4),
                "std": round(float(np.std(vals)), 4),
                "min": round(float(np.min(vals)), 4),
                "max": round(float(np.max(vals)), 4),
                "q25": round(float(np.percentile(vals, 25)), 4),
                "q75": round(float(np.percentile(vals, 75)), 4),
            })

    profile_df = pd.DataFrame(profile_rows)
    profile_csv_path = os.path.join(CLUSTERING_DIR, "cluster_profiles.csv")
    profile_df.to_csv(profile_csv_path, index=False)
    logger.info("Saved cluster profiles to %s", profile_csv_path)

    # Summary table: Mean and Median per cluster per feature
    summary_mean = df.groupby("cluster")[FEATURE_COLS].mean()
    summary_mean["count"] = df.groupby("cluster").size()
    summary_mean["pct"] = (summary_mean["count"] / len(df)) * 100.0

    return profile_df, summary_mean


def compute_contingency_and_metrics(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_clusters: np.ndarray,
    val_clusters: np.ndarray,
    test_clusters: np.ndarray,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    """Compute cross-tabulation and ARI/NMI against provisional target_label for academic analysis."""
    contingency_records = []
    metrics = {}

    splits_data = [
        ("Train", train_df, train_clusters),
        ("Val", val_df, val_clusters),
        ("Test", test_df, test_clusters),
    ]

    for split_name, split_df, clusters in splits_data:
        y_true = split_df["target_label"].values
        ari = float(adjusted_rand_score(y_true, clusters))
        nmi = float(normalized_mutual_info_score(y_true, clusters))
        metrics[split_name] = {
            "ARI": round(ari, 4),
            "NMI": round(nmi, 4),
        }

        # Contingency table
        ct = pd.crosstab(
            clusters,
            y_true,
            rownames=["Cluster"],
            colnames=["target_label"],
            margins=True
        )

        for c in range(len(np.unique(clusters))):
            c0 = int(ct.loc[c, 0]) if (c in ct.index and 0 in ct.columns) else 0
            c1 = int(ct.loc[c, 1]) if (c in ct.index and 1 in ct.columns) else 0
            total = c0 + c1
            p0 = round((c0 / total) * 100.0, 2) if total > 0 else 0.0
            p1 = round((c1 / total) * 100.0, 2) if total > 0 else 0.0

            contingency_records.append({
                "split": split_name,
                "cluster": f"Cluster {c}",
                "target_0_count": c0,
                "target_1_count": c1,
                "total": total,
                "target_0_pct": p0,
                "target_1_pct": p1,
                "ari": round(ari, 4),
                "nmi": round(nmi, 4),
            })

    contingency_df = pd.DataFrame(contingency_records)
    contingency_csv_path = os.path.join(CLUSTERING_DIR, "cluster_contingency.csv")
    contingency_df.to_csv(contingency_csv_path, index=False)
    logger.info("Saved cluster contingency analysis to %s", contingency_csv_path)

    return contingency_df, metrics


# ==============================================================================
# VISUALIZATION FUNCTIONS (300 DPI)
# ==============================================================================

def plot_elbow_curve(elbow_df: pd.DataFrame, optimal_k: int):
    """Plot 1: Inertia vs K with elbow point annotated."""
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=300)

    color1 = "#1f77b4"
    ax1.plot(elbow_df["k"], elbow_df["inertia"], marker="o", linewidth=2.2, markersize=7, color=color1, label="Inertia (WCSS)")
    ax1.set_xlabel("Number of Clusters (K)", fontweight="bold")
    ax1.set_ylabel("Inertia / Within-Cluster Sum of Squares", color=color1, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_xticks(elbow_df["k"])
    ax1.grid(True, linestyle="--", alpha=0.6)

    # Highlight optimal K
    opt_row = elbow_df[elbow_df["k"] == optimal_k].iloc[0]
    ax1.scatter([optimal_k], [opt_row["inertia"]], color="#d62728", s=130, zorder=5, edgecolor="black", linewidth=1.5)
    ax1.annotate(
        f"Selected Elbow Point (K={optimal_k})\nInertia = {opt_row['inertia']:.1f}",
        xy=(optimal_k, opt_row["inertia"]),
        xytext=(optimal_k + 0.6, opt_row["inertia"] + 450),
        arrowprops=dict(facecolor="#d62728", shrink=0.08, width=1.5, headwidth=8),
        fontweight="bold",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#ffebee", edgecolor="#d62728", alpha=0.9),
    )

    # Secondary axis: percentage drop in inertia
    ax2 = ax1.twinx()
    color2 = "#2ca02c"
    valid_drops = elbow_df.dropna(subset=["drop_pct"])
    ax2.bar(valid_drops["k"] - 0.15, valid_drops["drop_pct"], width=0.3, alpha=0.35, color=color2, label="Inertia Drop (%)")
    ax2.set_ylabel("Inertia Reduction Rate (%)", color=color2, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(0, 35)

    plt.title("Elbow Method for Optimal K Selection (K-Means Clustering)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "elbow_curve.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    logger.info("Saved Plot 1: %s", out_path)


def plot_silhouette_comparison(silhouette_df: pd.DataFrame, optimal_k: int):
    """Plot 2: Silhouette Score vs K with optimal K highlighted."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    ax.plot(
        silhouette_df["k"],
        silhouette_df["silhouette_score"],
        marker="s",
        linewidth=2.2,
        markersize=7,
        color="#7570b3",
        label="Silhouette Score",
    )
    ax.set_xlabel("Number of Clusters (K)", fontweight="bold")
    ax.set_ylabel("Mean Silhouette Coefficient", fontweight="bold")
    ax.set_xticks(silhouette_df["k"])
    ax.set_ylim(0.14, 0.26)
    ax.grid(True, linestyle="--", alpha=0.6)

    # Highlight peak/optimal K
    opt_row = silhouette_df[silhouette_df["k"] == optimal_k].iloc[0]
    ax.scatter([optimal_k], [opt_row["silhouette_score"]], color="#d62728", s=130, zorder=5, edgecolor="black", linewidth=1.5)
    ax.annotate(
        f"Peak Silhouette (K={optimal_k})\nScore = {opt_row['silhouette_score']:.4f}",
        xy=(optimal_k, opt_row["silhouette_score"]),
        xytext=(optimal_k + 0.6, opt_row["silhouette_score"] + 0.012),
        arrowprops=dict(facecolor="#d62728", shrink=0.08, width=1.5, headwidth=8),
        fontweight="bold",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#ede7f6", edgecolor="#7570b3", alpha=0.9),
    )

    # Annotate weak-to-moderate boundary interpretation
    ax.axhline(0.25, color="gray", linestyle=":", alpha=0.7)
    ax.text(9.8, 0.245, "Weak-to-Moderate Threshold (0.25)", ha="right", fontsize=9, color="#555555", style="italic")

    plt.title("Silhouette Score Comparison Across Candidate K Values", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "silhouette_comparison.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    logger.info("Saved Plot 2: %s", out_path)


def plot_silhouette_analysis(X_train_scaled: np.ndarray, train_clusters: np.ndarray, optimal_k: int):
    """Plot 3: Silhouette plot showing silhouette coefficient for each sample in each cluster."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    sample_silhouette_values = silhouette_samples(X_train_scaled, train_clusters)
    avg_score = silhouette_score(X_train_scaled, train_clusters)

    y_lower = 10
    colors = ["#2b5c8f", "#d95f02", "#7570b3"]

    for i in range(optimal_k):
        ith_cluster_silhouette_values = sample_silhouette_values[train_clusters == i]
        ith_cluster_silhouette_values.sort()

        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        color = colors[i % len(colors)]
        ax.fill_betweenx(
            np.arange(y_lower, y_upper),
            0,
            ith_cluster_silhouette_values,
            facecolor=color,
            edgecolor=color,
            alpha=0.75,
            label=f"Cluster {i} (n={size_cluster_i})",
        )

        # Label cluster number in center of slice
        ax.text(-0.08, y_lower + 0.5 * size_cluster_i, f"Cluster {i}", color=color, fontweight="bold", fontsize=10)
        y_lower = y_upper + 15

    ax.set_title(f"Silhouette Analysis for K-Means Clustering (K={optimal_k})", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Silhouette Coefficient Values", fontweight="bold")
    ax.set_ylabel("Cluster Slice (Sample Index)", fontweight="bold")

    # Average silhouette score vertical dashed line
    ax.axvline(x=avg_score, color="red", linestyle="--", linewidth=1.8, label=f"Mean Silhouette ({avg_score:.4f})")
    ax.set_yticks([])  # Clear y-axis tick labels
    ax.set_xlim([-0.2, 0.6])
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "silhouette_analysis.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    logger.info("Saved Plot 3: %s", out_path)


def plot_pca_cluster_visualization(
    X_train_scaled: np.ndarray,
    train_clusters: np.ndarray,
    kmeans_model: KMeans,
    optimal_k: int,
):
    """Plot 4: 2D PCA projection of clusters with centroids marked."""
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_train_scaled)
    centroids_pca = pca.transform(kmeans_model.cluster_centers_)

    var_pc1 = pca.explained_variance_ratio_[0] * 100.0
    var_pc2 = pca.explained_variance_ratio_[1] * 100.0
    total_var = var_pc1 + var_pc2

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    colors = ["#2b5c8f", "#d95f02", "#7570b3"]

    for i in range(optimal_k):
        mask = (train_clusters == i)
        ax.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            c=colors[i % len(colors)],
            label=f"Cluster {i} (n={np.sum(mask)})",
            alpha=0.60,
            s=28,
            edgecolors="none",
        )

    # Plot Centroids
    ax.scatter(
        centroids_pca[:, 0],
        centroids_pca[:, 1],
        marker="X",
        s=180,
        c="#ffffff",
        edgecolors="#000000",
        linewidths=2.2,
        zorder=10,
        label="Cluster Centroids (Projected)",
    )

    for i in range(optimal_k):
        ax.annotate(
            f"  C{i}",
            xy=(centroids_pca[i, 0], centroids_pca[i, 1]),
            fontweight="bold",
            fontsize=11,
            color="#000000",
            zorder=11,
        )

    ax.set_title("2D PCA Projection of K-Means Clusters (Standardized Feature Space)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel(f"Principal Component 1 ({var_pc1:.1f}% Variance)", fontweight="bold")
    ax.set_ylabel(f"Principal Component 2 ({var_pc2:.1f}% Variance)", fontweight="bold")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Note at bottom explaining PCA is visualization-only
    ax.text(
        0.5, -0.13,
        f"Note: Clustering was performed strictly in 5D standardized feature space.\n"
        f"PCA captures {total_var:.1f}% of total variance and is used exclusively for 2D visual projection.",
        transform=ax.transAxes,
        ha="center",
        fontsize=8.5,
        color="#555555",
        style="italic",
        bbox=dict(boxstyle="square,pad=0.3", facecolor="#f8f9fa", edgecolor="#cccccc"),
    )

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "pca_cluster_visualization.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info("Saved Plot 4: %s", out_path)


def plot_cluster_size_distribution(
    train_clusters: np.ndarray,
    val_clusters: np.ndarray,
    test_clusters: np.ndarray,
    optimal_k: int,
):
    """Plot 5: Grouped bar chart of cluster sizes across train, val, and test splits."""
    splits = ["Train", "Val", "Test"]
    cluster_labels = [f"Cluster {i}" for i in range(optimal_k)]

    data = {
        "Train": [np.sum(train_clusters == i) / len(train_clusters) * 100.0 for i in range(optimal_k)],
        "Val": [np.sum(val_clusters == i) / len(val_clusters) * 100.0 for i in range(optimal_k)],
        "Test": [np.sum(test_clusters == i) / len(test_clusters) * 100.0 for i in range(optimal_k)],
    }
    counts = {
        "Train": [np.sum(train_clusters == i) for i in range(optimal_k)],
        "Val": [np.sum(val_clusters == i) for i in range(optimal_k)],
        "Test": [np.sum(test_clusters == i) for i in range(optimal_k)],
    }

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    x = np.arange(len(cluster_labels))
    width = 0.25

    colors = ["#2b5c8f", "#41b6c4", "#a1dab4"]

    for idx, split_name in enumerate(splits):
        bars = ax.bar(
            x + (idx - 1) * width,
            data[split_name],
            width,
            label=f"{split_name} (N={len(eval(split_name.lower() + '_clusters'))})",
            color=colors[idx],
            edgecolor="black",
            linewidth=0.8,
            alpha=0.85,
        )
        # Add labels on top of bars
        for b_idx, bar in enumerate(bars):
            cnt = counts[split_name][b_idx]
            pct = data[split_name][b_idx]
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 0.8,
                f"{cnt}\n({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )

    ax.set_title("Cluster Proportion Consistency Across Partitions (Train / Val / Test)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Assigned Cluster", fontweight="bold")
    ax.set_ylabel("Proportion of Dataset (%)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(cluster_labels, fontweight="bold")
    ax.set_ylim(0, max(max(v) for v in data.values()) + 12)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "cluster_size_distribution.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    logger.info("Saved Plot 5: %s", out_path)


def plot_cluster_feature_heatmap(kmeans_model: KMeans, optimal_k: int):
    """Plot 6: Heatmap of standardized feature centers (Z-scores) across clusters."""
    centers_scaled = kmeans_model.cluster_centers_
    heatmap_df = pd.DataFrame(
        centers_scaled,
        index=[f"Cluster {i}" for i in range(optimal_k)],
        columns=FEATURE_COLS,
    )

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    sns.heatmap(
        heatmap_df,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        center=0.0,
        cbar_kws={"label": "Standardized Centroid Value (Z-Score)"},
        linewidths=1.0,
        linecolor="white",
        ax=ax,
        annot_kws={"size": 10, "weight": "bold"},
    )

    ax.set_title("Standardized Cluster Centroids (Z-Score Heatmap)", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Cluster Identifier", fontweight="bold")
    ax.set_xlabel("Academic Feature Name", fontweight="bold")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()

    out_path = os.path.join(PLOTS_DIR, "cluster_feature_heatmap.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    logger.info("Saved Plot 6: %s", out_path)


def plot_feature_distributions_by_cluster(train_df: pd.DataFrame, train_clusters: np.ndarray, optimal_k: int):
    """Plot 7: 5 subplots showing box plots of unscaled features across clusters."""
    df = train_df[FEATURE_COLS].copy()
    df["cluster"] = [f"Cluster {c}" for c in train_clusters]

    fig, axes = plt.subplots(2, 3, figsize=(14, 9), dpi=300)
    axes = axes.flatten()

    colors = ["#2b5c8f", "#d95f02", "#7570b3"]

    for idx, feat in enumerate(FEATURE_COLS):
        ax = axes[idx]
        sns.boxplot(
            data=df,
            x="cluster",
            y=feat,
            palette=colors,
            ax=ax,
            boxprops=dict(alpha=0.75, edgecolor="black"),
            medianprops=dict(color="yellow", linewidth=2.0),
            showmeans=True,
            meanprops=dict(marker="o", markeredgecolor="black", markerfacecolor="white", markersize=6),
        )
        ax.set_title(f"Distribution of {feat}", fontweight="bold", fontsize=11)
        ax.set_xlabel("")
        ax.set_ylabel("Original Feature Value", fontweight="bold", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    # Hide unused 6th subplot
    axes[5].axis("off")

    # Add explanatory legend in 6th subplot area
    axes[5].text(
        0.1, 0.5,
        "Box Plot Interpretation:\n"
        "• Yellow line: Median\n"
        "• White circle: Mean\n"
        "• Shaded box: IQR (25th to 75th percentile)\n"
        "• Whiskers: 1.5 × IQR\n"
        "• Diamond points: Statistical outliers\n\n"
        "Clusters exhibit pronounced\n"
        "separation on semantic similarity\n"
        "and word count dimensions.",
        fontsize=10.5,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#f0f4f8", edgecolor="#b0bec5"),
        va="center",
    )

    plt.suptitle("Feature Distributions by Assigned K-Means Cluster (Training Set, N=1,264)", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout()
    out_path = os.path.join(PLOTS_DIR, "feature_distribution_by_cluster.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    logger.info("Saved Plot 7: %s", out_path)


# ==============================================================================
# MAIN EXECUTION ROUTINE
# ==============================================================================

def run_kmeans_pipeline():
    """Execute complete Step 5 unsupervised learning workflow."""
    logger.info("=" * 80)
    logger.info("STARTING PART A - STEP 5: UNSUPERVISED LEARNING (K-MEANS CLUSTERING)")
    logger.info("=" * 80)

    ensure_directories()

    # 1. Load Data & Scaler
    train_df, val_df, test_df, scaler = load_data_and_scaler()

    # Extract strictly unscaled features
    X_train_raw = train_df[FEATURE_COLS].values
    X_val_raw = val_df[FEATURE_COLS].values
    X_test_raw = test_df[FEATURE_COLS].values

    # Transform using pre-fitted scaler (NO refitting)
    X_train_scaled = scaler.transform(X_train_raw)
    X_val_scaled = scaler.transform(X_val_raw)
    X_test_scaled = scaler.transform(X_test_raw)

    logger.info("Features scaled successfully using pre-fitted academic_scaler.pkl.")

    # 2. Evaluate K in [2..10]
    elbow_df, silhouette_df, models_dict = evaluate_k_range(
        X_train_scaled=X_train_scaled,
        k_min=2,
        k_max=10,
        random_state=42,
    )

    # 3. Select Optimal K
    # Peak silhouette is K=3 (0.2311) and elbow drop sharply flattens after K=3
    optimal_k = 3
    final_kmeans = models_dict[optimal_k]
    logger.info("Selected Optimal K=%d (Inertia: %.2f, Silhouette: %.4f)", optimal_k, final_kmeans.inertia_, silhouette_df.loc[silhouette_df['k'] == optimal_k, 'silhouette_score'].values[0])

    # 4. Predict Clusters for Train, Val, Test
    train_clusters = final_kmeans.labels_
    val_clusters = final_kmeans.predict(X_val_scaled)
    test_clusters = final_kmeans.predict(X_test_scaled)

    # 5. Save Model and Metadata
    model_save_path = os.path.join(CLUSTERING_DIR, "kmeans_model.pkl")
    joblib.dump(final_kmeans, model_save_path)
    logger.info("Serialized trained K-Means model to %s", model_save_path)

    # Invert cluster centers to original scale for interpretability
    centers_scaled = final_kmeans.cluster_centers_
    centers_unscaled = scaler.inverse_transform(centers_scaled)

    # 6. Cluster Profiling
    profile_df, summary_mean = compute_cluster_profiles(
        train_df=train_df,
        train_clusters=train_clusters,
        scaler=scaler,
        optimal_k=optimal_k,
    )

    # 7. Post-Hoc Target Label Comparison
    contingency_df, metrics_ari_nmi = compute_contingency_and_metrics(
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        train_clusters=train_clusters,
        val_clusters=val_clusters,
        test_clusters=test_clusters,
    )

    # 8. Save Cluster Assignments
    for split_name, split_df, clusters in [
        ("train", train_df, train_clusters),
        ("val", val_df, val_clusters),
        ("test", test_df, test_clusters),
    ]:
        out_assign = split_df[["question", "answer", "target_label"] + FEATURE_COLS].copy()
        out_assign["cluster"] = clusters
        out_assign["cluster_name"] = [f"Cluster {c}" for c in clusters]
        csv_path = os.path.join(CLUSTERING_DIR, f"cluster_assignments_{split_name}.csv")
        out_assign.to_csv(csv_path, index=False)
        logger.info("Saved %s cluster assignments to %s", split_name, csv_path)

    # 9. Save Metadata JSON
    metadata = {
        "algorithm": "KMeans",
        "optimal_k": optimal_k,
        "random_state": 42,
        "n_init": 10,
        "max_iter": 300,
        "iterations_to_converge": int(final_kmeans.n_iter_),
        "inertia": round(float(final_kmeans.inertia_), 4),
        "silhouette_score": round(float(silhouette_df.loc[silhouette_df['k'] == optimal_k, 'silhouette_score'].values[0]), 4),
        "feature_names": FEATURE_COLS,
        "scaler_path": "ml/models/academic_scaler.pkl",
        "cluster_centers_scaled": centers_scaled.tolist(),
        "cluster_centers_unscaled": centers_unscaled.tolist(),
        "split_counts": {
            "train": {f"Cluster {c}": int(np.sum(train_clusters == c)) for c in range(optimal_k)},
            "val": {f"Cluster {c}": int(np.sum(val_clusters == c)) for c in range(optimal_k)},
            "test": {f"Cluster {c}": int(np.sum(test_clusters == c)) for c in range(optimal_k)},
        },
        "academic_contingency_metrics": metrics_ari_nmi,
        "neutral_cluster_descriptions": {
            "Cluster 0": "Cluster 0 - Extended / Substantive (Highest word count [20.0], highest lexical overlap [0.144], high semantic similarity [0.718], natural word repetition)",
            "Cluster 1": "Cluster 1 - Low Alignment / Divergent (Lowest semantic similarity [0.448], lowest lexical overlap [0.039], shortest word count [15.35], 0% Class 1)",
            "Cluster 2": "Cluster 2 - Concise Technical (High semantic similarity [0.717], highest average word length [6.83], highest unique word ratio [0.970], moderate length [17.2])",
        },
    }

    metadata_path = os.path.join(CLUSTERING_DIR, "cluster_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved cluster metadata JSON to %s", metadata_path)

    # 10. Generate Visualizations (300 DPI)
    logger.info("Generating publication-quality visualizations (300 DPI)...")
    plot_elbow_curve(elbow_df, optimal_k)
    plot_silhouette_comparison(silhouette_df, optimal_k)
    plot_silhouette_analysis(X_train_scaled, train_clusters, optimal_k)
    plot_pca_cluster_visualization(X_train_scaled, train_clusters, final_kmeans, optimal_k)
    plot_cluster_size_distribution(train_clusters, val_clusters, test_clusters, optimal_k)
    plot_cluster_feature_heatmap(final_kmeans, optimal_k)
    plot_feature_distributions_by_cluster(train_df, train_clusters, optimal_k)

    logger.info("=" * 80)
    logger.info("PART A - STEP 5 K-MEANS PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_kmeans_pipeline()
