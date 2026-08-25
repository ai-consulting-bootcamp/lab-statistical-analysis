"""
statistical_analysis.py
Part 2: Pairwise group comparisons (t-tests, Fisher's exact test, Cohen's d)
Part 3: Multiple comparisons correction (Bonferroni, Benjamini-Hochberg FDR)
"""

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import fisher_exact, false_discovery_control

plt.style.use("seaborn-v0_8-whitegrid")
ALPHA = 0.05

df = pd.read_csv("marketing_data.csv")
channels = sorted(df["Marketing_Channel"].unique())
print("Channels:", channels)

# =================================================================
# STEP 4: t-tests on CPA (continuous metric)
# =================================================================
def cohens_d(a, b):
    pooled_std = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return (np.mean(b) - np.mean(a)) / pooled_std

def interpret_d(d):
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    elif ad < 0.5:
        return "small"
    elif ad < 0.8:
        return "medium"
    else:
        return "large"

cpa_clean = df[["Marketing_Channel", "CPA"]].replace([np.inf, -np.inf], np.nan).dropna()

ttest_results = []
for a, b in itertools.combinations(channels, 2):
    va = cpa_clean.loc[cpa_clean.Marketing_Channel == a, "CPA"].values
    vb = cpa_clean.loc[cpa_clean.Marketing_Channel == b, "CPA"].values
    t_stat, p_val = stats.ttest_ind(va, vb, equal_var=False)
    mean_a, mean_b = va.mean(), vb.mean()
    diff = mean_b - mean_a
    pct_diff = diff / mean_a * 100
    d = cohens_d(va, vb)
    ttest_results.append({
        "group_a": a, "group_b": b,
        "mean_a": mean_a, "mean_b": mean_b,
        "diff_b_minus_a": diff, "pct_diff": pct_diff,
        "t_stat": t_stat, "p_value": p_val,
        "cohens_d": d, "effect_size": interpret_d(d),
        "significant_uncorrected": p_val < ALPHA,
        "n_a": len(va), "n_b": len(vb),
    })

ttest_df = pd.DataFrame(ttest_results)
print("\n=== CPA pairwise t-tests ===")
for _, r in ttest_df.iterrows():
    print(f"{r.group_a} vs {r.group_b}: mean {r.mean_a:.2f} vs {r.mean_b:.2f} "
          f"(diff {r.diff_b_minus_a:+.2f}, {r.pct_diff:+.1f}%), "
          f"t={r.t_stat:.3f}, p={r.p_value:.4f}, d={r.cohens_d:.3f} ({r.effect_size}), "
          f"{'SIG' if r.significant_uncorrected else 'ns'} @ α=0.05")

n_sig_uncorrected_cpa = ttest_df["significant_uncorrected"].sum()
print(f"\n{n_sig_uncorrected_cpa}/{len(ttest_df)} CPA comparisons significant at uncorrected α=0.05")

# ---- heatmap of CPA p-values ----
pmat = pd.DataFrame(np.ones((len(channels), len(channels))), index=channels, columns=channels)
for _, r in ttest_df.iterrows():
    pmat.loc[r.group_a, r.group_b] = r.p_value
    pmat.loc[r.group_b, r.group_a] = r.p_value

fig, ax = plt.subplots(figsize=(6.5, 5.5))
im = ax.imshow(pmat.values, cmap="RdYlGn_r", vmin=0, vmax=1)
ax.set_xticks(range(len(channels))); ax.set_xticklabels(channels, rotation=30, ha="right")
ax.set_yticks(range(len(channels))); ax.set_yticklabels(channels)
for i in range(len(channels)):
    for j in range(len(channels)):
        ax.text(j, i, f"{pmat.values[i, j]:.3f}", ha="center", va="center", fontsize=9,
                color="white" if pmat.values[i, j] < 0.3 else "black")
plt.colorbar(im, label="p-value")
ax.set_title("CPA pairwise comparison: p-value heatmap")
plt.tight_layout()
plt.savefig("output/images/metric_comparison_heatmap.png", dpi=150)
plt.close()
print("Saved output/images/metric_comparison_heatmap.png")

