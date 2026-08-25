"""
Part 5: confidence intervals, composite ranking, budget allocation.

Outputs:
  outputs/bootstrap_ci_cpa.csv
  outputs/composite_ranking.csv
  outputs/budget_allocation.csv
  figures/cpa_confidence_intervals.png
"""

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
BUDGET = 500_000
MIN_SHARE, MAX_SHARE = 0.03, 0.25

df = pd.read_csv("data/marketing_data.csv")
summary = pd.read_csv("outputs/campaign_summary.csv", index_col=0)


# ------------------------------------------------------------ bootstrap CI
def bootstrap_ci(data, n_bootstrap=2000, ci_level=0.95):
    data = np.asarray(data, dtype=float)
    data = data[np.isfinite(data)]
    if len(data) < 3:
        return np.nan, np.nan
    means = rng.choice(data, size=(n_bootstrap, len(data)), replace=True).mean(axis=1)
    lo = (1 - ci_level) / 2 * 100
    return float(np.percentile(means, lo)), float(np.percentile(means, 100 - lo))


rows = []
for camp, sub in df.groupby("campaign_name"):
    cpa_vals = sub["cpa"].dropna()
    roas_vals = sub["roas"].dropna()
    lo_c, hi_c = bootstrap_ci(cpa_vals)
    lo_r, hi_r = bootstrap_ci(roas_vals)
    rows.append(dict(campaign=camp, n_days=len(cpa_vals),
                     mean_daily_cpa=cpa_vals.mean(),
                     cpa_ci_low=lo_c, cpa_ci_high=hi_c,
                     ci_width_pct=100 * (hi_c - lo_c) / cpa_vals.mean(),
                     mean_daily_roas=roas_vals.mean(),
                     roas_ci_low=lo_r, roas_ci_high=hi_r))
ci = pd.DataFrame(rows).sort_values("mean_daily_cpa")
ci.round(3).to_csv("outputs/bootstrap_ci_cpa.csv", index=False)

print("=" * 78)
print("BOOTSTRAP 95% CONFIDENCE INTERVALS ON DAILY MEANS (2000 resamples)")
print("=" * 78)
print(ci.round(3).to_string(index=False))

overlap = []
c = ci.set_index("campaign")
for a in c.index:
    for b in c.index:
        if a < b and not (c.loc[a, "cpa_ci_high"] < c.loc[b, "cpa_ci_low"]
                          or c.loc[b, "cpa_ci_high"] < c.loc[a, "cpa_ci_low"]):
            overlap.append((a, b))
print(f"\ncampaign pairs whose CPA confidence intervals overlap: {len(overlap)} of 55")

fig, ax = plt.subplots(figsize=(10, 7))
o = ci.sort_values("mean_daily_cpa")
ax.errorbar(o.mean_daily_cpa, range(len(o)),
            xerr=[o.mean_daily_cpa - o.cpa_ci_low, o.cpa_ci_high - o.mean_daily_cpa],
            fmt="o", capsize=4, color="#2e86c1")
ax.set_yticks(range(len(o)))
ax.set_yticklabels(o.campaign)
ax.set_xlabel("mean daily CPA with bootstrap 95% CI")
ax.set_title("Where the estimates actually sit, with uncertainty")
fig.tight_layout()
fig.savefig("figures/cpa_confidence_intervals.png", dpi=150)
plt.close(fig)

# --------------------------------------------------------- composite ranking
r = summary.copy()
r["rank_cpa"] = r["CPA"].rank(ascending=True)      # lower CPA is better
r["rank_roas"] = r["ROAS"].rank(ascending=False)   # higher ROAS is better
r["composite_rank"] = 0.5 * r["rank_cpa"] + 0.5 * r["rank_roas"]
r["score"] = len(r) + 1 - r["composite_rank"]      # higher score is better
r = r.sort_values("score", ascending=False)
r[["CPA", "ROAS", "profit", "rank_cpa", "rank_roas", "composite_rank", "score"]] \
    .round(3).to_csv("outputs/composite_ranking.csv")

print("\n" + "=" * 78)
print("COMPOSITE RANKING (50% CPA rank, 50% ROAS rank)")
print("=" * 78)
print(r[["CPA", "ROAS", "profit", "composite_rank", "score"]].round(2).to_string())

# ------------------------------------------------------------- allocation
# Two allocations are produced deliberately.
#
# A. Template allocation: budget proportional to composite score, capped.
#    Ranks discard magnitude, so a campaign returning 0.11 on spend gets a
#    floor allocation only because it is not last on every metric.
#
# B. Profitability screen: campaigns below break-even ROAS get a test budget
#    only, and the released spend goes to campaigns with proven positive
#    return, still capped to avoid assuming linear scaling.
raw = r["score"] / r["score"].sum()
capped = raw.clip(MIN_SHARE, MAX_SHARE)
alloc_a = capped / capped.sum()

profitable = r["ROAS"] >= 1.0
share_b = pd.Series(0.0, index=r.index)
share_b[~profitable] = MIN_SHARE
remaining = 1 - share_b.sum()
w = r.loc[profitable, "score"] / r.loc[profitable, "score"].sum()
share_b[profitable] = (w * remaining).clip(upper=MAX_SHARE)
share_b = share_b / share_b.sum()

alloc = pd.DataFrame({
    "current_share": (r["spend"] / r["spend"].sum()),
    "alloc_A_rank_proportional": alloc_a,
    "alloc_B_profit_screened": share_b,
    "ROAS": r["ROAS"], "CPA": r["CPA"],
})
alloc["A_budget"] = (alloc["alloc_A_rank_proportional"] * BUDGET).round(0)
alloc["B_budget"] = (alloc["alloc_B_profit_screened"] * BUDGET).round(0)
alloc["change_vs_current_B_pp"] = 100 * (alloc["alloc_B_profit_screened"]
                                         - alloc["current_share"])
alloc.round(4).to_csv("outputs/budget_allocation.csv")

print("\n" + "=" * 78)
print(f"BUDGET ALLOCATION OPTIONS ON ${BUDGET:,}/month")
print("=" * 78)
show = alloc.copy()
for col in ["current_share", "alloc_A_rank_proportional", "alloc_B_profit_screened"]:
    show[col] = (100 * show[col]).round(1)
print(show[["ROAS", "current_share", "alloc_A_rank_proportional",
            "alloc_B_profit_screened", "B_budget", "change_vs_current_B_pp"]]
      .round(1).to_string())

print(f"\nspend currently going to campaigns with ROAS below 1.0: "
      f"{100 * alloc.loc[alloc.ROAS < 1, 'current_share'].sum():.1f}% of budget")
print("\nPart 5 complete.")
