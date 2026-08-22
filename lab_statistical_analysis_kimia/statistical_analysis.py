"""
Statistical Analysis — Marketing Channel ROI Comparison Lab
==============================================================
Part 2: Pairwise comparisons (t-tests for continuous metrics, Fisher's exact
         test for binary/conversion outcomes)
Part 3: Multiple comparisons correction (Bonferroni, Benjamini-Hochberg FDR)

Run data_exploration.py first — this script reads data/marketing_data_clean.csv.
"""

import itertools
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind, fisher_exact, false_discovery_control
import matplotlib.pyplot as plt

from data_exploration import COLUMN_MAP as cm

ALPHA = 0.05


def cohens_d(a, b):
    pooled_std = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    if pooled_std == 0:
        return np.nan
    return (np.mean(b) - np.mean(a)) / pooled_std


def interpret_effect(d):
    d = abs(d)
    if pd.isna(d):
        return "n/a"
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


def pairwise_ttests(df, metric_col, group_col):
    results = []
    groups = sorted(df[group_col].dropna().unique())
    for g_a, g_b in itertools.combinations(groups, 2):
        a = df.loc[df[group_col] == g_a, metric_col].dropna()
        a = a[np.isfinite(a)]
        b = df.loc[df[group_col] == g_b, metric_col].dropna()
        b = b[np.isfinite(b)]
        if len(a) < 2 or len(b) < 2:
            continue
        t_stat, p_val = ttest_ind(a, b, equal_var=False)
        mean_a, mean_b = a.mean(), b.mean()
        diff = mean_b - mean_a
        pct_diff = (diff / mean_a * 100) if mean_a != 0 else np.nan
        d = cohens_d(a, b)
        results.append({
            "group_a": g_a, "group_b": g_b,
            "mean_a": mean_a, "mean_b": mean_b,
            "diff": diff, "pct_diff": pct_diff,
            "t_stat": t_stat, "p_value": p_val,
            "cohens_d": d, "effect_size": interpret_effect(d),
            "significant_uncorrected": p_val < ALPHA,
        })
    return pd.DataFrame(results)


def pairwise_fisher(df, group_col, conversions_col, attempts_col):
    agg = df.groupby(group_col).agg(
        conversions=(conversions_col, "sum"),
        attempts=(attempts_col, "sum"),
    ).reset_index()
    agg["non_conversions"] = agg["attempts"] - agg["conversions"]
    agg["rate"] = agg["conversions"] / agg["attempts"]
    print("\n=== Fisher's exact — group totals ===")
    print(agg)

    results = []
    groups = agg[group_col].tolist()
    for g_a, g_b in itertools.combinations(groups, 2):
        row_a = agg[agg[group_col] == g_a].iloc[0]
        row_b = agg[agg[group_col] == g_b].iloc[0]
        table = [[row_a["conversions"], row_a["non_conversions"]],
                 [row_b["conversions"], row_b["non_conversions"]]]
        odds_ratio, p_val = fisher_exact(table, alternative="two-sided")
        diff = row_b["rate"] - row_a["rate"]
        pct_diff = (diff / row_a["rate"] * 100) if row_a["rate"] != 0 else np.nan
        results.append({
            "group_a": g_a, "group_b": g_b,
            "rate_a": row_a["rate"], "rate_b": row_b["rate"],
            "diff": diff, "pct_diff": pct_diff,
            "odds_ratio": odds_ratio, "p_value": p_val,
            "significant_uncorrected": p_val < ALPHA,
        })
    return agg, pd.DataFrame(results)


def apply_corrections(results_df, label):
    n = len(results_df)
    if n == 0:
        print(f"\nNo comparisons available for {label} correction.")
        return results_df
    alpha_bonf = ALPHA / n
    results_df = results_df.copy()
    results_df["significant_bonferroni"] = results_df["p_value"] < alpha_bonf
    results_df["p_value_fdr"] = false_discovery_control(results_df["p_value"].values, method="bh")
    results_df["significant_fdr"] = results_df["p_value_fdr"] < ALPHA

    n_uncorrected = results_df["significant_uncorrected"].sum()
    n_bonf = results_df["significant_bonferroni"].sum()
    n_fdr = results_df["significant_fdr"].sum()

    print(f"\n=== {label}: {n} comparisons ===")
    print(f"Expected false positives at alpha=0.05 by chance alone: {n * ALPHA:.2f}")
    print(f"Bonferroni-adjusted alpha: {alpha_bonf:.6f}")
    print(f"Significant (uncorrected):  {n_uncorrected}")
    print(f"Significant (Bonferroni):   {n_bonf}")
    print(f"Significant (FDR/BH):       {n_fdr}")

    return results_df


