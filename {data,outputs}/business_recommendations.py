"""
Part 5: Business Recommendations
Marketing Channel Budget Allocation Lab
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
MONTHLY_BUDGET = 500_000
MIN_ALLOC_PCT = 0.08   # floor per channel (keep every channel alive for testing)
MAX_ALLOC_PCT = 0.30   # ceiling per channel (avoid over-concentration risk)

df = pd.read_csv("data/marketing_data.csv")
group_summary = pd.read_csv("outputs/group_summary.csv", index_col="Channel")


def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    means = [RNG.choice(data, size=len(data), replace=True).mean() for _ in range(n_bootstrap)]
    lower = np.percentile(means, (1 - ci_level) / 2 * 100)
    upper = np.percentile(means, (1 + ci_level) / 2 * 100)
    return lower, upper


ci_rows = []
for ch, sub in df.groupby("Channel"):
    lo, hi = bootstrap_ci(sub["CPA"].values)
    ci_rows.append({"Channel": ch, "mean_CPA": round(sub["CPA"].mean(), 2),
                     "CI_lower_95": round(lo, 2), "CI_upper_95": round(hi, 2)})
ci_df = pd.DataFrame(ci_rows).set_index("Channel")
print("Bootstrap 95% CI for mean CPA:\n", ci_df)
ci_df.to_csv("outputs/bootstrap_ci_cpa.csv")

# ---------------------------------------------------------------------------
# Composite ranking: 50% CPA rank (lower better) + 50% ROAS rank (higher better)
# ---------------------------------------------------------------------------
ranking = group_summary[["mean_CPA", "mean_ROAS"]].copy()
ranking["rank_CPA"] = ranking["mean_CPA"].rank(ascending=True)     # 1 = lowest (best) CPA
ranking["rank_ROAS"] = ranking["mean_ROAS"].rank(ascending=False)  # 1 = highest (best) ROAS
ranking["composite_score"] = 0.5 * ranking["rank_CPA"] + 0.5 * ranking["rank_ROAS"]
ranking = ranking.sort_values("composite_score")
print("\nComposite ranking (lower score = better):\n", ranking)
ranking.to_csv("outputs/composite_ranking.csv")

# ---------------------------------------------------------------------------
# Budget allocation proportional to inverse composite score, with floor/ceiling
# ---------------------------------------------------------------------------
inv_score = 1 / ranking["composite_score"]
raw_alloc_pct = inv_score / inv_score.sum()
alloc_pct = raw_alloc_pct.clip(lower=MIN_ALLOC_PCT, upper=MAX_ALLOC_PCT)
alloc_pct = alloc_pct / alloc_pct.sum()  # renormalize after clipping
alloc_df = pd.DataFrame({
    "channel": ranking.index,
    "composite_score": ranking["composite_score"].values,
    "allocation_pct": (alloc_pct.values * 100).round(1),
    "allocation_usd": (alloc_pct.values * MONTHLY_BUDGET).round(0),
})
alloc_df = alloc_df.sort_values("allocation_usd", ascending=False)
print("\nBudget allocation recommendation:\n", alloc_df)
alloc_df.to_csv("outputs/budget_allocation.csv", index=False)
print("\nTotal allocated:", alloc_df["allocation_usd"].sum())

print("\n=== Part 5 (quant support) complete ===")
