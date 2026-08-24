"""
Step 5: Compare Binary Outcomes Using Fisher's Exact Test
=============================================================
Two binary-outcome (`converted`) comparisons, both required by this step:

  1. HEADLINE: test_group (ad vs. psa) — the dataset's actual randomized
     experiment arm, and the primary binary-outcome comparison this lab asks for.
  2. SECONDARY: most_ads_day (7 groups, 21 pairs) — day-of-week is not an
     experiment arm, but it's the only other categorical grouping variable
     this dataset supports (see dataset_selection.md), and it's what drives
     the ad-delivery-timing recommendation in business_recommendations.py.
     Read these as descriptive/exploratory, not causal, comparisons.
"""
import itertools
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import fisher_exact

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)

os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)

df = pd.read_csv("data/marketing_data.csv")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def run_pairwise_fisher(data, group_col, groups):
    # total_users: the outcome here is one conversion decision per user, not repeated
    # trials, so "users" (not "attempts") is the accurate denominator label.
    agg = data.groupby(group_col, observed=True)["converted"].agg(
        conversions="sum", total_users="count"
    )
    agg["non_conversions"] = agg["total_users"] - agg["conversions"]
    agg["rate"] = agg["conversions"] / agg["total_users"]
    print(agg.round(4))
    print()

    results = []
    for group_a, group_b in itertools.combinations(groups, 2):
        conv_a, tot_a, nonconv_a = agg.loc[group_a, ["conversions", "total_users", "non_conversions"]]
        conv_b, tot_b, nonconv_b = agg.loc[group_b, ["conversions", "total_users", "non_conversions"]]

        table = [[conv_a, nonconv_a], [conv_b, nonconv_b]]
        odds_ratio, p_value = fisher_exact(table, alternative="two-sided")

        rate_a, rate_b = conv_a / tot_a, conv_b / tot_b
        diff = rate_b - rate_a
        pct_diff = (diff / rate_a) * 100 if rate_a else np.nan

        results.append(
            {
                "group_a": group_a,
                "group_b": group_b,
                "conversions_a": conv_a,
                "total_a": tot_a,
                "rate_a": rate_a,
                "conversions_b": conv_b,
                "total_b": tot_b,
                "rate_b": rate_b,
                "difference": diff,
                "pct_difference": pct_diff,
                "odds_ratio": odds_ratio,
                "p_value": p_value,
                "significant_uncorrected": p_value < 0.05,
            }
        )
        print(
            f"{group_a:>9} vs {group_b:<9} | rate_a={rate_a:.4%} rate_b={rate_b:.4%} "
            f"diff={diff:+.4%} ({pct_diff:+6.2f}%) | OR={odds_ratio:.3f} p={p_value:.4e}"
        )

    return pd.DataFrame(results), agg


# 1. HEADLINE comparison: test_group (ad vs. psa), the randomized experiment arm --------
print("=" * 70)
print("HEADLINE COMPARISON: test_group (ad vs. psa)")
print("=" * 70)
arm_df, arm_agg = run_pairwise_fisher(df, "test_group", ["ad", "psa"])
arm_df.to_csv("results/fisher_results_ad_vs_psa.csv", index=False)
print(
    f"\nTakeaway: ad vs. psa differ by {arm_df.loc[0, 'pct_difference']:+.1f}% relative "
    f"(p={arm_df.loc[0, 'p_value']:.2e}) — statistically significant and, at this size of "
    "relative difference, also practically meaningful for the experiment's core question "
    "(does showing the ad increase conversion vs. the psa control)."
)

# 2. SECONDARY comparison: most_ads_day (7 groups, 21 pairs, descriptive/exploratory) ----
print()
print("=" * 70)
print("CONVERSION SUMMARY BY most_ads_day (secondary grouping — see module docstring)")
print("=" * 70)
fisher_df, day_agg = run_pairwise_fisher(df, "most_ads_day", day_order)
fisher_df.to_csv("results/fisher_results_by_day.csv", index=False)

n_sig = fisher_df["significant_uncorrected"].sum()
print()
print(f"Total comparisons: {len(fisher_df)} | Significant at alpha=0.05 (uncorrected): {n_sig}")

# 2b. Compact summary of significant pairs + practical-meaningfulness takeaway -----------
# "Practically meaningful" here is a rough screen (>=10% relative difference), not a formal
# effect-size threshold — Step 6 (FDR correction) and business_recommendations.py are what
# actually decide which of these findings drive the recommendation.
sig_pairs = fisher_df[fisher_df["significant_uncorrected"]].copy()
sig_pairs["practically_meaningful"] = sig_pairs["pct_difference"].abs() >= 10
print()
print("Significant pairs (uncorrected) — rate difference and a rough practical-meaningfulness screen:")
print(
    sig_pairs[["group_a", "group_b", "rate_a", "rate_b", "pct_difference", "p_value", "practically_meaningful"]]
    .sort_values("pct_difference", key=abs, ascending=False)
    .round(4)
    .to_string(index=False)
)
n_meaningful = sig_pairs["practically_meaningful"].sum()
print(
    f"\nTakeaway: {n_sig} of {len(fisher_df)} most_ads_day pairs are significant before correction; "
    f"{n_meaningful} of those also clear a >=10% relative-difference screen for practical relevance. "
    "See multiple_comparisons_correction.py for which of these survive FDR/Bonferroni correction."
)

# 3. Visualize rate comparisons (by most_ads_day) ----------------------------
sorted_agg = day_agg.sort_values("rate")
overall_rate = df["converted"].mean() * 100
best_day, worst_day = sorted_agg["rate"].idxmax(), sorted_agg["rate"].idxmin()
fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(sorted_agg.index.astype(str), sorted_agg["rate"] * 100, color="#2E86AB")
for bar, rate in zip(bars, sorted_agg["rate"]):
    ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
             f"{rate:.2%}", va="center", fontsize=9)
ax.axvline(overall_rate, color="gray", linestyle="--", linewidth=1, label=f"Overall rate ({overall_rate:.2f}%)")
ax.set_xlabel("Conversion rate (%)")
ax.set_title(f"Conversion rate by most_ads_day\nHighest: {best_day} · Lowest: {worst_day}")
ax.legend(fontsize=8)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig("figures/rate_comparison.png", dpi=150)
plt.close(fig)
print()
print("Saved figures/rate_comparison.png")
