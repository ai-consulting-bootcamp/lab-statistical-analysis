"""
Step 8: Synthesize Findings and Create Recommendations
==========================================================
Bootstrap confidence intervals, composite ranking, and a day-of-week ad
delivery weighting recommendation, all built only from FDR-corrected,
real findings from Steps 2-7.
"""
import os

import numpy as np
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)
rng = np.random.default_rng(7)

df = pd.read_csv("data/marketing_data.csv")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ttest_corrected = pd.read_csv("results/ttest_results_corrected.csv")
fisher_corrected = pd.read_csv("results/fisher_results_corrected.csv")
arm_df = pd.read_csv("results/fisher_results_ad_vs_psa.csv")

# 1. Summary of significant findings (FDR-corrected) ---------------------------
print("=" * 70)
print("SIGNIFICANT FINDINGS AFTER FDR CORRECTION")
print("=" * 70)

sig_conv = fisher_corrected[fisher_corrected["significant_fdr"]].copy()
sig_conv["higher_rate_group"] = np.where(sig_conv["difference"] > 0, sig_conv["group_b"], sig_conv["group_a"])
print(f"\nConversion-rate pairs significant after FDR: {len(sig_conv)} of {len(fisher_corrected)}")
print(sig_conv[["group_a", "group_b", "higher_rate_group", "difference", "p_value_fdr"]].round(6).to_string(index=False))

sig_ads = ttest_corrected[ttest_corrected["significant_fdr"]].copy()
print(f"\ntotal_ads pairs significant after FDR: {len(sig_ads)} of {len(ttest_corrected)} "
      "(all have negligible Cohen's d — see ttest_comparisons/multiple_comparisons_correction output; not practically meaningful)")

print(f"\nHeadline experimental finding (ad vs. psa): conversion rate "
      f"{arm_df.loc[0, 'rate_a']:.4%} (ad) vs {arm_df.loc[0, 'rate_b']:.4%} (psa), "
      f"a {arm_df.loc[0, 'pct_difference']:+.1f}% relative difference, "
      f"p={arm_df.loc[0, 'p_value']:.2e}, odds ratio={arm_df.loc[0, 'odds_ratio']:.2f}.")

# 2. Bootstrap confidence intervals ---------------------------------------------
def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    data = np.asarray(data)
    boot_means = np.empty(n_bootstrap)
    n = len(data)
    for i in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        boot_means[i] = sample.mean()
    alpha = 1 - ci_level
    lower = np.percentile(boot_means, 100 * (alpha / 2))
    upper = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return lower, upper


print()
print("=" * 70)
print("BOOTSTRAP 95% CONFIDENCE INTERVALS BY most_ads_day")
print("=" * 70)

ci_rows = []
for day in day_order:
    subset = df[df["most_ads_day"] == day]
    ads_lo, ads_hi = bootstrap_ci(subset["total_ads"].values, n_bootstrap=1000)
    conv_lo, conv_hi = bootstrap_ci(subset["converted"].astype(float).values, n_bootstrap=1000)
    ci_rows.append(
        {
            "most_ads_day": day,
            "n": len(subset),
            "mean_total_ads": subset["total_ads"].mean(),
            "total_ads_ci_lower": ads_lo,
            "total_ads_ci_upper": ads_hi,
            "conversion_rate": subset["converted"].mean(),
            "conversion_rate_ci_lower": conv_lo,
            "conversion_rate_ci_upper": conv_hi,
        }
    )

ci_df = pd.DataFrame(ci_rows).round(4)
print(ci_df.to_string(index=False))
ci_df.to_csv("results/confidence_intervals.csv", index=False)

# 3. Composite ranking and ad-delivery weighting recommendation ----------------
# Only conversion_rate has an unambiguous "higher is better" direction without
# cost data — total_ads (exposure) is reported for context but is not used to
# rank groups, since more/less exposure isn't inherently good or bad here.
rank_df = ci_df[["most_ads_day", "conversion_rate", "mean_total_ads", "n"]].copy()
rank_df["rank"] = rank_df["conversion_rate"].rank(ascending=False).astype(int)
rank_df = rank_df.sort_values("rank")

# Composite score = normalized conversion rate, used as allocation weight.
raw_weight = rank_df["conversion_rate"] - rank_df["conversion_rate"].min() + 0.001
rank_df["composite_score"] = raw_weight / raw_weight.sum()

# Apply reasonable constraints: no day below 8% or above 25% of weight.
# Plain clip-then-renormalize can push clipped values back outside the bounds
# (renormalizing divides by a smaller post-clip total), so redistribute
# iteratively ("water-filling") until every share truly sits within bounds.
MIN_SHARE, MAX_SHARE = 0.08, 0.25


def constrained_allocation(scores, min_share, max_share, tol=1e-9):
    shares = (scores / scores.sum()).to_numpy(dtype=float)
    fixed = np.zeros(len(shares), dtype=bool)
    for _ in range(100):
        free = ~fixed
        free_total = shares[free].sum()
        if free_total > 0:
            shares[free] = shares[free] / free_total * (1 - shares[fixed].sum())
        over = free & (shares > max_share + tol)
        under = free & (shares < min_share - tol)
        if not over.any() and not under.any():
            break
        shares[over] = max_share
        shares[under] = min_share
        fixed = fixed | over | under
    return shares


rank_df["allocation_pct"] = constrained_allocation(rank_df["composite_score"], MIN_SHARE, MAX_SHARE)

TOTAL_BUDGET = 500_000  # from the lab scenario; illustrative only (see memo caveats)
rank_df["illustrative_allocation_usd"] = (rank_df["allocation_pct"] * TOTAL_BUDGET).round(0)

print()
print("=" * 70)
print("COMPOSITE RANKING & AD-DELIVERY WEIGHTING RECOMMENDATION")
print("=" * 70)
print(rank_df.round(4).to_string(index=False))
rank_df.to_csv("results/allocation_recommendation.csv", index=False)

print()
print("NOTE: this dataset has no per-channel cost/revenue data, so the table above allocates a "
      "*day-of-week ad delivery schedule weight* (a real, actionable lever — e.g. Google/Meta Ads "
      "dayparting bid adjustments), not a literal channel budget split. The $500K figure from the lab "
      "scenario is applied only as an illustrative example of how the weighting would translate to a "
      "budget number, and should not be read as a validated allocation of real ad spend by channel.")