# =================================================================
# STEP 5: Fisher's exact test on conversion rate (binary outcome)
# =================================================================
binom = df.groupby("Marketing_Channel").agg(
    conversions=("Conversions", "sum"),
    attempts=("Clicks", "sum"),
).reset_index()
binom["non_conversions"] = binom["attempts"] - binom["conversions"]
binom["conversion_rate"] = binom["conversions"] / binom["attempts"]
print("\n=== Conversions / attempts summary ===")
print(binom.round(4).to_string(index=False))

fisher_results = []
for a, b in itertools.combinations(channels, 2):
    ra = binom[binom.Marketing_Channel == a].iloc[0]
    rb = binom[binom.Marketing_Channel == b].iloc[0]
    table = [[ra.conversions, ra.non_conversions],
             [rb.conversions, rb.non_conversions]]
    odds_ratio, p_val = fisher_exact(table, alternative="two-sided")
    rate_a, rate_b = ra.conversion_rate, rb.conversion_rate
    diff = rate_b - rate_a
    pct_diff = diff / rate_a * 100
    fisher_results.append({
        "group_a": a, "group_b": b,
        "conv_a": int(ra.conversions), "attempts_a": int(ra.attempts), "rate_a": rate_a,
        "conv_b": int(rb.conversions), "attempts_b": int(rb.attempts), "rate_b": rate_b,
        "diff": diff, "pct_diff": pct_diff,
        "odds_ratio": odds_ratio, "p_value": p_val,
        "significant_uncorrected": p_val < ALPHA,
    })

fisher_df = pd.DataFrame(fisher_results)
print("\n=== Conversion rate pairwise Fisher's exact tests ===")
for _, r in fisher_df.iterrows():
    print(f"{r.group_a} vs {r.group_b}: rate {r.rate_a:.4f} vs {r.rate_b:.4f} "
          f"(diff {r["diff"]:+.4f}, {r.pct_diff:+.1f}%), OR={r.odds_ratio:.3f}, "
          f"p={r.p_value:.2e}, {'SIG' if r.significant_uncorrected else 'ns'} @ α=0.05")

n_sig_uncorrected_fisher = fisher_df["significant_uncorrected"].sum()
print(f"\n{n_sig_uncorrected_fisher}/{len(fisher_df)} conversion-rate comparisons "
      f"significant at uncorrected α=0.05")

# ---- rate comparison bar chart ----
fig, ax = plt.subplots(figsize=(7, 4.5))
b = binom.sort_values("conversion_rate", ascending=False)
bars = ax.barh(b["Marketing_Channel"], b["conversion_rate"], color="#4C72B0")
for bar, v in zip(bars, b["conversion_rate"]):
    ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f" {v:.2%}",
            va="center", fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("Conversion rate (conversions / clicks)")
ax.set_title("Conversion rate by channel")
plt.tight_layout()
plt.savefig("output/images/rate_comparison.png", dpi=150)
plt.close()
print("Saved output/images/rate_comparison.png")

# =================================================================
# STEP 6: Multiple comparisons correction
# =================================================================
n_cpa = len(ttest_df)
n_fisher = len(fisher_df)
total_comparisons = n_cpa + n_fisher
expected_false_positives = total_comparisons * ALPHA
print(f"\n=== Multiple comparisons problem ===")
print(f"Total comparisons: {total_comparisons} ({n_cpa} CPA + {n_fisher} conversion-rate)")
print(f"Expected false positives by chance at α=0.05: {expected_false_positives:.2f}")

# ---- Bonferroni ----
alpha_bonf_cpa = ALPHA / n_cpa
alpha_bonf_fisher = ALPHA / n_fisher
ttest_df["significant_bonferroni"] = ttest_df["p_value"] < alpha_bonf_cpa
fisher_df["significant_bonferroni"] = fisher_df["p_value"] < alpha_bonf_fisher

print(f"\nBonferroni-adjusted alpha (CPA, n={n_cpa}): {alpha_bonf_cpa:.5f}")
print(f"CPA comparisons significant after Bonferroni: {ttest_df['significant_bonferroni'].sum()}")
print(f"Bonferroni-adjusted alpha (conversion rate, n={n_fisher}): {alpha_bonf_fisher:.5f}")
print(f"Conversion-rate comparisons significant after Bonferroni: {fisher_df['significant_bonferroni'].sum()}")

