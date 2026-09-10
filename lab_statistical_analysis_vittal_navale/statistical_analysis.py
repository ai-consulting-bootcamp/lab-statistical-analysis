"""
Parts 2-3: Pairwise Group Comparisons & Multiple Comparisons Correction
Lab: In God we trust, everyone else bring the data

Reads the cleaned daily-by-channel panel produced by data_exploration.py and:
  - Compares channel CPA using independent t-tests + Cohen's d (Part 2, Step 4)
  - Compares channel conversion rates using Fisher's exact test (Part 2, Step 5)
  - Applies Bonferroni and Benjamini-Hochberg corrections to both families of
    tests (Part 3, Step 6)
"""

import itertools

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import false_discovery_control

plt.style.use("seaborn-v0_8-whitegrid")

GROUP_COL = "channel"
ALPHA = 0.05

daily = pd.read_csv("data/marketing_data.csv", parse_dates=["date"])
channels = sorted(daily[GROUP_COL].unique())
print("Channels:", channels)

# ===========================================================================
# Step 4: t-tests on CPA (continuous metric)
# ===========================================================================
def cohens_d(a, b):
    pooled_std = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return (b.mean() - a.mean()) / pooled_std


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


metric = "cpa"
clean = daily.dropna(subset=[metric])
clean = clean[np.isfinite(clean[metric])]

ttest_rows = []
for a, b in itertools.combinations(channels, 2):
    vals_a = clean.loc[clean[GROUP_COL] == a, metric]
    vals_b = clean.loc[clean[GROUP_COL] == b, metric]
    t_stat, p_val = stats.ttest_ind(vals_a, vals_b, equal_var=False)
    mean_a, mean_b = vals_a.mean(), vals_b.mean()
    diff = mean_b - mean_a
    pct_diff = (diff / mean_a) * 100
    d = cohens_d(vals_a, vals_b)
    ttest_rows.append(
        dict(
            group_a=a,
            group_b=b,
            n_a=len(vals_a),
            n_b=len(vals_b),
            mean_a=mean_a,
            mean_b=mean_b,
            diff=diff,
            pct_diff=pct_diff,
            t_stat=t_stat,
            p_value=p_val,
            cohens_d=d,
            effect_size=interpret_d(d),
            significant_uncorrected=p_val < ALPHA,
        )
    )

ttest_df = pd.DataFrame(ttest_rows).sort_values("p_value").reset_index(drop=True)
print(f"\n=== CPA t-test results ({metric}), {len(ttest_df)} pairwise comparisons ===")
for _, r in ttest_df.iterrows():
    print(
        f"{r.group_a:>15} vs {r.group_b:<15} | mean_a=${r.mean_a:8.2f} mean_b=${r.mean_b:8.2f} "
        f"diff=${r['diff']:9.2f} ({r.pct_diff:+7.1f}%) | t={r.t_stat:7.3f} p={r.p_value:.4e} "
        f"d={r.cohens_d:6.2f} ({r.effect_size}) {'*' if r.significant_uncorrected else ''}"
    )

n_sig_uncorrected_cpa = ttest_df["significant_uncorrected"].sum()
print(f"\nTotal CPA comparisons: {len(ttest_df)}; significant at alpha=0.05 (uncorrected): {n_sig_uncorrected_cpa}")

ttest_df.round(4).to_csv("data/ttest_cpa_results.csv", index=False)

# --- Heatmap of CPA p-values ---
mat = pd.DataFrame(np.ones((len(channels), len(channels))), index=channels, columns=channels)
for _, r in ttest_df.iterrows():
    mat.loc[r.group_a, r.group_b] = r.p_value
    mat.loc[r.group_b, r.group_a] = r.p_value
np.fill_diagonal(mat.values, 1.0)

fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(mat.values, cmap="RdYlGn_r", vmin=0, vmax=1)
ax.set_xticks(range(len(channels)))
ax.set_yticks(range(len(channels)))
ax.set_xticklabels(channels, rotation=45, ha="right")
ax.set_yticklabels(channels)
for i in range(len(channels)):
    for j in range(len(channels)):
        ax.text(j, i, f"{mat.values[i, j]:.3f}", ha="center", va="center", fontsize=8,
                 color="white" if mat.values[i, j] < 0.3 else "black")
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("p-value (t-test on daily CPA)")
ax.set_title("CPA Comparison Heatmap (p-values)\nRed = significant, Green = not significant")
fig.tight_layout()
fig.savefig("images/metric_comparison_heatmap.png", dpi=150, bbox_inches="tight")
print("Saved images/metric_comparison_heatmap.png")

