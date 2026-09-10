"""
Part 5: Business Recommendations
Lab: In God we trust, everyone else bring the data

Synthesizes the FDR-corrected statistical findings into confidence intervals,
a composite channel ranking, and a proposed $500K/month budget allocation.
Numbers printed here are pulled directly into executive_memo.md.
"""

import numpy as np
import pandas as pd

GROUP_COL = "channel"
MONTHLY_BUDGET = 500_000
MIN_ALLOCATION_PCT = 0.05  # floor per channel (avoid abandoning a channel entirely)
MAX_ALLOCATION_PCT = 0.40  # ceiling per channel (avoid over-concentration risk)

rng = np.random.default_rng(7)

daily = pd.read_csv("data/marketing_data.csv", parse_dates=["date"])
channel_summary = pd.read_csv("data/channel_summary.csv")
ttest_results = pd.read_csv("data/ttest_cpa_results.csv")
fisher_results = pd.read_csv("data/fisher_conversion_results.csv")

# ===========================================================================
# 1. Summary of statistically significant findings (FDR-corrected)
# ===========================================================================
print("=== Significant CPA Differences (FDR-corrected) ===")
sig_cpa = ttest_results[ttest_results["significant_fdr"]].copy()
for _, r in sig_cpa.iterrows():
    lower_channel = r["group_a"] if r["mean_a"] < r["mean_b"] else r["group_b"]
    higher_channel = r["group_b"] if r["mean_a"] < r["mean_b"] else r["group_a"]
    abs_diff = abs(r["mean_a"] - r["mean_b"])
    print(f"  {lower_channel} has lower CPA than {higher_channel} by ${abs_diff:.2f} "
          f"(p_fdr={r['p_value_fdr']:.2e}, Cohen's d={r['cohens_d']:.2f}, {r['effect_size']})")

print("\n=== Significant Conversion Rate Differences (FDR-corrected) ===")
sig_fisher = fisher_results[fisher_results["significant_fdr"]].copy()
for _, r in sig_fisher.iterrows():
    higher_channel = r["group_a"] if r["rate_a"] > r["rate_b"] else r["group_b"]
    lower_channel = r["group_b"] if r["rate_a"] > r["rate_b"] else r["group_a"]
    abs_diff = abs(r["rate_a"] - r["rate_b"])
    print(f"  {higher_channel} has higher conversion rate than {lower_channel} by {abs_diff*100:.2f}pp "
          f"(p_fdr={r['p_value_fdr']:.2e})")

# ===========================================================================
# 2. Bootstrap confidence intervals for CPA by channel
# ===========================================================================
def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    data = np.asarray(data)
    means = np.empty(n_bootstrap)
    n = len(data)
    for i in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        means[i] = sample.mean()
    alpha = 1 - ci_level
    lower = np.percentile(means, 100 * (alpha / 2))
    upper = np.percentile(means, 100 * (1 - alpha / 2))
    return lower, upper


ci_rows = []
for ch in sorted(daily[GROUP_COL].unique()):
    vals = daily.loc[daily[GROUP_COL] == ch, "cpa"].dropna()
    vals = vals[np.isfinite(vals)]
    lower, upper = bootstrap_ci(vals, n_bootstrap=1000, ci_level=0.95)
    ci_rows.append(dict(channel=ch, mean_cpa=vals.mean(), ci_lower=lower, ci_upper=upper, n=len(vals)))

ci_df = pd.DataFrame(ci_rows).sort_values("mean_cpa")
print("\n=== 95% Bootstrap Confidence Intervals for CPA ===")
print(ci_df.round(2).to_string(index=False))
ci_df.round(2).to_csv("data/cpa_confidence_intervals.csv", index=False)

# ===========================================================================
# 3. Composite ranking (CPA + ROAS, 50/50) and budget allocation
# ===========================================================================
rank_df = channel_summary[[GROUP_COL, "cpa", "roas", "conversion_rate", "conversions", "profit"]].copy()
rank_df["rank_cpa"] = rank_df["cpa"].rank(ascending=True)   # lower CPA = better = rank 1
rank_df["rank_roas"] = rank_df["roas"].rank(ascending=False)  # higher ROAS = better = rank 1
rank_df["composite_score"] = 0.5 * rank_df["rank_cpa"] + 0.5 * rank_df["rank_roas"]
rank_df = rank_df.sort_values("composite_score")

print("\n=== Composite Channel Ranking (50% CPA rank + 50% ROAS rank; lower score = better) ===")
print(rank_df.round(3).to_string(index=False))
rank_df.round(3).to_csv("data/composite_ranking.csv", index=False)

# Inverse-score weighting for allocation: better (lower) composite score -> more budget
max_score = rank_df["composite_score"].max()
rank_df["inv_score"] = (max_score + 1) - rank_df["composite_score"]
raw_weight = rank_df["inv_score"] / rank_df["inv_score"].sum()
rank_df["raw_allocation_pct"] = raw_weight

# Apply min/max constraints, then renormalize
alloc = rank_df["raw_allocation_pct"].clip(lower=MIN_ALLOCATION_PCT, upper=MAX_ALLOCATION_PCT)
alloc = alloc / alloc.sum()
rank_df["allocation_pct"] = alloc
rank_df["allocation_amount"] = (alloc * MONTHLY_BUDGET).round(0)

alloc_table = rank_df[[GROUP_COL, "composite_score", "allocation_pct", "allocation_amount"]].sort_values(
    "allocation_amount", ascending=False
)
print(f"\n=== Proposed Monthly Budget Allocation (${MONTHLY_BUDGET:,}) ===")
print(alloc_table.round(4).to_string(index=False))
alloc_table.round(2).to_csv("data/budget_allocation.csv", index=False)

print(f"\nTotal allocated: ${alloc_table['allocation_amount'].sum():,.0f}")

print("\nBusiness recommendations complete.")
