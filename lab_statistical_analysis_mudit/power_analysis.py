"""
Step 7: Power Analysis & Sample Size Planning
================================================
Empirical (Monte Carlo) power analysis for both metrics used in this lab.

Unit note (read this before the numbers below): the lab's template specifies sample size
in **days** (`empirical_power_cpa(..., n_days, ...)`, "30, 60, ... 180 days"), because it
assumes one CPA observation per channel per day. This dataset has no such daily time series
per channel — it is campaign-level (one row per campaign, each already spanning 5-30 days;
see dataset_selection.md). There is no valid way to recover a daily CPA series from it, so
"days" is translated to the closest available sampling unit for each metric:
  - CPA (`empirical_power_cpa`): **campaigns per group** — one CPA observation per campaign,
    the direct analog of "one CPA observation per day" in the lab's original design.
  - Conversion rate (`empirical_power_conversion`): **clicks per group** — the natural
    denominator for the binomial/Fisher's-exact test used in Step 5, analogous to "days" in
    the same way CPA-per-campaign is.
This is a deliberate adaptation, not an oversight — see the caveat repeated in
executive_memo.md.
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, fisher_exact

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)
rng = np.random.default_rng(42)

os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)

df = pd.read_csv("data/marketing_data.csv")

BASE_CPA_MEAN = df["Acquisition_Cost"].mean()
BASE_CONVERSION_RATE = df["Conversions"].sum() / df["Clicks"].sum()

print(f"Base CPA: mean={BASE_CPA_MEAN:.2f}")
print(f"Base conversion rate: {BASE_CONVERSION_RATE:.4%}")
print()
print("Sample-size unit: the lab's template asks for power vs. 'n_days'. This dataset is "
      "campaign-level, not a daily time series (see module docstring) — 'campaigns per group' "
      "is used for the CPA power curve below, and 'clicks per group' for conversion rate.")


def empirical_power_cpa(true_diff_pct, base_cpa, n_campaigns, n_sim=1000, alpha=0.05):
    """Power to detect a true_diff_pct relative difference in mean CPA between two
    groups of size n_campaigns, via independent t-test.

    Follows the lab's recipe exactly: both groups are normal(mean, std=base_cpa*0.15),
    group B's mean shifted by true_diff_pct. `n_campaigns` stands in for the lab's `n_days`
    (see module docstring — this dataset has no daily granularity).

    Floor, not ceiling: "cap at 50% of base" in the lab's instructions prevents the normal
    draws from producing unrealistic near-zero or negative CPA values, not from producing
    unrealistically *high* ones. Both groups use the same floor (50% of the un-shifted base
    CPA, per the lab's "same std and cap" instruction), so the floor does not itself bias the
    comparison between groups.
    """
    std = base_cpa * 0.15
    floor = base_cpa * 0.5
    rejections = 0
    for _ in range(n_sim):
        a = np.maximum(rng.normal(base_cpa, std, n_campaigns), floor)
        b = np.maximum(rng.normal(base_cpa * (1 + true_diff_pct), std, n_campaigns), floor)
        _, p = ttest_ind(a, b)
        if p < alpha:
            rejections += 1
    return rejections / n_sim


def empirical_power_conversion(true_diff_pct, base_rate, n_clicks, n_sim=1000, alpha=0.05):
    """Power to detect a true_diff_pct relative difference in conversion rate between
    two groups with n_clicks each, via Fisher's exact test on simulated binomial counts."""
    rejections = 0
    rate_b = min(base_rate * (1 + true_diff_pct), 0.999)
    for _ in range(n_sim):
        conv_a = rng.binomial(n_clicks, base_rate)
        conv_b = rng.binomial(n_clicks, rate_b)
        table = [[conv_a, n_clicks - conv_a], [conv_b, n_clicks - conv_b]]
        _, p = fisher_exact(table, alternative="two-sided")
        if p < alpha:
            rejections += 1
    return rejections / n_sim


def summarize_power(power_df, n_col, target=0.8):
    """Compact effect_size_pct / n / power / meets_80pct_target table for quick auditing,
    without needing to open the CSV."""
    out = power_df.rename(columns={n_col: "n"}).copy()
    out["meets_80pct_target"] = out["power"] >= target
    return out[["effect_size_pct", "n", "power", "meets_80pct_target"]]


# 1. Power curves for CPA ------------------------------------------------------
print()
print("=" * 70)
print("POWER CURVES — CPA (t-test)")
print("=" * 70)

effect_sizes = [0.05, 0.10, 0.15, 0.20]
campaign_ns = [30, 60, 90, 120, 180]

power_rows = []
for pct in effect_sizes:
    for n in campaign_ns:
        power = empirical_power_cpa(pct, BASE_CPA_MEAN, n, n_sim=500)
        power_rows.append({"effect_size_pct": pct, "n_campaigns": n, "power": power})
        print(f"CPA  {pct:.0%} diff, n={n:>4} campaigns/group -> power={power:.3f}")

power_df = pd.DataFrame(power_rows)
power_df.to_csv("results/power_analysis_cpa.csv", index=False)
print("\nSummary (effect_size_pct / n / power / meets_80pct_target):")
print(summarize_power(power_df, "n_campaigns").to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 6))
for pct in effect_sizes:
    subset = power_df[power_df["effect_size_pct"] == pct]
    ax.plot(subset["n_campaigns"], subset["power"], marker="o", label=f"{pct:.0%} relative difference")