def plot_pvalue_heatmap(results_df, metric_name, outdir="outputs"):
    import os
    os.makedirs(outdir, exist_ok=True)
    groups = sorted(set(results_df["group_a"]) | set(results_df["group_b"]))
    matrix = pd.DataFrame(1.0, index=groups, columns=groups)
    for _, row in results_df.iterrows():
        matrix.loc[row["group_a"], row["group_b"]] = row["p_value"]
        matrix.loc[row["group_b"], row["group_a"]] = row["p_value"]
    mat_values = matrix.values.copy()
    np.fill_diagonal(mat_values, 1.0)

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(mat_values, cmap="RdYlGn_r", vmin=0, vmax=1)
    ax.set_xticks(range(len(groups)))
    ax.set_yticks(range(len(groups)))
    ax.set_xticklabels(groups, rotation=45, ha="right")
    ax.set_yticklabels(groups)
    for i in range(len(groups)):
        for j in range(len(groups)):
            ax.text(j, i, f"{mat_values[i, j]:.3f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="p-value")
    ax.set_title(f"Pairwise p-value heatmap — {metric_name}")
    plt.tight_layout()
    fname = f"{outdir}/metric_comparison_heatmap.png"
    plt.savefig(fname, dpi=150)
    print(f"Saved {fname}")
    plt.close()


def plot_correction_comparison(cpa_res, cr_res, outdir="outputs"):
    import os
    os.makedirs(outdir, exist_ok=True)
    labels = ["Uncorrected", "Bonferroni", "FDR (BH)"]
    cpa_counts = [cpa_res["significant_uncorrected"].sum(),
                  cpa_res["significant_bonferroni"].sum(),
                  cpa_res["significant_fdr"].sum()] if len(cpa_res) else [0, 0, 0]
    cr_counts = [cr_res["significant_uncorrected"].sum(),
                 cr_res["significant_bonferroni"].sum(),
                 cr_res["significant_fdr"].sum()] if len(cr_res) else [0, 0, 0]

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x - width / 2, cpa_counts, width, label="CPA comparisons")
    ax.bar(x + width / 2, cr_counts, width, label="Conversion rate comparisons")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("# significant comparisons")
    ax.set_title("Effect of multiple comparisons correction")
    ax.legend()
    plt.tight_layout()
    fname = f"{outdir}/correction_comparison.png"
    plt.savefig(fname, dpi=150)
    print(f"Saved {fname}")
    plt.close()


def plot_rate_comparison(agg_df, group_col, outdir="outputs"):
    import os
    os.makedirs(outdir, exist_ok=True)
    agg_sorted = agg_df.sort_values("rate")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(agg_sorted[group_col].astype(str), agg_sorted["rate"] * 100)
    for bar, rate in zip(bars, agg_sorted["rate"]):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                 f" {rate*100:.2f}%", va="center", fontsize=9)
    ax.set_xlabel("Conversion rate (%)")
    ax.set_title("Conversion rate by channel")
    plt.tight_layout()
    fname = f"{outdir}/rate_comparison.png"
    plt.savefig(fname, dpi=150)
    print(f"Saved {fname}")
    plt.close()


def main():
    df = pd.read_csv("data/marketing_data_clean.csv")
    channel_col = cm["channel"]

    # --- t-tests on CPA (using acquisition_cost as-is; see README for caveat) ---
    cpa_results = pairwise_ttests(df, cm["acquisition_cost"], channel_col)
    print("\n=== CPA pairwise t-test results ===")
    print(cpa_results.to_string(index=False))
    cpa_results = apply_corrections(cpa_results, "CPA (Acquisition_Cost) t-tests")
    if len(cpa_results):
        plot_pvalue_heatmap(cpa_results, "Acquisition Cost")

    # --- t-tests on conversion rate as a continuous metric ---
    cr_ttest_results = pairwise_ttests(df, cm["conversion_rate"], channel_col)
    print("\n=== Conversion rate pairwise t-test results ===")
    print(cr_ttest_results.to_string(index=False))

    # --- Fisher's exact on conversions (binary) vs. clicks (attempts) ---
    if "conversions_est" in df.columns:
        agg, fisher_results = pairwise_fisher(df, channel_col, "conversions_est", cm["clicks"])
        print("\n=== Fisher's exact results ===")
        print(fisher_results.to_string(index=False))
        fisher_results = apply_corrections(fisher_results, "Conversion rate Fisher's exact tests")
        plot_rate_comparison(agg, channel_col)
    else:
        fisher_results = pd.DataFrame()
        print("\nSkipping Fisher's exact test: 'conversions_est' not available "
              "(needs Clicks + Conversion_Rate columns).")

    plot_correction_comparison(cpa_results, fisher_results if len(fisher_results) else cr_ttest_results)

    cpa_results.to_csv("data/cpa_pairwise_results.csv", index=False)
    fisher_results.to_csv("data/conversion_pairwise_results.csv", index=False)
    print("\n=== Statistical analysis complete ===")
    print("Saved: data/cpa_pairwise_results.csv, data/conversion_pairwise_results.csv")


if __name__ == "__main__":
    main()
