"""
Step 7: Power Analysis & Sample Size Planning
================================================
Empirical (Monte Carlo) power analysis for both metrics used in this lab:

  - `empirical_power_total_ads` — continuous metric (adapts the lab's
    `empirical_power_cpa` recipe to total_ads, since there is no CPA here).
  - `empirical_power_conversion` — binary metric (conversion rate), simulated
    with binomial counts and tested with Fisher's exact test, matching the
    test used in Step 5.

Sample size is expressed in **users per group**, not "days", because this
dataset has no daily time series — see dataset_selection.md.
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, fisher_exact

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)
rng = np.random.default_rng(42)

df = pd.read_csv("data/marketing_data.csv")

BASE_TOTAL_ADS_MEAN = df["total_ads"].mean()
BASE_TOTAL_ADS_STD = df["total_ads"].std()
BASE_CONVERSION_RATE = df["converted"].mean()

print(f"Base total_ads: mean={BASE_TOTAL_ADS_MEAN:.2f}, std={BASE_TOTAL_ADS_STD:.2f}")
print(f"Base conversion rate: {BASE_CONVERSION_RATE:.4%}")


def empirical_power_total_ads(true_diff_pct, base_mean, base_std, n_users, n_sim=1000, alpha=0.05):
    """Power to detect a true_diff_pct relative difference in mean total_ads
    between two groups of size n_users, via independent t-test."""
    rejections = 0
    mean_b = base_mean * (1 + true_diff_pct)
    for _ in range(n_sim):
        a = rng.normal(base_mean, base_std, n_users)
        a = np.clip(a, 0, None)  # total_ads cannot be negative
        b = rng.normal(mean_b, base_std, n_users)
        b = np.clip(b, 0, None)
        _, p_value = ttest_ind(a, b)
        if p_value < alpha:
            rejections += 1
    return rejections / n_sim


def empirical_power_conversion(true_diff_pct, base_rate, n_users, n_sim=1000, alpha=0.05):
    """Power to detect a true_diff_pct relative difference in conversion rate
    between two groups of size n_users, via Fisher's exact test."""
    rejections = 0
    rate_b = base_rate * (1 + true_diff_pct)
    for _ in range(n_sim):
        conv_a = rng.binomial(n_users, base_rate)
        conv_b = rng.binomial(n_users, rate_b)
        table = [[conv_a, n_users - conv_a], [conv_b, n_users - conv_b]]
        _, p_value = fisher_exact(table, alternative="two-sided")
        if p_value < alpha:
            rejections += 1
    return rejections / n_sim


# 1a. Power curves — total_ads -----------------------------------------------
effect_sizes = [0.05, 0.10, 0.15, 0.20]
n_grid_continuous = [30, 60, 90, 120, 180]

rows = []
for pct in effect_sizes:
    for n in n_grid_continuous:
        power = empirical_power_total_ads(pct, BASE_TOTAL_ADS_MEAN, BASE_TOTAL_ADS_STD, n, n_sim=500)
        rows.append({"effect_size_pct": pct, "n_users": n, "power": power})
power_total_ads_df = pd.DataFrame(rows)
power_total_ads_df.to_csv("results/power_analysis_total_ads.csv", index=False)

print()
print("=" * 70)
print("POWER TABLE — total_ads (continuous)")
print("=" * 70)
print(power_total_ads_df.pivot(index="n_users", columns="effect_size_pct", values="power"))

fig, ax = plt.subplots(figsize=(8, 6))
for pct in effect_sizes:
    subset = power_total_ads_df[power_total_ads_df["effect_size_pct"] == pct]
    ax.plot(subset["n_users"], subset["power"], marker="o", label=f"{pct:.0%} difference")
ax.axhline(0.8, color="gray", linestyle="--", label="80% power target")
ax.set_xlabel("Users per group")
ax.set_ylabel("Power")
ax.set_title("Power curves — detecting a difference in mean total_ads")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/power_analysis_total_ads.png", dpi=150)
plt.close(fig)
print("Saved figures/power_analysis_total_ads.png")

# 1b. Power curves — conversion rate ------------------------------------------
n_grid_binary = [500, 1000, 2000, 5000, 10000]
rows = []
for pct in effect_sizes:
    for n in n_grid_binary:
        power = empirical_power_conversion(pct, BASE_CONVERSION_RATE, n, n_sim=500)
        rows.append({"effect_size_pct": pct, "n_users": n, "power": power})
power_conv_df = pd.DataFrame(rows)
power_conv_df.to_csv("results/power_analysis_conversion.csv", index=False)

print()
print("=" * 70)
print("POWER TABLE — conversion rate (binary)")
print("=" * 70)
print(power_conv_df.pivot(index="n_users", columns="effect_size_pct", values="power"))

fig, ax = plt.subplots(figsize=(8, 6))
for pct in effect_sizes:
    subset = power_conv_df[power_conv_df["effect_size_pct"] == pct]
    ax.plot(subset["n_users"], subset["power"], marker="o", label=f"{pct:.0%} relative difference")
