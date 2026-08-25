"""
Step 5: Compare Binary Outcomes Using Fisher's Exact Test
=============================================================
Pairwise Fisher's exact tests on conversion rate (Conversions / Clicks, per the lab's
conversion-rate formula) across the 5 Campaign_Type groups.
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
groups = sorted(df["Campaign_Type"].unique())


def run_pairwise_fisher(data, group_col, groups):
    # total_clicks is the denominator ("attempts"): conversion rate = conversions / clicks,
    # matching the CTR/conversion-rate formulas used in key_metrics.py.
    agg = data.groupby(group_col, observed=True).agg(
        conversions=("Conversions", "sum"), total_clicks=("Clicks", "sum")
    )
    agg["non_conversions"] = agg["total_clicks"] - agg["conversions"]
    agg["rate"] = agg["conversions"] / agg["total_clicks"]
    print(agg.round(4))
    print()

    results = []
    for group_a, group_b in itertools.combinations(groups, 2):
        conv_a, tot_a, nonconv_a = agg.loc[group_a, ["conversions", "total_clicks", "non_conversions"]]
        conv_b, tot_b, nonconv_b = agg.loc[group_b, ["conversions", "total_clicks", "non_conversions"]]

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
            f"{group_a:>12} vs {group_b:<12} | rate_a={rate_a:.4%} rate_b={rate_b:.4%} "
            f"diff={diff:+.4%} ({pct_diff:+6.2f}%) | OR={odds_ratio:.3f} p={p_value:.4e}"
        )

    return pd.DataFrame(results), agg


# 1. Pairwise Fisher's exact across Campaign_Type (5 groups, 10 pairs) --------
print("=" * 70)
print("CONVERSION SUMMARY BY Campaign_Type")
print("=" * 70)
fisher_df, group_agg = run_pairwise_fisher(df, "Campaign_Type", groups)
fisher_df.to_csv("results/fisher_results_by_campaign_type.csv", index=False)

n_sig = fisher_df["significant_uncorrected"].sum()
print()
print(f"Total comparisons: {len(fisher_df)} | Significant at alpha=0.05 (uncorrected): {n_sig}")

# 2. Compact summary of significant pairs + practical-meaningfulness takeaway -----------
# "Practically meaningful" here is a rough screen (>=10% relative difference), not a formal
# effect-size threshold — Step 6 (FDR correction) is what actually decides which findings
# (if any) should drive the budget recommendation.
sig_pairs = fisher_df[fisher_df["significant_uncorrected"]].copy()
if len(sig_pairs) > 0:
    sig_pairs["practically_meaningful"] = sig_pairs["pct_difference"].abs() >= 10
    print()
    print("Significant pairs (uncorrected) — rate difference and a rough practical-meaningfulness screen:")
    print(
        sig_pairs[["group_a", "group_b", "rate_a", "rate_b", "pct_difference", "p_value", "practically_meaningful"]]
        .sort_values("pct_difference", key=abs, ascending=False)
        .round(4)
        .to_string(index=False)
    )
else:
    print("\nNo pairs significant at alpha=0.05 (uncorrected) — no evidence of a conversion-rate "
          "difference by Campaign_Type in this dataset.")

# 3. Visualize rate comparisons (by Campaign_Type) ----------------------------
sorted_agg = group_agg.sort_values("rate")
overall_rate = df["Conversions"].sum() / df["Clicks"].sum() * 100
best_group, worst_group = sorted_agg["rate"].idxmax(), sorted_agg["rate"].idxmin()
fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(sorted_agg.index.astype(str), sorted_agg["rate"] * 100, color="#2E86AB")
for bar, rate in zip(bars, sorted_agg["rate"]):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
             f"{rate:.2%}", va="center", fontsize=9)
ax.axvline(overall_rate, color="gray", linestyle="--", linewidth=1, label=f"Overall rate ({overall_rate:.2f}%)")
ax.set_xlabel("Conversion rate (%) [conversions / clicks]")
ax.set_title(f"Conversion rate by Campaign_Type\nHighest: {best_group} · Lowest: {worst_group}")
ax.legend(fontsize=8)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig("figures/rate_comparison.png", dpi=150)
plt.close(fig)
print()
print("Saved figures/rate_comparison.png")
