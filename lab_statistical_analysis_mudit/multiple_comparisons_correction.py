"""
Step 6: Apply Multiple Comparisons Correction
=================================================
Applies Bonferroni and Benjamini-Hochberg (FDR) correction to the two
families of pairwise tests from Steps 4 and 5 (21 t-tests on total_ads,
21 Fisher's exact tests on conversion rate, both across most_ads_day).
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import false_discovery_control

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)

ALPHA = 0.05

ttest_df = pd.read_csv("results/ttest_results.csv")
fisher_df = pd.read_csv("results/fisher_results_by_day.csv")

# 1. The multiple comparisons problem ----------------------------------------
total_comparisons = len(ttest_df) + len(fisher_df)
expected_false_positives = total_comparisons * ALPHA
print("=" * 70)
print("THE MULTIPLE COMPARISONS PROBLEM")
print("=" * 70)
print(f"Total comparisons made: {len(ttest_df)} (t-tests) + {len(fisher_df)} (Fisher's exact) "
      f"= {total_comparisons}")
print(f"At alpha={ALPHA}, we expect ~{expected_false_positives:.2f} false positives by chance alone, "
      f"even if none of the true underlying differences existed.")
print("Some of the 'significant' results found in Steps 4-5 are therefore likely to be noise, "
      "not real differences — correction is needed before acting on them.")


def apply_corrections(df, label):
    n = len(df)
    alpha_bonf = ALPHA / n
    df = df.copy()
    df["significant_bonferroni"] = df["p_value"] < alpha_bonf

    df["p_value_fdr"] = false_discovery_control(df["p_value"].values, method="bh")
    df["significant_fdr"] = df["p_value_fdr"] < ALPHA

    print()
    print("=" * 70)
    print(f"{label} — {n} comparisons, Bonferroni alpha = {alpha_bonf:.6f}")
    print("=" * 70)
    n_uncorrected = (df["p_value"] < ALPHA).sum()
    n_bonf = df["significant_bonferroni"].sum()
    n_fdr = df["significant_fdr"].sum()
    print(f"Significant uncorrected (alpha=0.05): {n_uncorrected}")
    print(f"Significant after Bonferroni:          {n_bonf}")
    print(f"Significant after FDR (BH):             {n_fdr}")

    if n_bonf > 0:
        print("\nComparisons remaining significant after Bonferroni:")
        print(df.loc[df["significant_bonferroni"], ["group_a", "group_b", "p_value"]])
    if n_fdr > 0:
        print("\nComparisons remaining significant after FDR:")
        print(df.loc[df["significant_fdr"], ["group_a", "group_b", "p_value", "p_value_fdr"]])

    return df, n_uncorrected, n_bonf, n_fdr


ttest_corrected, t_unc, t_bonf, t_fdr = apply_corrections(ttest_df, "T-TEST (total_ads by most_ads_day)")
fisher_corrected, f_unc, f_bonf, f_fdr = apply_corrections(fisher_df, "FISHER'S EXACT (conversion by most_ads_day)")

ttest_corrected.to_csv("results/ttest_results_corrected.csv", index=False)
fisher_corrected.to_csv("results/fisher_results_corrected.csv", index=False)

# 2. Compare correction methods -----------------------------------------------
summary = pd.DataFrame(
    {
        "Uncorrected": [t_unc, f_unc],
        "Bonferroni": [t_bonf, f_bonf],
        "FDR (BH)": [t_fdr, f_fdr],
    },
    index=["t-test (total_ads)", "Fisher's exact (conversion)"],
)
print()
print("=" * 70)
print("SUMMARY: significant comparisons by correction method")
print("=" * 70)
print(summary)
summary.to_csv("results/correction_summary.csv")

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(summary.columns))
width = 0.35
ax.bar(x - width / 2, summary.loc["t-test (total_ads)"], width, label="t-test (total_ads)", color="#2E86AB")
ax.bar(x + width / 2, summary.loc["Fisher's exact (conversion)"], width, label="Fisher's exact (conversion)", color="#A23B72")
ax.set_xticks(x)
ax.set_xticklabels(summary.columns)
ax.set_ylabel("Number of significant comparisons (out of 21)")
ax.set_title("Effect of multiple comparisons correction")
ax.legend()
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("figures/correction_comparison.png", dpi=150)
plt.close(fig)
print("\nSaved figures/correction_comparison.png")

print()
print("=" * 70)
print("KEY INSIGHT")
print("=" * 70)
print(f"t-test family: {t_unc} of 21 comparisons looked 'significant' before correction, and {t_bonf} "
      f"(Bonferroni) / {t_fdr} (FDR) still do after correction — sample sizes per day (77k-93k users) "
      "are so large that even tiny, practically meaningless differences in mean ad exposure clear the "
      "corrected p-value bar. Every single one of those comparisons had a 'negligible' Cohen's d "
      "(|d| < 0.1, see ttest_comparisons output) — this is the textbook case of statistical significance without "
      "practical significance, and correction alone does not catch it. Effect size has to be checked too.")
print(f"Fisher's exact family: {f_unc} of 21 conversion-rate comparisons looked significant before "
      f"correction; {f_bonf} survive Bonferroni and {f_fdr} survive FDR — almost unchanged, again because "
      "the sample sizes are large. Unlike the t-test family, several of these rate differences are also "
      "large in relative terms (10-35%), so they are more likely to be practically meaningful.")
