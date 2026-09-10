"""
Part 4: Power Analysis & Sample Size Planning
Lab: In God we trust, everyone else bring the data

Empirically estimates statistical power for detecting CPA differences of
various sizes at various sample sizes (days of data), and assesses whether
our historical dataset was adequate to detect the differences we actually
found in statistical_analysis.py.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

plt.style.use("seaborn-v0_8-whitegrid")
rng = np.random.default_rng(42)

GROUP_COL = "channel"
ALPHA = 0.05


def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=0.05):
    """Estimate power to detect a true_diff_pct difference in mean CPA
    between two channels, each with n_days of daily observations."""
    std = base_cpa * 0.15
    cap = base_cpa * 0.5
    rejections = 0
    for _ in range(n_sim):
        a = rng.normal(base_cpa, std, n_days)
        a = np.clip(a, base_cpa - cap, base_cpa + cap)
        mean_b = base_cpa * (1 + true_diff_pct)
        b = rng.normal(mean_b, std, n_days)
        b = np.clip(b, mean_b - cap, mean_b + cap)
        _, p = stats.ttest_ind(a, b, equal_var=False)
        if p < alpha:
            rejections += 1
    return rejections / n_sim


# ---------------------------------------------------------------------------
# 1. Power curves across effect sizes and sample sizes
# ---------------------------------------------------------------------------
channel_summary = pd.read_csv("data/channel_summary.csv")
base_cpa = channel_summary["cpa"].median()  # representative baseline CPA
print(f"Using baseline CPA for simulation: ${base_cpa:.2f} (median across channels)")

effect_sizes = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [30, 60, 90, 120, 180]
N_SIM = 800

power_rows = []
for eff in effect_sizes:
    for n_days in sample_sizes:
        power = empirical_power_cpa(eff, base_cpa, n_days, n_sim=N_SIM, alpha=ALPHA)
        power_rows.append({"effect_size_pct": eff, "n_days": n_days, "power": power})

power_df = pd.DataFrame(power_rows)
print("\n=== Power Table (CPA t-test, baseline=${:.2f}) ===".format(base_cpa))
pivot = power_df.pivot(index="n_days", columns="effect_size_pct", values="power")
print(pivot.round(3).to_string())
power_df.round(4).to_csv("data/power_analysis_results.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 6))
for eff in effect_sizes:
    sub = power_df[power_df["effect_size_pct"] == eff]
    ax.plot(sub["n_days"], sub["power"], marker="o", label=f"{eff*100:.0f}% difference")
ax.axhline(0.80, color="red", linestyle="--", linewidth=1, label="80% power target")
ax.set_xlabel("Sample Size (days per channel)")
ax.set_ylabel("Statistical Power")
ax.set_title(f"Power to Detect CPA Differences (baseline CPA=${base_cpa:.0f})")
ax.legend()
ax.grid(True)
fig.tight_layout()
fig.savefig("images/power_analysis_cpa.png", dpi=150, bbox_inches="tight")
print("Saved images/power_analysis_cpa.png")

# ---------------------------------------------------------------------------
# 2. Minimum sample size for 80% power, per effect size
# ---------------------------------------------------------------------------
TARGET_POWER = 0.80
CURRENT_DAYS_BASELINE = 90  # lab's reference monitoring window

print("\n=== Minimum Days for 80% Power ===")
min_days_rows = []
finer_days = list(range(10, 401, 10))
for eff in effect_sizes:
    min_days = None
    for n_days in finer_days:
        p = empirical_power_cpa(eff, base_cpa, n_days, n_sim=400, alpha=ALPHA)
        if p >= TARGET_POWER:
            min_days = n_days
            break
    status = "Sufficient" if (min_days is not None and min_days <= CURRENT_DAYS_BASELINE) else "Insufficient"
    min_days_rows.append(
        {
            "effect_size_pct": eff,
            "min_days_for_80pct_power": min_days if min_days is not None else ">400",
            f"status_at_{CURRENT_DAYS_BASELINE}_days": status,
        }
    )
    print(f"  {eff*100:>4.0f}% difference -> min days for 80% power: {min_days if min_days else '>400'} "
          f"({status} with {CURRENT_DAYS_BASELINE}-day window)")

min_days_df = pd.DataFrame(min_days_rows)
min_days_df.to_csv("data/min_sample_size_recommendations.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Assess adequacy of ACTUAL historical data for the pairs found
#    significant after FDR correction in statistical_analysis.py
# ---------------------------------------------------------------------------
ttest_results = pd.read_csv("data/ttest_cpa_results.csv")
sig_pairs = ttest_results[ttest_results["significant_fdr"]].copy()

print(f"\n=== Data Adequacy for FDR-Significant CPA Pairs (n={len(sig_pairs)}) ===")
adequacy_rows = []
for _, row in sig_pairs.iterrows():
    observed_diff_pct = abs(row["pct_diff"]) / 100
    baseline = min(row["mean_a"], row["mean_b"])
    n_available = int(min(row["n_a"], row["n_b"]))
    power_at_available = empirical_power_cpa(observed_diff_pct, baseline, n_available, n_sim=500, alpha=ALPHA)

    min_days_needed = None
    if power_at_available < TARGET_POWER:
        for n_days in finer_days:
            p = empirical_power_cpa(observed_diff_pct, baseline, n_days, n_sim=300, alpha=ALPHA)
            if p >= TARGET_POWER:
                min_days_needed = n_days
                break

    adequacy_rows.append(
        dict(
            group_a=row["group_a"],
            group_b=row["group_b"],
            observed_diff_pct=observed_diff_pct * 100,
            n_days_available=n_available,
            power_at_available_n=power_at_available,
            min_days_needed_for_80pct=min_days_needed if min_days_needed else power_at_available >= TARGET_POWER,
        )
    )
    note = "adequate" if power_at_available >= TARGET_POWER else f"needs ~{min_days_needed} days"
    print(f"  {row['group_a']:>15} vs {row['group_b']:<15} | observed diff={observed_diff_pct*100:6.1f}% | "
          f"n_available={n_available} days | power={power_at_available:.2f} -> {note}")

adequacy_df = pd.DataFrame(adequacy_rows)
adequacy_df.to_csv("data/power_adequacy_assessment.csv", index=False)

print("\nPower analysis complete.")
