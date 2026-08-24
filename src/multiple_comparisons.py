import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import false_discovery_control


# ============================================================
# CONFIGURATION
# ============================================================

CPA_FILE = "results/tables/cpa_ttest_results.csv"
FISHER_FILE = "results/tables/fisher_exact_results.csv"

TABLE_DIR = "results/tables"
FIGURE_DIR = "results/figures"

ALPHA = 0.05


# ============================================================
# LOAD RESULTS
# ============================================================

print("Loading statistical results...")

cpa = pd.read_csv(CPA_FILE)
fisher = pd.read_csv(FISHER_FILE)

print(f"CPA comparisons: {len(cpa)}")
print(f"Conversion-rate comparisons: {len(fisher)}")


# ============================================================
# CPA — BONFERRONI
# ============================================================

print("\n" + "=" * 60)
print("CPA — MULTIPLE COMPARISONS")
print("=" * 60)

cpa_n = len(cpa)

cpa_bonferroni_alpha = ALPHA / cpa_n

cpa["significant_bonferroni"] = (
    cpa["p_value"] < cpa_bonferroni_alpha
)

print(
    f"\nBonferroni alpha: "
    f"{cpa_bonferroni_alpha:.6f}"
)

print(
    "Significant before correction:",
    cpa["significant_uncorrected"].sum()
)

print(
    "Significant after Bonferroni:",
    cpa["significant_bonferroni"].sum()
)


# ============================================================
# CPA — BENJAMINI-HOCHBERG FDR
# ============================================================

cpa["p_value_fdr"] = false_discovery_control(
    cpa["p_value"].values,
    method="bh"
)

cpa["significant_fdr"] = (
    cpa["p_value_fdr"] < ALPHA
)

print(
    "Significant after Benjamini-Hochberg:",
    cpa["significant_fdr"].sum()
)


# Save CPA corrected results

cpa.to_csv(
    f"{TABLE_DIR}/cpa_multiple_comparisons.csv",
    index=False
)


# ============================================================
# CONVERSION RATE — BONFERRONI
# ============================================================

print("\n" + "=" * 60)
print("CONVERSION RATE — MULTIPLE COMPARISONS")
print("=" * 60)

fisher_n = len(fisher)

fisher_bonferroni_alpha = ALPHA / fisher_n

fisher["significant_bonferroni"] = (
    fisher["p_value"] < fisher_bonferroni_alpha
)

print(
    f"\nBonferroni alpha: "
    f"{fisher_bonferroni_alpha:.6f}"
)

print(
    "Significant before correction:",
    fisher["significant_uncorrected"].sum()
)

print(
    "Significant after Bonferroni:",
    fisher["significant_bonferroni"].sum()
)


# ============================================================
# CONVERSION RATE — BENJAMINI-HOCHBERG
# ============================================================

fisher["p_value_fdr"] = false_discovery_control(
    fisher["p_value"].values,
    method="bh"
)

fisher["significant_fdr"] = (
    fisher["p_value_fdr"] < ALPHA
)

print(
    "Significant after Benjamini-Hochberg:",
    fisher["significant_fdr"].sum()
)


# Save corrected Fisher results

fisher.to_csv(
    f"{TABLE_DIR}/fisher_multiple_comparisons.csv",
    index=False
)


# ============================================================
# DISPLAY SIGNIFICANT CPA RESULTS
# ============================================================

print("\n" + "=" * 60)
print("CPA RESULTS SURVIVING FDR")
print("=" * 60)

cpa_fdr = cpa[
    cpa["significant_fdr"]
].sort_values("p_value_fdr")

if len(cpa_fdr) == 0:

    print("No CPA comparisons remain significant after FDR.")

else:

    print(
        cpa_fdr[
            [
                "group_a",
                "group_b",
                "mean_a",
                "mean_b",
                "p_value",
                "p_value_fdr",
                "cohens_d",
                "effect_size"
            ]
        ].round(6).to_string(index=False)
    )