ax.axhline(0.8, color="gray", linestyle="--", label="80% power target")
ax.set_xlabel("Campaigns per group")
ax.set_ylabel("Power")
ax.set_title(f"Power curves — detecting a relative difference in CPA\n(base CPA=${BASE_CPA_MEAN:.0f})")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/power_analysis_cpa.png", dpi=150)
plt.close(fig)
print("\nSaved figures/power_analysis_cpa.png")

# 2. Power curves for conversion rate -------------------------------------------
print()
print("=" * 70)
print("POWER CURVES — conversion rate (Fisher's exact)")
print("=" * 70)

click_ns = [500, 1000, 2500, 5000, 10000]
power_rows_conv = []
for pct in effect_sizes:
    for n in click_ns:
        power = empirical_power_conversion(pct, BASE_CONVERSION_RATE, n, n_sim=500)
        power_rows_conv.append({"effect_size_pct": pct, "n_clicks": n, "power": power})
        print(f"Conversion  {pct:.0%} diff, n={n:>5} clicks/group -> power={power:.3f}")

power_conv_df = pd.DataFrame(power_rows_conv)
power_conv_df.to_csv("results/power_analysis_conversion.csv", index=False)
print("\nSummary (effect_size_pct / n / power / meets_80pct_target):")
print(summarize_power(power_conv_df, "n_clicks").to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 6))
for pct in effect_sizes:
    subset = power_conv_df[power_conv_df["effect_size_pct"] == pct]
    ax.plot(subset["n_clicks"], subset["power"], marker="o", label=f"{pct:.0%} relative difference")
ax.axhline(0.8, color="gray", linestyle="--", label="80% power target")
ax.set_xlabel("Clicks per group")
ax.set_ylabel("Power")
ax.set_title(f"Power curves — detecting a relative difference in conversion rate\n(base rate={BASE_CONVERSION_RATE:.2%})")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/power_analysis_conversion.png", dpi=150)
plt.close(fig)
print("Saved figures/power_analysis_conversion.png")

# 3. Minimum sample size for 80% power ----------------------------------------
def find_min_n(power_fn, base_args, effect_pct, candidate_ns, target_power=0.8, n_sim=300):
    for n in candidate_ns:
        power = power_fn(effect_pct, *base_args, n, n_sim=n_sim)
        if power >= target_power:
            return n, power
    return None, None


print()
print("=" * 70)
print("MINIMUM SAMPLE SIZE FOR 80% POWER")
print("=" * 70)

candidate_ns_continuous = [30, 60, 90, 120, 180, 300, 500, 1000, 2000, 5000]
min_n_rows = []
current_n_campaigns = int(df.groupby("Campaign_Type", observed=True).size().min())
for pct in effect_sizes:
    n, power = find_min_n(empirical_power_cpa, (BASE_CPA_MEAN,), pct, candidate_ns_continuous)
    sufficient = current_n_campaigns >= n if n else True
    min_n_rows.append(
        {"metric": "cpa", "effect_size_pct": pct, "min_n_campaigns": n, "achieved_power": power,
         "current_min_group_n": current_n_campaigns, "current_data_sufficient": sufficient}
    )
    print(f"CPA   {pct:.0%} diff -> min n/group = {n} campaigns (power={power}) | "
          f"current smallest group n={current_n_campaigns} -> {'SUFFICIENT' if sufficient else 'INSUFFICIENT'}")

candidate_ns_clicks = [200, 500, 1000, 2500, 5000, 10000, 25000, 50000]
current_n_clicks = int(df.groupby("Campaign_Type", observed=True)["Clicks"].sum().min())
for pct in effect_sizes:
    n, power = find_min_n(empirical_power_conversion, (BASE_CONVERSION_RATE,), pct, candidate_ns_clicks)
    sufficient = current_n_clicks >= n if n else True
    min_n_rows.append(
        {"metric": "conversion_rate", "effect_size_pct": pct, "min_n_campaigns": n, "achieved_power": power,
         "current_min_group_n": current_n_clicks, "current_data_sufficient": sufficient}
    )
    print(f"Conversion {pct:.0%} diff -> min n/group = {n} clicks (power={power}) | "
          f"current smallest group n={current_n_clicks:,} -> {'SUFFICIENT' if sufficient else 'INSUFFICIENT'}")

min_n_df = pd.DataFrame(min_n_rows)
min_n_df.to_csv("results/power_min_sample_size.csv", index=False)