# ===========================================================================
# Step 5: Fisher's exact test on conversion rate (binary outcome)
# ===========================================================================
totals = (
    daily.groupby(GROUP_COL, as_index=False)
    .agg(conversions=("conversions", "sum"), clicks=("clicks", "sum"))
)
totals["non_conversions"] = totals["clicks"] - totals["conversions"]
totals["conversion_rate"] = totals["conversions"] / totals["clicks"]
print("\n=== Conversion summary by channel (clicks -> conversions) ===")
print(totals.round(4).to_string(index=False))
totals.round(4).to_csv("data/conversion_totals.csv", index=False)

fisher_rows = []
for a, b in itertools.combinations(channels, 2):
    row_a = totals.loc[totals[GROUP_COL] == a].iloc[0]
    row_b = totals.loc[totals[GROUP_COL] == b].iloc[0]
    table = [
        [row_a.conversions, row_a.non_conversions],
        [row_b.conversions, row_b.non_conversions],
    ]
    odds_ratio, p_val = stats.fisher_exact(table, alternative="two-sided")
    rate_a = row_a.conversions / row_a.clicks
    rate_b = row_b.conversions / row_b.clicks
    diff = rate_b - rate_a
    pct_diff = (diff / rate_a) * 100
    fisher_rows.append(
        dict(
            group_a=a,
            group_b=b,
            conversions_a=int(row_a.conversions),
            clicks_a=int(row_a.clicks),
            rate_a=rate_a,
            conversions_b=int(row_b.conversions),
            clicks_b=int(row_b.clicks),
            rate_b=rate_b,
            diff=diff,
            pct_diff=pct_diff,
            odds_ratio=odds_ratio,
            p_value=p_val,
            significant_uncorrected=p_val < ALPHA,
        )
    )

fisher_df = pd.DataFrame(fisher_rows).sort_values("p_value").reset_index(drop=True)
print(f"\n=== Fisher's exact test results (conversion rate), {len(fisher_df)} pairwise comparisons ===")
for _, r in fisher_df.iterrows():
    print(
        f"{r.group_a:>15} vs {r.group_b:<15} | rate_a={r.rate_a*100:5.2f}% rate_b={r.rate_b*100:5.2f}% "
        f"diff={r['diff']*100:+6.2f}pp ({r.pct_diff:+6.1f}%) | OR={r.odds_ratio:6.3f} p={r.p_value:.4e} "
        f"{'*' if r.significant_uncorrected else ''}"
    )

n_sig_uncorrected_fisher = fisher_df["significant_uncorrected"].sum()
print(f"\nTotal conversion-rate comparisons: {len(fisher_df)}; significant at alpha=0.05 (uncorrected): {n_sig_uncorrected_fisher}")

fisher_df.round(6).to_csv("data/fisher_conversion_results.csv", index=False)

# --- Rate comparison bar chart ---
totals_sorted = totals.sort_values("conversion_rate", ascending=True)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(totals_sorted[GROUP_COL], totals_sorted["conversion_rate"] * 100, color="teal")
for bar, val in zip(bars, totals_sorted["conversion_rate"] * 100):
    ax.text(val + 0.02, bar.get_y() + bar.get_height() / 2, f"{val:.2f}%", va="center", fontsize=9)
ax.set_xlabel("Conversion Rate (%)")
ax.set_title("Conversion Rate by Channel (clicks -> conversions), 2023-2025")
fig.tight_layout()
fig.savefig("images/rate_comparison.png", dpi=150, bbox_inches="tight")
print("Saved images/rate_comparison.png")

# ===========================================================================
# Step 6: Multiple comparisons correction
# ===========================================================================
n_cpa = len(ttest_df)
n_fisher = len(fisher_df)
total_comparisons = n_cpa + n_fisher
expected_false_positives = total_comparisons * ALPHA

