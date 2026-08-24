"""
Parts 2-3: Pairwise Group Comparisons + Multiple Comparisons Correction
Marketing Channel Budget Allocation Lab
"""

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, fisher_exact, false_discovery_control

plt.style.use("seaborn-v0_8-whitegrid")
ALPHA = 0.05

df = pd.read_csv("data/marketing_data.csv")
channels = sorted(df["Channel"].unique())
print("Channels:", channels)

# ---------------------------------------------------------------------------
# Step 4: t-tests on continuous metrics (CPA and ROI used as primary; also Conversion_Rate)
# ---------------------------------------------------------------------------
def cohens_d(a, b):
    pooled_std = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return (np.mean(b) - np.mean(a)) / pooled_std


def interpret_d(d):
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"


def pairwise_ttests(data, metric):
    rows = []
    clean = data[["Channel", metric]].replace([np.inf, -np.inf], np.nan).dropna()
    for a, b in itertools.combinations(channels, 2):
        va = clean.loc[clean["Channel"] == a, metric].values
        vb = clean.loc[clean["Channel"] == b, metric].values
        t_stat, p_val = ttest_ind(va, vb, equal_var=False)
        mean_a, mean_b = va.mean(), vb.mean()
        diff = mean_b - mean_a
        pct_diff = diff / mean_a * 100 if mean_a != 0 else np.nan
        d = cohens_d(va, vb)
        rows.append({
            "metric": metric, "group_a": a, "group_b": b,
            "mean_a": round(mean_a, 3), "mean_b": round(mean_b, 3),
            "diff_b_minus_a": round(diff, 3), "pct_diff": round(pct_diff, 2),
            "t_stat": round(t_stat, 3), "p_value": p_val,
            "cohens_d": round(d, 3), "effect_size": interpret_d(d),
            "significant_uncorrected": p_val < ALPHA,
        })
    return pd.DataFrame(rows)


cpa_results = pairwise_ttests(df, "CPA")
roi_results = pairwise_ttests(df, "ROI")

print(f"\nCPA comparisons: {len(cpa_results)} total, "
      f"{cpa_results['significant_uncorrected'].sum()} significant at alpha=0.05 (uncorrected)")
print(f"ROI comparisons: {len(roi_results)} total, "
      f"{roi_results['significant_uncorrected'].sum()} significant at alpha=0.05 (uncorrected)")

cpa_results.to_csv("outputs/ttest_cpa_results.csv", index=False)
roi_results.to_csv("outputs/ttest_roi_results.csv", index=False)

print("\nCPA t-test results:\n", cpa_results.to_string(index=False))

# --- p-value heatmap for CPA ---
def pvalue_heatmap(results, channels, title, fname):
    n = len(channels)
    mat = np.ones((n, n))
    idx = {c: i for i, c in enumerate(channels)}
    for _, r in results.iterrows():
        i, j = idx[r["group_a"]], idx[r["group_b"]]
        mat[i, j] = r["p_value"]
        mat[j, i] = r["p_value"]
    np.fill_diagonal(mat, 1.0)

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(mat, cmap="RdYlGn_r", vmin=0, vmax=0.1)
    ax.set_xticks(range(n)); ax.set_xticklabels(channels, rotation=45, ha="right")
    ax.set_yticks(range(n)); ax.set_yticklabels(channels)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{mat[i, j]:.3f}", ha="center", va="center", fontsize=8)
    ax.set_title(title)
    fig.colorbar(im, label="p-value")
    plt.tight_layout()
    plt.savefig(fname, dpi=150)
    plt.close()


pvalue_heatmap(cpa_results, channels, "CPA Pairwise Comparison p-values", "outputs/metric_comparison_heatmap_cpa.png")
pvalue_heatmap(roi_results, channels, "ROI Pairwise Comparison p-values", "outputs/metric_comparison_heatmap_roi.png")
print("Saved p-value heatmaps.")

# ---------------------------------------------------------------------------
# Step 5: Fisher's exact test on conversion outcomes
# Attempts = Clicks, "successes" = Conversions (derived in Part 1)
# ---------------------------------------------------------------------------
agg = df.groupby("Channel").agg(conversions=("Conversions", "sum"), attempts=("Clicks", "sum"))
agg["non_conversions"] = agg["attempts"] - agg["conversions"]
agg["conv_rate_%"] = (agg["conversions"] / agg["attempts"] * 100).round(3)
print("\nConversion summary by channel:\n", agg)
agg.to_csv("outputs/conversion_summary.csv")

fisher_rows = []
for a, b in itertools.combinations(channels, 2):
    conv_a, non_a = agg.loc[a, "conversions"], agg.loc[a, "non_conversions"]
    conv_b, non_b = agg.loc[b, "conversions"], agg.loc[b, "non_conversions"]
    table = [[conv_a, non_a], [conv_b, non_b]]
    odds_ratio, p_val = fisher_exact(table, alternative="two-sided")
    rate_a = conv_a / (conv_a + non_a)
    rate_b = conv_b / (conv_b + non_b)
    diff = rate_b - rate_a
    fisher_rows.append({
        "group_a": a, "group_b": b,
        "conversions_a": conv_a, "attempts_a": conv_a + non_a, "rate_a_%": round(rate_a * 100, 3),
        "conversions_b": conv_b, "attempts_b": conv_b + non_b, "rate_b_%": round(rate_b * 100, 3),
        "diff_pct_pts": round(diff * 100, 3), "odds_ratio": round(odds_ratio, 4),
        "p_value": p_val, "significant_uncorrected": p_val < ALPHA,
    })

