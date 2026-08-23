from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from scipy.stats import fisher_exact, ttest_ind
from scipy.stats import false_discovery_control, fisher_exact, ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "marketing_data.csv"
RESULTS_DIR = BASE_DIR / "results"


# ---------------------------------------------------------
# Load prepared data
# ---------------------------------------------------------

df = pd.read_csv(DATA_FILE)

campaign_ids = sorted(df["xyz_campaign_id"].unique())

print("\n--- CAMPAIGNS ---")
print(campaign_ids)


# ---------------------------------------------------------
# Cohen's d
# ---------------------------------------------------------

def cohens_d(group_a, group_b):
    mean_difference = group_b.mean() - group_a.mean()
    pooled_std = np.sqrt((group_a.var(ddof=1) + group_b.var(ddof=1)) / 2)

    if pooled_std == 0:
        return np.nan

    return mean_difference / pooled_std


def interpret_effect_size(d):
    absolute_d = abs(d)

    if absolute_d < 0.2:
        return "negligible"
    if absolute_d < 0.5:
        return "small"
    if absolute_d < 0.8:
        return "medium"

    return "large"

# ---------------------------------------------------------
# Pairwise CPA comparisons
# ---------------------------------------------------------

cpa_results = []

for campaign_a, campaign_b in combinations(campaign_ids, 2):
    group_a = df.loc[(df["xyz_campaign_id"] == campaign_a) & df["CPA"].notna(), "CPA"]
    group_b = df.loc[(df["xyz_campaign_id"] == campaign_b) & df["CPA"].notna(), "CPA"]

    t_statistic, p_value = ttest_ind(group_a, group_b, equal_var=False)

    mean_a = group_a.mean()
    mean_b = group_b.mean()
    difference = mean_b - mean_a
    percentage_difference = (difference / mean_a) * 100

    d = cohens_d(group_a, group_b)

    cpa_results.append({
        "campaign_a": campaign_a,
        "campaign_b": campaign_b,
        "n_a": len(group_a),
        "n_b": len(group_b),
        "mean_cpa_a": mean_a,
        "mean_cpa_b": mean_b,
        "difference": difference,
        "percentage_difference": percentage_difference,
        "t_statistic": t_statistic,
        "p_value": p_value,
        "cohens_d": d,
        "effect_size": interpret_effect_size(d),
        "significant_0_05": p_value < 0.05,
    })


# ---------------------------------------------------------
# CPA comparison results
# ---------------------------------------------------------

cpa_results_df = pd.DataFrame(cpa_results)

print("\n--- CPA PAIRWISE COMPARISONS ---")
print(cpa_results_df.round(4).to_string(index=False))

print("\n--- CPA SIGNIFICANCE SUMMARY ---")
print(f"Total comparisons: {len(cpa_results_df)}")
print(f"Significant at p < 0.05: {cpa_results_df['significant_0_05'].sum()}")


# ---------------------------------------------------------
# Save CPA results
# ---------------------------------------------------------

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CPA_RESULTS_FILE = RESULTS_DIR / "cpa_pairwise_comparisons.csv"
cpa_results_df.to_csv(CPA_RESULTS_FILE, index=False)

print(f"\nCPA results saved to: {CPA_RESULTS_FILE}")

# ---------------------------------------------------------
# Aggregate conversion outcomes
# ---------------------------------------------------------

conversion_summary = df.groupby("xyz_campaign_id").agg(
    total_conversions=("Total_Conversion", "sum"),
    approved_conversions=("Approved_Conversion", "sum"),
).reset_index()

conversion_summary["non_approved_conversions"] = conversion_summary["total_conversions"] - conversion_summary["approved_conversions"]
conversion_summary["purchase_rate"] = conversion_summary["approved_conversions"] / conversion_summary["total_conversions"]

print("\n--- CONVERSION OUTCOME SUMMARY ---")
print(conversion_summary.round(4).to_string(index=False))


# ---------------------------------------------------------
# Pairwise Fisher's exact tests
# ---------------------------------------------------------

fisher_results = []