# ============================================================
# DISPLAY SIGNIFICANT CONVERSION RESULTS
# ============================================================

print("\n" + "=" * 60)
print("CONVERSION RATE RESULTS SURVIVING FDR")
print("=" * 60)

fisher_fdr = fisher[
    fisher["significant_fdr"]
].sort_values("p_value_fdr")

if len(fisher_fdr) == 0:

    print(
        "No conversion-rate comparisons "
        "remain significant after FDR."
    )

else:

    print(
        fisher_fdr[
            [
                "group_a",
                "group_b",
                "conversion_rate_a",
                "conversion_rate_b",
                "difference_b_minus_a",
                "odds_ratio",
                "p_value",
                "p_value_fdr"
            ]
        ].round(6).to_string(index=False)
    )


# ============================================================
# SUMMARY TABLE
# ============================================================

summary = pd.DataFrame({
    "analysis": [
        "CPA",
        "CPA",
        "CPA",
        "Conversion Rate",
        "Conversion Rate",
        "Conversion Rate"
    ],
    "method": [
        "Uncorrected",
        "Bonferroni",
        "Benjamini-Hochberg FDR",
        "Uncorrected",
        "Bonferroni",
        "Benjamini-Hochberg FDR"
    ],
    "number_of_comparisons": [
        len(cpa),
        len(cpa),
        len(cpa),
        len(fisher),
        len(fisher),
        len(fisher)
    ],
    "alpha": [
        ALPHA,
        cpa_bonferroni_alpha,
        ALPHA,
        ALPHA,
        fisher_bonferroni_alpha,
        ALPHA
    ],
    "significant_results": [
        cpa["significant_uncorrected"].sum(),
        cpa["significant_bonferroni"].sum(),
        cpa["significant_fdr"].sum(),
        fisher["significant_uncorrected"].sum(),
        fisher["significant_bonferroni"].sum(),
        fisher["significant_fdr"].sum()
    ]
})

summary.to_csv(
    f"{TABLE_DIR}/multiple_comparisons_summary.csv",
    index=False
)

print("\n" + "=" * 60)
print("CORRECTION SUMMARY")
print("=" * 60)

print(
    summary.to_string(index=False)
)


# ============================================================
# EXPECTED FALSE POSITIVES
# ============================================================

total_tests = len(cpa) + len(fisher)

expected_false_positives = total_tests * ALPHA

print("\n" + "=" * 60)
print("MULTIPLE COMPARISON CONTEXT")
print("=" * 60)

print(f"Total statistical tests: {total_tests}")
print(f"Alpha level: {ALPHA}")
print(
    f"Expected false positives at alpha=0.05: "
    f"{expected_false_positives:.2f}"
)


# ============================================================
# VISUALIZATION
# ============================================================

print("\nCreating correction comparison chart...")

plot_summary = summary.copy()

labels = [
    "CPA\nUncorrected",
    "CPA\nBonferroni",
    "CPA\nFDR",
    "Conversion\nUncorrected",
    "Conversion\nBonferroni",
    "Conversion\nFDR"
]

values = plot_summary["significant_results"].values

plt.figure(figsize=(10, 6))

bars = plt.bar(
    range(len(values)),
    values
)

plt.xticks(
    range(len(values)),
    labels
)

plt.ylabel("Number of Significant Comparisons")

plt.title(
    "Impact of Multiple Comparisons Correction"
)

for bar, value in zip(bars, values):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        str(int(value)),
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/correction_comparison.png",
    dpi=300
)

plt.close()

print(
    f"Saved: {FIGURE_DIR}/correction_comparison.png"
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 60)
print("MULTIPLE COMPARISONS ANALYSIS COMPLETED")
print("=" * 60)

print("\nFiles created:")

print(
    "- results/tables/cpa_multiple_comparisons.csv"
)

print(
    "- results/tables/fisher_multiple_comparisons.csv"
)

print(
    "- results/tables/multiple_comparisons_summary.csv"
)

print(
    "- results/figures/correction_comparison.png"
)