sig_bonf_cpa = ttest_df[ttest_df.significant_bonferroni]
sig_bonf_fisher = fisher_df[fisher_df.significant_bonferroni]
if len(sig_bonf_cpa):
    print("CPA pairs surviving Bonferroni:")
    for _, r in sig_bonf_cpa.iterrows():
        print(f"  {r.group_a} vs {r.group_b}: p={r.p_value:.2e}")
if len(sig_bonf_fisher):
    print("Conversion-rate pairs surviving Bonferroni:")
    for _, r in sig_bonf_fisher.iterrows():
        print(f"  {r.group_a} vs {r.group_b}: p={r.p_value:.2e}")

# ---- Benjamini-Hochberg FDR ----
ttest_df["p_value_fdr"] = false_discovery_control(ttest_df["p_value"].values, method="bh")
fisher_df["p_value_fdr"] = false_discovery_control(fisher_df["p_value"].values, method="bh")
ttest_df["significant_fdr"] = ttest_df["p_value_fdr"] < ALPHA
fisher_df["significant_fdr"] = fisher_df["p_value_fdr"] < ALPHA

print(f"\nCPA comparisons significant after FDR (BH): {ttest_df['significant_fdr'].sum()}")
print(f"Conversion-rate comparisons significant after FDR (BH): {fisher_df['significant_fdr'].sum()}")

sig_fdr_cpa = ttest_df[ttest_df.significant_fdr]
sig_fdr_fisher = fisher_df[fisher_df.significant_fdr]
if len(sig_fdr_cpa):
    print("CPA pairs surviving FDR:")
    for _, r in sig_fdr_cpa.iterrows():
        print(f"  {r.group_a} vs {r.group_b}: p={r.p_value:.2e}, p_fdr={r.p_value_fdr:.4f}, d={r.cohens_d:.2f}")
if len(sig_fdr_fisher):
    print("Conversion-rate pairs surviving FDR:")
    for _, r in sig_fdr_fisher.iterrows():
        print(f"  {r.group_a} vs {r.group_b}: p={r.p_value:.2e}, p_fdr={r.p_value_fdr:.4f}")

# ---- Comparison summary table + chart ----
summary = pd.DataFrame({
    "metric": ["CPA (t-test)", "Conversion rate (Fisher's exact)"],
    "n_comparisons": [n_cpa, n_fisher],
    "uncorrected_sig": [n_sig_uncorrected_cpa, n_sig_uncorrected_fisher],
    "bonferroni_sig": [ttest_df.significant_bonferroni.sum(), fisher_df.significant_bonferroni.sum()],
    "fdr_sig": [ttest_df.significant_fdr.sum(), fisher_df.significant_fdr.sum()],
})
print("\n=== Correction method comparison ===")
print(summary.to_string(index=False))

fig, ax = plt.subplots(figsize=(7, 4.5))
x = np.arange(len(summary))
w = 0.25
ax.bar(x - w, summary["uncorrected_sig"], w, label="Uncorrected (α=0.05)", color="#C44E52")
ax.bar(x, summary["bonferroni_sig"], w, label="Bonferroni", color="#4C72B0")
ax.bar(x + w, summary["fdr_sig"], w, label="FDR (BH)", color="#55A868")
ax.set_xticks(x); ax.set_xticklabels(summary["metric"])
ax.set_ylabel("# significant comparisons")
ax.set_title("Effect of multiple-comparisons correction")
ax.legend()
plt.tight_layout()
plt.savefig("output/images/correction_comparison.png", dpi=150)
plt.close()
print("Saved output/images/correction_comparison.png")

# Save all result tables
ttest_df.to_csv("output/data/cpa_ttest_results.csv", index=False)
fisher_df.to_csv("output/data/conversion_rate_fisher_results.csv", index=False)
summary.to_csv("output/data/correction_summary.csv", index=False)
binom.to_csv("output/data/conversion_binomial_summary.csv", index=False)

print("\nPart 2-3 complete.")
