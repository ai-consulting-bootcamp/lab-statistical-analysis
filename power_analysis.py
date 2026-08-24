"""
Part 4: Power Analysis & Sample Size Planning
Marketing Channel Budget Allocation Lab
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

plt.style.use("seaborn-v0_8-whitegrid")
ALPHA = 0.05
TARGET_POWER = 0.80
RNG = np.random.default_rng(42)


def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=ALPHA):
    """Simulate n_sim two-sample t-test experiments comparing daily CPA
    between channel A (mean=base_cpa) and channel B (mean=base_cpa*(1+true_diff_pct)).
    Returns the proportion of simulations that correctly reject H0 (= power).

    Per the lab spec: std = base_cpa * 0.15, and values are capped at 50% of base_cpa.
    That cap is a floor only (CPA can't sensibly go below half its baseline), not a
    symmetric band -- we do not also cap the upside, since nothing in the spec caps
    the upper tail and doing so would artificially suppress variance for the higher-mean group.
    """
    std = base_cpa * 0.15
    floor = base_cpa * 0.5
    rejections = 0
    for _ in range(n_sim):
        a = RNG.normal(base_cpa, std, n_days)
        a = np.clip(a, floor, None)
        b = RNG.normal(base_cpa * (1 + true_diff_pct), std, n_days)
        b = np.clip(b, floor, None)
        _, p = ttest_ind(a, b)
        if p < alpha:
            rejections += 1
    return rejections / n_sim


# ---------------------------------------------------------------------------
# Power curves across effect sizes and sample sizes
# ---------------------------------------------------------------------------
df = pd.read_csv("data/marketing_data.csv")
base_cpa = df["CPA"].mean()
print(f"Base CPA used for simulation: ${base_cpa:.2f}")

effect_sizes = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [30, 60, 90, 120, 180]
N_SIM = 500  # reduced for speed; still stable estimates

power_rows = []
for es in effect_sizes:
    for n in sample_sizes:
        power = empirical_power_cpa(es, base_cpa, n, n_sim=N_SIM)
        power_rows.append({"effect_size_pct": es * 100, "n_days": n, "power": power})
        print(f"effect={es*100:.0f}%  n_days={n:4d}  power={power:.3f}")

power_df = pd.DataFrame(power_rows)
power_df.to_csv("outputs/power_analysis_results.csv", index=False)

# --- power curves plot ---
fig, ax = plt.subplots(figsize=(8, 6))
for es in effect_sizes:
    sub = power_df[power_df["effect_size_pct"] == es * 100]
    ax.plot(sub["n_days"], sub["power"], marker="o", label=f"{es*100:.0f}% difference")
ax.axhline(TARGET_POWER, color="black", linestyle="--", linewidth=1, label="80% target power")
ax.set_xlabel("Sample size (days of campaign data per channel)")
ax.set_ylabel("Statistical power")
ax.set_title("Power to Detect CPA Differences vs. Sample Size")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig("outputs/power_analysis_cpa.png", dpi=150)
plt.close()
print("Saved outputs/power_analysis_cpa.png")

# ---------------------------------------------------------------------------
# Minimum sample size for 80% power, per effect size
# ---------------------------------------------------------------------------
CURRENT_N_DAYS = 90  # ~90 days is what we'd realistically have per channel in a rolling analysis
min_n_rows = []
for es in effect_sizes:
    # search a finer grid to find min n achieving target power
    found = None
    for n in range(10, 401, 10):
        p = empirical_power_cpa(es, base_cpa, n, n_sim=300)
        if p >= TARGET_POWER:
            found = n
            break
    status = "Sufficient" if (found is not None and found <= CURRENT_N_DAYS) else "Insufficient"
    min_n_rows.append({
        "effect_size_pct": es * 100,
        "min_days_for_80pct_power": found if found else ">400",
        "current_data_days": CURRENT_N_DAYS,
        "status_with_current_data": status,
    })

min_n_df = pd.DataFrame(min_n_rows)
print("\nMinimum sample size for 80% power:\n", min_n_df)
min_n_df.to_csv("outputs/min_sample_size.csv", index=False)

# ---------------------------------------------------------------------------
# Assess adequacy for CPA pairs (the metric this power analysis is built around),
# using each pair's *exact* observed effect size directly -- not snapped to the
# nearest of the [5,10,15,20]% simulation grid -- and the smaller of the two
# channel means as the baseline, per the lab spec.
# ---------------------------------------------------------------------------
cpa_results = pd.read_csv("outputs/ttest_cpa_results.csv")
sig_cpa_fdr = cpa_results[cpa_results["significant_fdr"] == True]
sig_cpa_uncorrected = cpa_results[cpa_results["significant_uncorrected"] == True]

print(f"\n--- CPA pairs significant after FDR correction: {len(sig_cpa_fdr)} ---")
print("(Expected: 0, since Part 2-3 found no CPA/ROI pair survives correction.)")
print(f"--- CPA pairs significant before correction (context only): {len(sig_cpa_uncorrected)} ---")

def adequacy_for_pair(row, n_days_current=CURRENT_N_DAYS, n_sim=1000):
    baseline = min(row["mean_a"], row["mean_b"])
    diff = abs(row["mean_b"] - row["mean_a"])
    observed_effect = diff / baseline if baseline > 0 else np.nan
    power_now = empirical_power_cpa(observed_effect, baseline, n_days_current, n_sim=n_sim)
    # find min days for 80% power at this *exact* observed effect size
    min_days = None
    for n in range(10, 401, 10):
        if empirical_power_cpa(observed_effect, baseline, n, n_sim=300) >= TARGET_POWER:
            min_days = n
            break
    return {
        "pair": f"{row['group_a']} vs {row['group_b']}",
        "baseline_cpa": round(baseline, 2),
        "observed_diff_pct_of_baseline": round(observed_effect * 100, 3),
        "power_with_90days": round(power_now, 3),
        "min_days_for_80pct_power": min_days if min_days else ">400",
        "note": "adequately powered at 90 days" if power_now >= TARGET_POWER else "under-powered at 90 days for this exact observed gap",
    }

adequacy_rows = [adequacy_for_pair(r) for _, r in sig_cpa_uncorrected.iterrows()]
adequacy_df = pd.DataFrame(adequacy_rows)
if len(adequacy_df):
    print("\nCPA adequacy (uncorrected-significant pairs, exact observed effect size):")
    print(adequacy_df.to_string(index=False))
else:
    print("\nNo CPA pairs were significant even before correction -- no adequacy check to run;"
          " the observed CPA gaps are too small relative to noise to test power against.")
adequacy_df.to_csv("outputs/power_adequacy_cpa_pairs.csv", index=False)

print("\n=== Part 4 complete ===")
