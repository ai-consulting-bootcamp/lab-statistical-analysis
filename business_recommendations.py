"""
business_recommendations.py
Part 5: Synthesize findings into business recommendations
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
ALPHA = 0.05

df = pd.read_csv("marketing_data.csv")
channel_summary = pd.read_csv("output/data/channel_summary.csv")
ttest_df = pd.read_csv("output/data/cpa_ttest_results.csv")
fisher_df = pd.read_csv("output/data/conversion_rate_fisher_results.csv")

# ---------------------------------------------------------------
# Bootstrap 95% CI for mean CPA per channel
# ---------------------------------------------------------------
def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    data = np.asarray(data)
    boot_means = np.array([
        rng.choice(data, size=len(data), replace=True).mean()
        for _ in range(n_bootstrap)
    ])
    lo = np.percentile(boot_means, (1 - ci_level) / 2 * 100)
    hi = np.percentile(boot_means, (1 + ci_level) / 2 * 100)
    return lo, hi

ci_rows = []
for ch in sorted(df["Marketing_Channel"].unique()):
    vals = df.loc[df.Marketing_Channel == ch, "CPA"].replace([np.inf, -np.inf], np.nan).dropna()
    lo, hi = bootstrap_ci(vals.values)
    ci_rows.append({"channel": ch, "mean_CPA": vals.mean(), "ci95_lower": lo, "ci95_upper": hi,
                     "n": len(vals)})

ci_df = pd.DataFrame(ci_rows)
print("=== 95% Bootstrap CI for mean CPA by channel ===")
print(ci_df.round(3).to_string(index=False))
ci_df.to_csv("output/data/cpa_confidence_intervals.csv", index=False)

# ---------------------------------------------------------------
# Composite ranking: lower CPA is better, higher ROAS is better (50/50)
# ---------------------------------------------------------------
cs = channel_summary.copy()
cs["rank_cpa"] = cs["CPA"].rank(ascending=True)   # lower is better -> rank 1 = best
cs["rank_roas"] = cs["ROAS"].rank(ascending=False)  # higher is better -> rank 1 = best
cs["composite_score"] = 0.5 * cs["rank_cpa"] + 0.5 * cs["rank_roas"]
cs = cs.sort_values("composite_score")
print("\n=== Composite ranking (50% CPA rank + 50% ROAS rank; lower score = better) ===")
print(cs[["Marketing_Channel", "CPA", "ROAS", "rank_cpa", "rank_roas", "composite_score"]]
      .round(3).to_string(index=False))

# ---------------------------------------------------------------
# Budget allocation recommendation
# ---------------------------------------------------------------
TOTAL_BUDGET = 500_000
MIN_PCT, MAX_PCT = 0.10, 0.40  # guardrails: no channel gets <10% or >40%

# Inverse composite score -> weight (lower score = better = higher weight)
inv = 1 / cs["composite_score"]
weights = inv / inv.sum()
cs["raw_allocation_pct"] = weights.values

# Apply guardrails then renormalize
capped = cs["raw_allocation_pct"].clip(MIN_PCT, MAX_PCT)
capped = capped / capped.sum()
cs["allocation_pct"] = capped
cs["allocation_usd"] = (capped * TOTAL_BUDGET).round(0)

print(f"\n=== Recommended monthly allocation of ${TOTAL_BUDGET:,} "
      f"(guardrails: {MIN_PCT:.0%}-{MAX_PCT:.0%} per channel) ===")
alloc_display = cs[["Marketing_Channel", "composite_score", "allocation_pct", "allocation_usd"]].copy()
alloc_display["allocation_pct"] = (alloc_display["allocation_pct"] * 100).round(1)
print(alloc_display.to_string(index=False))
cs.to_csv("output/data/budget_allocation.csv", index=False)

# ---------------------------------------------------------------
# Significant findings summary (post FDR correction)
# ---------------------------------------------------------------
sig_cpa = ttest_df[ttest_df["significant_fdr"]] if "significant_fdr" in ttest_df.columns else ttest_df.iloc[0:0]
sig_fisher = fisher_df[fisher_df["significant_fdr"]] if "significant_fdr" in fisher_df.columns else fisher_df.iloc[0:0]

print(f"\n=== Statistically significant findings after FDR correction ===")
print(f"CPA differences: {len(sig_cpa)} of {len(ttest_df)} pairs")
print(f"Conversion-rate differences: {len(sig_fisher)} of {len(fisher_df)} pairs")
if len(sig_fisher):
    for _, r in sig_fisher.iterrows():
        better = r["group_a"] if r["rate_a"] > r["rate_b"] else r["group_b"]
        print(f"  {r['group_a']} vs {r['group_b']}: {better} has the higher conversion rate "
              f"(p_fdr={r['p_value_fdr']:.2e})")

print("\nPart 5 numeric work complete. See executive_memo.md for narrative.")