ax.axhline(0.8, color="gray", linestyle="--", label="80% power target")
ax.set_xlabel("Users per group")
ax.set_ylabel("Power")
ax.set_title(f"Power curves — detecting a relative difference in conversion rate\n(base rate={BASE_CONVERSION_RATE:.2%})")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/power_analysis_conversion.png", dpi=150)
plt.close(fig)
print("Saved figures/power_analysis_conversion.png")

# 2. Minimum sample size for 80% power ----------------------------------------
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
for pct in effect_sizes:
    n, power = find_min_n(
        empirical_power_total_ads, (BASE_TOTAL_ADS_MEAN, BASE_TOTAL_ADS_STD), pct, candidate_ns_continuous
    )
    current_n = int(df.groupby("most_ads_day", observed=True).size().min())  # smallest group we actually have
    sufficient = current_n >= n if n else True
    min_n_rows.append(
        {"metric": "total_ads", "effect_size_pct": pct, "min_n_users": n, "achieved_power": power,
         "current_min_group_n": current_n, "current_data_sufficient": sufficient}
    )
    print(f"total_ads   {pct:.0%} diff -> min n/group = {n} (power={power}) | "
          f"current smallest group n={current_n} -> {'SUFFICIENT' if sufficient else 'INSUFFICIENT'}")

candidate_ns_binary = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
for pct in effect_sizes:
    n, power = find_min_n(
        empirical_power_conversion, (BASE_CONVERSION_RATE,), pct, candidate_ns_binary
    )
    current_n = int(df.groupby("most_ads_day", observed=True).size().min())
    sufficient = current_n >= n if n else True
    min_n_rows.append(
        {"metric": "conversion_rate", "effect_size_pct": pct, "min_n_users": n, "achieved_power": power,
         "current_min_group_n": current_n, "current_data_sufficient": sufficient}
    )
    print(f"conversion  {pct:.0%} diff -> min n/group = {n} (power={power}) | "
          f"current smallest group n={current_n} -> {'SUFFICIENT' if sufficient else 'INSUFFICIENT'}")

min_n_df = pd.DataFrame(min_n_rows)
min_n_df.to_csv("results/power_min_sample_size.csv", index=False)

# 3. Assess current data adequacy for observed significant pairs --------------
print()
print("=" * 70)
print("CURRENT DATA ADEQUACY — power to detect the *observed* effects, at *actual* current n")
print("=" * 70)

ttest_corrected = pd.read_csv("results/ttest_results_corrected.csv")
fisher_corrected = pd.read_csv("results/fisher_results_corrected.csv")
group_sizes = df.groupby("most_ads_day", observed=True).size()

adequacy_rows = []
sig_ttest = ttest_corrected[ttest_corrected["significant_fdr"]]
for _, row in sig_ttest.iterrows():
    n_actual = int(min(group_sizes[row["group_a"]], group_sizes[row["group_b"]]))
    observed_pct = abs(row["pct_difference"]) / 100
    power = empirical_power_total_ads(observed_pct, BASE_TOTAL_ADS_MEAN, BASE_TOTAL_ADS_STD, n_actual, n_sim=300)
    adequacy_rows.append(
        {"metric": "total_ads", "group_a": row["group_a"], "group_b": row["group_b"],
         "observed_pct_diff": row["pct_difference"], "n_actual": n_actual, "power_at_current_n": power}
    )

sig_fisher = fisher_corrected[fisher_corrected["significant_fdr"]]
for _, row in sig_fisher.iterrows():
    n_actual = int(min(group_sizes[row["group_a"]], group_sizes[row["group_b"]]))
    observed_pct = abs(row["pct_difference"]) / 100
    power = empirical_power_conversion(observed_pct, BASE_CONVERSION_RATE, n_actual, n_sim=300)
    adequacy_rows.append(
        {"metric": "conversion_rate", "group_a": row["group_a"], "group_b": row["group_b"],
         "observed_pct_diff": row["pct_difference"], "n_actual": n_actual, "power_at_current_n": power}
    )

adequacy_df = pd.DataFrame(adequacy_rows)
adequacy_df.to_csv("results/power_current_data_adequacy.csv", index=False)
print(adequacy_df.round(4).to_string(index=False))

low_power = adequacy_df[adequacy_df["power_at_current_n"] < 0.8]
print()
if len(low_power) == 0:
    print("Every FDR-significant pair (both metrics) has >=80% power at our actual current sample sizes — "
          "we are well-powered to detect the differences we found. This is a direct consequence of the "
          "very large per-group sample sizes (tens of thousands of users), which is exactly why so many "
          "comparisons cleared statistical significance even when the underlying effect (Cohen's d) is tiny.")
else:
    print(f"{len(low_power)} FDR-significant pairs have <80% power at current n — treat these as provisional:")
    print(low_power.round(4).to_string(index=False))
