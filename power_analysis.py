"""
power_analysis.py
Part 4: Power Analysis & Sample Size Planning
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

plt.style.use("seaborn-v0_8-whitegrid")
rng = np.random.default_rng(42)

df = pd.read_csv("marketing_data.csv")
BASE_CPA = df["CPA"].replace([np.inf, -np.inf], np.nan).dropna().mean()
print(f"Base CPA used for simulation: ${BASE_CPA:.2f}")

ALPHA = 0.05


def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=ALPHA):
    """Simulate n_sim two-sample t-tests comparing daily CPA for channel A
    (mean=base_cpa) vs channel B (mean=base_cpa*(1+true_diff_pct)), each with
    n_days observations, std = 15% of base_cpa, floor at 50% of base_cpa.
    Returns proportion of simulations with p < alpha (empirical power)."""
    std = base_cpa * 0.15
    floor = base_cpa * 0.5
    rejections = 0
    for _ in range(n_sim):
        a = rng.normal(base_cpa, std, n_days)
        b = rng.normal(base_cpa * (1 + true_diff_pct), std, n_days)
        a = np.clip(a, floor, None)
        b = np.clip(b, floor, None)
        _, p = stats.ttest_ind(a, b)
        if p < alpha:
            rejections += 1
    return rejections / n_sim


effect_sizes = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [30, 60, 90, 120, 180]

power_rows = []
for eff in effect_sizes:
    for n in sample_sizes:
        p = empirical_power_cpa(eff, BASE_CPA, n, n_sim=500)
        power_rows.append({"effect_size_pct": eff, "n_days": n, "power": p})

power_df = pd.DataFrame(power_rows)
print("\n=== Power table (CPA, alpha=0.05) ===")
pivot = power_df.pivot(index="n_days", columns="effect_size_pct", values="power")
print(pivot.round(3).to_string())
power_df.to_csv("output/data/power_analysis_results.csv", index=False)

# ---- Power curves ----
fig, ax = plt.subplots(figsize=(8, 5.5))
for eff in effect_sizes:
    sub = power_df[power_df.effect_size_pct == eff]
    ax.plot(sub["n_days"], sub["power"], marker="o", label=f"{eff:.0%} CPA difference")
ax.axhline(0.8, color="black", linestyle="--", linewidth=1, label="80% power target")
ax.set_xlabel("Sample size (days per channel)")
ax.set_ylabel("Statistical power")
ax.set_title("Power to detect a CPA difference vs. sample size")
ax.legend()
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.savefig("output/images/power_analysis_cpa.png", dpi=150)
plt.close()
print("Saved output/images/power_analysis_cpa.png")

# ---- Minimum sample size for 80% power ----
TARGET_POWER = 0.80
CURRENT_DATA_DAYS = 90  # per lab spec: assess adequacy of ~90 days of data

print("\n=== Minimum sample size for 80% power ===")
min_n_rows = []
for eff in effect_sizes:
    sub = power_df[power_df.effect_size_pct == eff].sort_values("n_days")
    achieving = sub[sub.power >= TARGET_POWER]
    if len(achieving):
        min_n = achieving["n_days"].iloc[0]
    else:
        # extrapolate: test a larger grid
        min_n = None
        for n_try in range(200, 2001, 100):
            p = empirical_power_cpa(eff, BASE_CPA, n_try, n_sim=300)
            if p >= TARGET_POWER:
                min_n = n_try
                break
    status = "sufficient" if (min_n is not None and CURRENT_DATA_DAYS >= min_n) else "insufficient"
    min_n_rows.append({"effect_size_pct": eff, "min_days_for_80pct_power": min_n,
                        "current_data_days": CURRENT_DATA_DAYS, "status": status})
    print(f"  {eff:.0%} difference: min {min_n} days needed -> "
          f"current {CURRENT_DATA_DAYS} days is {status}")

min_n_df = pd.DataFrame(min_n_rows)
min_n_df.to_csv("output/data/min_sample_size.csv", index=False)

# ---- Assess adequacy for observed FDR-significant differences ----
# Using the CPA t-test results table produced in statistical_analysis.py
try:
    ttest_df = pd.read_csv("output/data/cpa_ttest_results.csv")
    sig_pairs = ttest_df[ttest_df["significant_fdr"]] if "significant_fdr" in ttest_df else ttest_df.iloc[0:0]
    print(f"\n=== Power assessment for CPA pairs significant after FDR correction ===")
    if len(sig_pairs) == 0:
        print("No CPA pairs were significant after FDR correction, so no observed-effect "
              "power assessment is applicable here. (This itself is informative: see memo.)")
    else:
        for _, r in sig_pairs.iterrows():
            baseline = min(r["mean_a"], r["mean_b"])
            observed_pct = abs(r["diff_b_minus_a"]) / baseline
            p90 = empirical_power_cpa(observed_pct, baseline, 90, n_sim=500)
            print(f"  {r['group_a']} vs {r['group_b']}: observed diff {observed_pct:.1%}, "
                  f"power at 90 days = {p90:.2f}")
except FileNotFoundError:
    print("Run statistical_analysis.py first to generate cpa_ttest_results.csv")

print("\nPart 4 complete.")