print(f"\n=== Multiple Comparisons Problem ===")
print(f"CPA comparisons: {n_cpa}; Conversion-rate comparisons: {n_fisher}; Total: {total_comparisons}")
print(f"At alpha=0.05, we expect ~{expected_false_positives:.2f} false positives by chance alone across all comparisons.")
print("Some 'significant' results below are likely due to random variation, not real channel differences.")

# --- Bonferroni ---
alpha_bonf_cpa = ALPHA / n_cpa
alpha_bonf_fisher = ALPHA / n_fisher
ttest_df["significant_bonferroni"] = ttest_df["p_value"] < alpha_bonf_cpa
fisher_df["significant_bonferroni"] = fisher_df["p_value"] < alpha_bonf_fisher

print(f"\nBonferroni-adjusted alpha for CPA comparisons: {alpha_bonf_cpa:.6f}")
print(f"CPA comparisons significant after Bonferroni: {ttest_df['significant_bonferroni'].sum()} / {n_cpa}")
print(ttest_df.loc[ttest_df["significant_bonferroni"], ["group_a", "group_b", "p_value"]].to_string(index=False))

print(f"\nBonferroni-adjusted alpha for conversion-rate comparisons: {alpha_bonf_fisher:.6f}")
print(f"Conversion-rate comparisons significant after Bonferroni: {fisher_df['significant_bonferroni'].sum()} / {n_fisher}")
print(fisher_df.loc[fisher_df["significant_bonferroni"], ["group_a", "group_b", "p_value"]].to_string(index=False))

# --- Benjamini-Hochberg FDR ---
ttest_df["p_value_fdr"] = false_discovery_control(ttest_df["p_value"], method="bh")
ttest_df["significant_fdr"] = ttest_df["p_value_fdr"] < ALPHA

fisher_df["p_value_fdr"] = false_discovery_control(fisher_df["p_value"], method="bh")
fisher_df["significant_fdr"] = fisher_df["p_value_fdr"] < ALPHA

print(f"\nCPA comparisons significant after FDR (BH): {ttest_df['significant_fdr'].sum()} / {n_cpa}")
print(ttest_df.loc[ttest_df["significant_fdr"], ["group_a", "group_b", "p_value", "p_value_fdr"]].to_string(index=False))

print(f"\nConversion-rate comparisons significant after FDR (BH): {fisher_df['significant_fdr'].sum()} / {n_fisher}")
print(fisher_df.loc[fisher_df["significant_fdr"], ["group_a", "group_b", "p_value", "p_value_fdr"]].to_string(index=False))

ttest_df.round(6).to_csv("data/ttest_cpa_results.csv", index=False)
fisher_df.round(6).to_csv("data/fisher_conversion_results.csv", index=False)

# --- Comparison summary table ---
correction_summary = pd.DataFrame(
    [
        {
            "metric": "CPA (t-test)",
            "uncorrected": int(ttest_df["significant_uncorrected"].sum()),
            "bonferroni": int(ttest_df["significant_bonferroni"].sum()),
            "fdr_bh": int(ttest_df["significant_fdr"].sum()),
            "total_comparisons": n_cpa,
        },
        {
            "metric": "Conversion Rate (Fisher)",
            "uncorrected": int(fisher_df["significant_uncorrected"].sum()),
            "bonferroni": int(fisher_df["significant_bonferroni"].sum()),
            "fdr_bh": int(fisher_df["significant_fdr"].sum()),
            "total_comparisons": n_fisher,
        },
    ]
)
print("\n=== Correction Method Comparison ===")
print(correction_summary.to_string(index=False))
correction_summary.to_csv("data/correction_summary.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(correction_summary))
width = 0.25
ax.bar(x - width, correction_summary["uncorrected"], width, label="Uncorrected (a=0.05)")
ax.bar(x, correction_summary["bonferroni"], width, label="Bonferroni")
ax.bar(x + width, correction_summary["fdr_bh"], width, label="FDR (Benjamini-Hochberg)")
ax.set_xticks(x)
ax.set_xticklabels(correction_summary["metric"])
ax.set_ylabel("Number of Significant Comparisons")
ax.set_title("Effect of Multiple Comparisons Correction")
ax.legend()
fig.tight_layout()
fig.savefig("images/correction_comparison.png", dpi=150, bbox_inches="tight")
print("Saved images/correction_comparison.png")

print("\nStatistical analysis complete.")