smallest_effect_ok = min_n_df[min_n_df["effect_size_pct"] == min(effect_sizes)]["current_data_sufficient"].all()
print(f"\nConclusion: current data is "
      f"{'SUFFICIENT' if smallest_effect_ok else 'INSUFFICIENT'} for 80% power at the smallest "
      f"effect size tested ({min(effect_sizes):.0%} relative difference) in both metrics — "
      "the effect size we'd most struggle to detect.")

# 4. Assess current data adequacy for observed FDR-significant pairs -----------
print()
print("=" * 70)
print("CURRENT DATA ADEQUACY — observed FDR-significant pairs")
print("=" * 70)

ttest_corrected = pd.read_csv("results/ttest_results_corrected.csv")
fisher_corrected = pd.read_csv("results/fisher_results_corrected.csv")

TARGET_POWER = 0.8


def estimate_n_needed(power_fn, base_args, obs_pct, n_current, n_sim=300):
    """When power at the current n is below target, search upward from n_current for the
    smallest n (as a multiple of n_current) that reaches 80% power, so the adequacy table
    always reports either 'sufficient' or a concrete number of additional observations needed."""
    candidates = [int(n_current * m) for m in (1.5, 2, 3, 5, 10, 20, 50)]
    return find_min_n(power_fn, base_args, obs_pct, candidates, target_power=TARGET_POWER, n_sim=n_sim)


adequacy_rows = []

sig_ttest = ttest_corrected[ttest_corrected["significant_fdr"]]
for _, row in sig_ttest.iterrows():
    obs_pct = abs(row["pct_difference"]) / 100
    n_group = int(df.loc[df["Campaign_Type"].isin([row["group_a"], row["group_b"]]),
                          "Campaign_Type"].value_counts().min())
    power = empirical_power_cpa(obs_pct, BASE_CPA_MEAN, n_group, n_sim=300)
    n_needed, power_at_needed = (None, None) if power >= TARGET_POWER else \
        estimate_n_needed(empirical_power_cpa, (BASE_CPA_MEAN,), obs_pct, n_group)
    adequacy_rows.append(
        {"metric": "cpa", "group_a": row["group_a"], "group_b": row["group_b"],
         "observed_pct_diff": row["pct_difference"], "n_per_group": n_group, "power_at_current_n": power,
         "estimated_n_needed_for_80pct": n_needed, "power_at_estimated_n": power_at_needed}
    )
    note = "sufficient" if power >= TARGET_POWER else f"~{n_needed} campaigns/group needed"
    print(f"CPA {row['group_a']} vs {row['group_b']}: observed diff={row['pct_difference']:+.2f}%, "
          f"n={n_group} campaigns/group -> power={power:.3f} ({note})")

sig_fisher = fisher_corrected[fisher_corrected["significant_fdr"]]
for _, row in sig_fisher.iterrows():
    obs_pct = abs(row["pct_difference"]) / 100
    n_group = int(min(row["total_a"], row["total_b"]))
    power = empirical_power_conversion(obs_pct, BASE_CONVERSION_RATE, n_group, n_sim=300)
    n_needed, power_at_needed = (None, None) if power >= TARGET_POWER else \
        estimate_n_needed(empirical_power_conversion, (BASE_CONVERSION_RATE,), obs_pct, n_group)
    adequacy_rows.append(
        {"metric": "conversion_rate", "group_a": row["group_a"], "group_b": row["group_b"],
         "observed_pct_diff": row["pct_difference"], "n_per_group": n_group, "power_at_current_n": power,
         "estimated_n_needed_for_80pct": n_needed, "power_at_estimated_n": power_at_needed}
    )
    note = "sufficient" if power >= TARGET_POWER else f"~{n_needed:,} clicks/group needed"
    print(f"Conversion {row['group_a']} vs {row['group_b']}: observed diff={row['pct_difference']:+.2f}%, "
          f"n={n_group:,} clicks/group -> power={power:.3f} ({note})")

if not adequacy_rows:
    print("No FDR-significant pairs to assess (none survived correction).")
else:
    adequacy_df = pd.DataFrame(adequacy_rows)
    adequacy_df.to_csv("results/power_current_data_adequacy.csv", index=False)
    n_underpowered = (adequacy_df["power_at_current_n"] < TARGET_POWER).sum()
    print(f"\nSaved results/power_current_data_adequacy.csv ({len(adequacy_df)} pairs)")
    if n_underpowered == 0:
        print("Conclusion: every FDR-significant pair is already adequately powered (>=80%) at "
              "the current sample size — no further data collection is needed to trust these "
              "specific comparisons, though see executive_memo.md for why they aren't "
              "practically meaningful regardless.")
    else:
        print(f"Conclusion: {n_underpowered} of {len(adequacy_df)} FDR-significant pair(s) are "
              "under-powered (<80%) at the current sample size — see "
              "'estimated_n_needed_for_80pct' for how much more data each would need.")
