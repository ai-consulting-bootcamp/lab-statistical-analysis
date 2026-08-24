"""
Step 5: Compare Binary Outcomes Using Fisher's Exact Test
=============================================================
Pairwise Fisher's exact tests on `converted` across the 7 most_ads_day groups,
plus the headline ad-vs-psa experimental comparison.
"""
import itertools
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import fisher_exact

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)

df = pd.read_csv("data/marketing_data.csv")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def run_pairwise_fisher(data, group_col, groups):
    agg = data.groupby(group_col, observed=True)["converted"].agg(
        conversions="sum", total_attempts="count"
    )
    agg["non_conversions"] = agg["total_attempts"] - agg["conversions"]
    agg["rate"] = agg["conversions"] / agg["total_attempts"]
    print(agg.round(4))
    print()

    results = []
    for group_a, group_b in itertools.combinations(groups, 2):
        conv_a, tot_a, nonconv_a = agg.loc[group_a, ["conversions", "total_attempts", "non_conversions"]]
        conv_b, tot_b, nonconv_b = agg.loc[group_b, ["conversions", "total_attempts", "non_conversions"]]

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


# 1. Pairwise Fisher's exact across most_ads_day (7 groups, 21 pairs) --------
print("=" * 70)
print("CONVERSION SUMMARY BY most_ads_day")
print("=" * 70)
fisher_df, day_agg = run_pairwise_fisher(df, "most_ads_day", day_order)
fisher_df.to_csv("results/fisher_results_by_day.csv", index=False)

n_sig = fisher_df["significant_uncorrected"].sum()
print()
print(f"Total comparisons: {len(fisher_df)} | Significant at alpha=0.05 (uncorrected): {n_sig}")

# 2. Headline comparison: test_group (ad vs. psa) ----------------------------
print()
print("=" * 70)
print("HEADLINE COMPARISON: test_group (ad vs. psa)")
print("=" * 70)
arm_df, arm_agg = run_pairwise_fisher(df, "test_group", ["ad", "psa"])
arm_df.to_csv("results/fisher_results_ad_vs_psa.csv", index=False)

# 3. Visualize rate comparisons (by most_ads_day) ----------------------------
sorted_agg = day_agg.sort_values("rate")
fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(sorted_agg.index.astype(str), sorted_agg["rate"] * 100, color="#2E86AB")
for bar, rate in zip(bars, sorted_agg["rate"]):
    ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
             f"{rate:.2%}", va="center", fontsize=9)
ax.set_xlabel("Conversion rate (%)")
ax.set_title("Conversion rate by most_ads_day")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig("figures/rate_comparison.png", dpi=150)
plt.close(fig)
print()
print("Saved figures/rate_comparison.png")
