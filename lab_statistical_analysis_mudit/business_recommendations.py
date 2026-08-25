"""
Step 8: Synthesize Findings and Create Recommendations
==========================================================
Bootstrap confidence intervals, composite ranking (CPA + ROAS), and a channel
budget-allocation recommendation, all built only from FDR-corrected,
real findings from Steps 2-7.
"""
import os

import numpy as np
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)
rng = np.random.default_rng(7)

os.makedirs("results", exist_ok=True)

df = pd.read_csv("data/marketing_data.csv")
groups = sorted(df["Campaign_Type"].unique())

ttest_corrected = pd.read_csv("results/ttest_results_corrected.csv")
fisher_corrected = pd.read_csv("results/fisher_results_corrected.csv")
group_summary = pd.read_csv("results/group_summary_by_campaign_type.csv", index_col="Campaign_Type")

# 1. Summary of significant findings (FDR-corrected) ---------------------------
print("=" * 70)
print("SIGNIFICANT FINDINGS AFTER FDR CORRECTION")
print("=" * 70)

sig_cpa = ttest_corrected[ttest_corrected["significant_fdr"]].copy()
print(f"\nCPA pairs significant after FDR: {len(sig_cpa)} of {len(ttest_corrected)}")
if len(sig_cpa) == 0:
    print("None. CPA does not differ meaningfully by Campaign_Type — a genuine null result "
          "(every uncorrected p-value was already > 0.05; see ttest_comparisons output).")

sig_conv = fisher_corrected[fisher_corrected["significant_fdr"]].copy()
sig_conv["higher_rate_group"] = np.where(sig_conv["difference"] > 0, sig_conv["group_b"], sig_conv["group_a"])
print(f"\nConversion-rate pairs significant after FDR: {len(sig_conv)} of {len(fisher_corrected)} "
      "(all have sub-1% relative differences — statistically significant only because clicks are "
      "aggregated in the millions per group; see multiple_comparisons_correction output. Not "
      "practically meaningful.)")
print(sig_conv[["group_a", "group_b", "higher_rate_group", "pct_difference", "p_value_fdr"]].round(6).to_string(index=False))

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
print("BOOTSTRAP 95% CONFIDENCE INTERVALS BY Campaign_Type")
print("=" * 70)

ci_rows = []
for g in groups:
    subset = df[df["Campaign_Type"] == g]
    cpa_lo, cpa_hi = bootstrap_ci(subset["Acquisition_Cost"].values, n_bootstrap=1000)
    conv_rate_per_campaign = subset["Conversions"] / subset["Clicks"]
    conv_lo, conv_hi = bootstrap_ci(conv_rate_per_campaign.values, n_bootstrap=1000)
    ci_rows.append(
        {
            "Campaign_Type": g,
            "n": len(subset),
            "mean_cpa": subset["Acquisition_Cost"].mean(),
            "cpa_ci_lower": cpa_lo,
            "cpa_ci_upper": cpa_hi,
            "mean_conversion_rate": conv_rate_per_campaign.mean(),
            "conversion_rate_ci_lower": conv_lo,
            "conversion_rate_ci_upper": conv_hi,
        }
    )

ci_df = pd.DataFrame(ci_rows).round(4)
print(ci_df.to_string(index=False))
ci_df.to_csv("results/confidence_intervals.csv", index=False)

# 3. Composite ranking and budget allocation recommendation --------------------
# Per the lab's suggested weighting: CPA and ROAS at 50% each (lower CPA is better,
# so its rank is taken as-is; higher ROAS is better, so its rank is inverted below).
rank_df = group_summary[["cpa", "roas", "conversion_rate"]].reset_index()
rank_df["cpa_rank"] = rank_df["cpa"].rank(ascending=True)         # 1 = lowest (best) CPA
rank_df["roas_rank"] = rank_df["roas"].rank(ascending=False)      # 1 = highest (best) ROAS
rank_df["composite_rank_score"] = 0.5 * rank_df["cpa_rank"] + 0.5 * rank_df["roas_rank"]
rank_df = rank_df.sort_values("composite_rank_score")

# Composite score = inverse of the composite rank, normalized to sum to 1, used as allocation weight.
raw_weight = 1 / rank_df["composite_rank_score"]
rank_df["composite_score"] = raw_weight / raw_weight.sum()

# Apply reasonable constraints: no channel below 12% or above 30% of a 5-way budget split.
MIN_SHARE, MAX_SHARE = 0.12, 0.30


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

TOTAL_BUDGET = 500_000  # from the lab scenario
rank_df["illustrative_allocation_usd"] = (rank_df["allocation_pct"] * TOTAL_BUDGET).round(0)

print()
print("=" * 70)
print("COMPOSITE RANKING & BUDGET ALLOCATION RECOMMENDATION")
print("=" * 70)
print(rank_df.round(4).to_string(index=False))
rank_df.to_csv("results/allocation_recommendation.csv", index=False)

print()
print("CAVEAT: the composite ranking above orders channels by CPA/ROAS even though none of the "
      "underlying CPA differences are statistically significant (0 of 10 pairs, see Step 4/6) and "
      "the conversion-rate differences, while technically significant after FDR, are all well "
      "under 1% relative and driven by sample size, not a real effect (see Step 6 key insight). "
      "This allocation is therefore a near-even split with only cosmetic tilting — treat it as "
      "'no statistical basis to prefer one Campaign_Type over another', not a confident reallocation.")