for campaign_a, campaign_b in combinations(campaign_ids, 2):
    row_a = conversion_summary.loc[conversion_summary["xyz_campaign_id"] == campaign_a].iloc[0]
    row_b = conversion_summary.loc[conversion_summary["xyz_campaign_id"] == campaign_b].iloc[0]

    contingency_table = [
        [row_a["approved_conversions"], row_a["non_approved_conversions"]],
        [row_b["approved_conversions"], row_b["non_approved_conversions"]],
    ]

    odds_ratio, p_value = fisher_exact(contingency_table, alternative="two-sided")

    rate_a = row_a["purchase_rate"]
    rate_b = row_b["purchase_rate"]

    difference = rate_b - rate_a
    percentage_difference = (difference / rate_a) * 100

    fisher_results.append({
        "campaign_a": campaign_a,
        "campaign_b": campaign_b,
        "approved_a": row_a["approved_conversions"],
        "total_a": row_a["total_conversions"],
        "purchase_rate_a": rate_a,
        "approved_b": row_b["approved_conversions"],
        "total_b": row_b["total_conversions"],
        "purchase_rate_b": rate_b,
        "difference": difference,
        "percentage_difference": percentage_difference,
        "odds_ratio": odds_ratio,
        "p_value": p_value,
        "significant_0_05": p_value < 0.05,
    })


# ---------------------------------------------------------
# Fisher results
# ---------------------------------------------------------

fisher_results_df = pd.DataFrame(fisher_results)

print("\n--- FISHER PAIRWISE COMPARISONS ---")
print(fisher_results_df.round(4).to_string(index=False))

print("\n--- FISHER SIGNIFICANCE SUMMARY ---")
print(f"Total comparisons: {len(fisher_results_df)}")
print(f"Significant at p < 0.05: {fisher_results_df['significant_0_05'].sum()}")


# ---------------------------------------------------------
# Save Fisher results
# ---------------------------------------------------------

FISHER_RESULTS_FILE = RESULTS_DIR / "fisher_pairwise_comparisons.csv"
fisher_results_df.to_csv(FISHER_RESULTS_FILE, index=False)

print(f"\nFisher results saved to: {FISHER_RESULTS_FILE}")

# ---------------------------------------------------------
# Multiple comparisons overview
# ---------------------------------------------------------

alpha = 0.05

total_comparisons = len(cpa_results_df) + len(fisher_results_df)
expected_false_positives = total_comparisons * alpha

print("\n--- MULTIPLE COMPARISONS OVERVIEW ---")
print(f"Total statistical tests: {total_comparisons}")
print(f"Expected false positives at alpha = 0.05: {expected_false_positives:.2f}")

# ---------------------------------------------------------
# Bonferroni correction
# ---------------------------------------------------------

cpa_bonferroni_alpha = alpha / len(cpa_results_df)
fisher_bonferroni_alpha = alpha / len(fisher_results_df)

cpa_results_df["significant_bonferroni"] = cpa_results_df["p_value"] < cpa_bonferroni_alpha
fisher_results_df["significant_bonferroni"] = fisher_results_df["p_value"] < fisher_bonferroni_alpha

print("\n--- BONFERRONI CORRECTION ---")
print(f"CPA adjusted alpha: {cpa_bonferroni_alpha:.4f}")
print(f"Purchase-rate adjusted alpha: {fisher_bonferroni_alpha:.4f}")
print(f"Significant CPA comparisons: {cpa_results_df['significant_bonferroni'].sum()}")
print(f"Significant purchase-rate comparisons: {fisher_results_df['significant_bonferroni'].sum()}")

# ---------------------------------------------------------
# Benjamini-Hochberg FDR correction
# ---------------------------------------------------------

cpa_results_df["p_value_fdr"] = false_discovery_control(cpa_results_df["p_value"].to_numpy(), method="bh")
fisher_results_df["p_value_fdr"] = false_discovery_control(fisher_results_df["p_value"].to_numpy(), method="bh")

cpa_results_df["significant_fdr"] = cpa_results_df["p_value_fdr"] < alpha
fisher_results_df["significant_fdr"] = fisher_results_df["p_value_fdr"] < alpha

print("\n--- BENJAMINI-HOCHBERG FDR ---")

print("\nCPA:")
print(cpa_results_df[["campaign_a", "campaign_b", "p_value", "p_value_fdr", "significant_fdr"]].round(6).to_string(index=False))

print("\nPurchase Rate:")
print(fisher_results_df[["campaign_a", "campaign_b", "p_value", "p_value_fdr", "significant_fdr"]].round(6).to_string(index=False))

# ---------------------------------------------------------
# Correction summary
# ---------------------------------------------------------