fisher_results = pd.DataFrame(fisher_rows)
print(f"\nFisher's exact comparisons: {len(fisher_results)} total, "
      f"{fisher_results['significant_uncorrected'].sum()} significant at alpha=0.05 (uncorrected)")
print(fisher_results.to_string(index=False))
fisher_results.to_csv("outputs/fisher_exact_results.csv", index=False)

# --- rate comparison bar chart ---
fig, ax = plt.subplots(figsize=(8, 5))
sorted_agg = agg.sort_values("conv_rate_%")
bars = ax.barh(sorted_agg.index, sorted_agg["conv_rate_%"], color="#4C72B0")
for bar, val in zip(bars, sorted_agg["conv_rate_%"]):
    ax.text(val + 0.02, bar.get_y() + bar.get_height() / 2, f"{val:.2f}%", va="center", fontsize=9)
ax.set_xlabel("Conversion Rate (%)")
ax.set_title("Conversion Rate by Channel (clicks -> conversions)")
plt.tight_layout()
plt.savefig("outputs/rate_comparison.png", dpi=150)
plt.close()
print("Saved outputs/rate_comparison.png")

# ---------------------------------------------------------------------------
# Step 6: Multiple comparisons correction
# ---------------------------------------------------------------------------
n_cpa = len(cpa_results)
n_roi = len(roi_results)
n_fisher = len(fisher_results)
total_comparisons = n_cpa + n_roi + n_fisher
expected_false_positives = total_comparisons * ALPHA
print(f"\n--- Multiple comparisons problem ---")
print(f"Total comparisons made: {total_comparisons} (CPA={n_cpa}, ROI={n_roi}, Fisher={n_fisher})")
print(f"Expected false positives at alpha=0.05 by chance alone: {expected_false_positives:.2f}")

def apply_bonferroni(results, n_tests):
    alpha_bonf = ALPHA / n_tests
    results = results.copy()
    results["significant_bonferroni"] = results["p_value"] < alpha_bonf
    return results, alpha_bonf


def apply_fdr(results):
    results = results.copy()
    adj = false_discovery_control(results["p_value"].values, method="bh")
    results["p_value_fdr"] = adj
    results["significant_fdr"] = adj < ALPHA
    return results


cpa_results, alpha_bonf_cpa = apply_bonferroni(cpa_results, n_cpa)
cpa_results = apply_fdr(cpa_results)

roi_results, alpha_bonf_roi = apply_bonferroni(roi_results, n_roi)
roi_results = apply_fdr(roi_results)

fisher_results, alpha_bonf_fisher = apply_bonferroni(fisher_results, n_fisher)
fisher_results = apply_fdr(fisher_results)

cpa_results.to_csv("outputs/ttest_cpa_results.csv", index=False)
roi_results.to_csv("outputs/ttest_roi_results.csv", index=False)
fisher_results.to_csv("outputs/fisher_exact_results.csv", index=False)

print(f"\nCPA: alpha_bonferroni={alpha_bonf_cpa:.6f} | "
      f"{cpa_results['significant_bonferroni'].sum()} sig. after Bonferroni | "
      f"{cpa_results['significant_fdr'].sum()} sig. after FDR")
print(f"ROI: alpha_bonferroni={alpha_bonf_roi:.6f} | "
      f"{roi_results['significant_bonferroni'].sum()} sig. after Bonferroni | "
      f"{roi_results['significant_fdr'].sum()} sig. after FDR")
print(f"Fisher (conv. rate): alpha_bonferroni={alpha_bonf_fisher:.6f} | "
      f"{fisher_results['significant_bonferroni'].sum()} sig. after Bonferroni | "
      f"{fisher_results['significant_fdr'].sum()} sig. after FDR")

print("\nCPA pairs still significant after FDR:")
print(cpa_results.loc[cpa_results["significant_fdr"], ["group_a", "group_b", "p_value", "p_value_fdr", "cohens_d"]])

print("\nROI pairs still significant after FDR:")
print(roi_results.loc[roi_results["significant_fdr"], ["group_a", "group_b", "p_value", "p_value_fdr", "cohens_d"]])

print("\nConversion-rate pairs still significant after FDR:")
print(fisher_results.loc[fisher_results["significant_fdr"], ["group_a", "group_b", "p_value", "p_value_fdr", "diff_pct_pts"]])

# --- correction comparison table + chart ---
def correction_summary(name, results):
    return {
        "test": name,
        "uncorrected": int(results["significant_uncorrected"].sum()),
        "bonferroni": int(results["significant_bonferroni"].sum()),
        "fdr_bh": int(results["significant_fdr"].sum()),
    }


correction_table = pd.DataFrame([
    correction_summary("CPA (t-test)", cpa_results),
    correction_summary("ROI (t-test)", roi_results),
    correction_summary("Conversion rate (Fisher)", fisher_results),
])
print("\nCorrection method comparison:\n", correction_table)
correction_table.to_csv("outputs/correction_comparison_table.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(correction_table))
w = 0.25
ax.bar(x - w, correction_table["uncorrected"], width=w, label="Uncorrected", color="#C44E52")
ax.bar(x, correction_table["bonferroni"], width=w, label="Bonferroni", color="#4C72B0")
ax.bar(x + w, correction_table["fdr_bh"], width=w, label="FDR (BH)", color="#55A868")
ax.set_xticks(x); ax.set_xticklabels(correction_table["test"])
ax.set_ylabel("Number of significant comparisons")
ax.set_title("Effect of Multiple Comparisons Correction")
ax.legend()
plt.tight_layout()
plt.savefig("outputs/correction_comparison.png", dpi=150)
plt.close()
print("Saved outputs/correction_comparison.png")

print("\n=== Parts 2-3 complete ===")