correction_summary = pd.DataFrame([
    {
        "metric": "CPA",
        "uncorrected": cpa_results_df["significant_0_05"].sum(),
        "bonferroni": cpa_results_df["significant_bonferroni"].sum(),
        "fdr": cpa_results_df["significant_fdr"].sum(),
    },
    {
        "metric": "Purchase Rate",
        "uncorrected": fisher_results_df["significant_0_05"].sum(),
        "bonferroni": fisher_results_df["significant_bonferroni"].sum(),
        "fdr": fisher_results_df["significant_fdr"].sum(),
    },
])

print("\n--- CORRECTION SUMMARY ---")
print(correction_summary.to_string(index=False))

# ---------------------------------------------------------
# Correction summary
# ---------------------------------------------------------

correction_summary = pd.DataFrame([
    {
        "metric": "CPA",
        "uncorrected": cpa_results_df["significant_0_05"].sum(),
        "bonferroni": cpa_results_df["significant_bonferroni"].sum(),
        "fdr": cpa_results_df["significant_fdr"].sum(),
    },
    {
        "metric": "Purchase Rate",
        "uncorrected": fisher_results_df["significant_0_05"].sum(),
        "bonferroni": fisher_results_df["significant_bonferroni"].sum(),
        "fdr": fisher_results_df["significant_fdr"].sum(),
    },
])

print("\n--- CORRECTION SUMMARY ---")
print(correction_summary.to_string(index=False))


# ---------------------------------------------------------
# CPA p-value heatmap
# ---------------------------------------------------------

p_value_matrix = pd.DataFrame(1.0, index=campaign_ids, columns=campaign_ids)

for _, row in cpa_results_df.iterrows():
    campaign_a = int(row["campaign_a"])
    campaign_b = int(row["campaign_b"])
    p_value = row["p_value"]

    p_value_matrix.loc[campaign_a, campaign_b] = p_value
    p_value_matrix.loc[campaign_b, campaign_a] = p_value

fig, ax = plt.subplots(figsize=(6, 5))

image = ax.imshow(p_value_matrix.values, vmin=0, vmax=0.05)

ax.set_xticks(range(len(campaign_ids)), labels=campaign_ids)
ax.set_yticks(range(len(campaign_ids)), labels=campaign_ids)

ax.set_xlabel("Campaign")
ax.set_ylabel("Campaign")
ax.set_title("CPA Pairwise p-values")

for i in range(len(campaign_ids)):
    for j in range(len(campaign_ids)):
        value = p_value_matrix.iloc[i, j]
        label = f"{value:.3f}" if value >= 0.001 else "<0.001"
        ax.text(j, i, label, ha="center", va="center")

fig.colorbar(image, ax=ax, label="p-value")
plt.tight_layout()

HEATMAP_FILE = RESULTS_DIR / "metric_comparison_heatmap.png"
plt.savefig(HEATMAP_FILE, dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------
# Purchase-rate comparison
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 5))

ax.bar(
    conversion_summary["xyz_campaign_id"].astype(str),
    conversion_summary["purchase_rate"] * 100,
)

ax.set_xlabel("Campaign")
ax.set_ylabel("Purchase Rate (%)")
ax.set_title("Purchase Rate by Campaign")

plt.tight_layout()

RATE_FILE = RESULTS_DIR / "rate_comparison.png"
plt.savefig(RATE_FILE, dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------
# Multiple-comparison correction chart
# ---------------------------------------------------------

correction_plot_df = correction_summary.melt(
    id_vars="metric",
    var_name="correction_method",
    value_name="significant_comparisons",
)

fig, ax = plt.subplots(figsize=(8, 5))

sns.barplot(
    data=correction_plot_df,
    x="correction_method",
    y="significant_comparisons",
    hue="metric",
    ax=ax,
)

ax.set_xlabel("Correction Method")
ax.set_ylabel("Number of Significant Comparisons")
ax.set_title("Effect of Multiple-Comparison Correction")

plt.tight_layout()

CORRECTION_CHART_FILE = RESULTS_DIR / "correction_comparison.png"
plt.savefig(CORRECTION_CHART_FILE, dpi=150, bbox_inches="tight")
plt.close()

print("\n--- CORRECTION CHART SAVED ---")
print(CORRECTION_CHART_FILE)

# ---------------------------------------------------------
# Save final corrected results
# ---------------------------------------------------------

cpa_results_df.to_csv(CPA_RESULTS_FILE, index=False)
fisher_results_df.to_csv(FISHER_RESULTS_FILE, index=False)

print("\n--- FINAL RESULT FILES SAVED ---")
print(CPA_RESULTS_FILE)
print(FISHER_RESULTS_FILE)

