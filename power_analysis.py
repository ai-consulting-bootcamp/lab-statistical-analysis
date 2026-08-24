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
    Returns the proportion of simulations that correctly reject H0 (= power)."""
    std = base_cpa * 0.15
    cap = base_cpa * 0.5
    rejections = 0
    for _ in range(n_sim):
        a = RNG.normal(base_cpa, std, n_days)
        a = np.clip(a, base_cpa - cap, base_cpa + cap)
        b = RNG.normal(base_cpa * (1 + true_diff_pct), std, n_days)
        b = np.clip(b, base_cpa - cap, base_cpa + cap)
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
# Assess adequacy for pairs that were significant after FDR correction
# ---------------------------------------------------------------------------
fisher_results = pd.read_csv("outputs/fisher_exact_results.csv")
sig_pairs = fisher_results[fisher_results["significant_fdr"] == True]

print("\n--- Data adequacy for FDR-significant conversion-rate pairs ---")
adequacy_rows = []
for _, r in sig_pairs.iterrows():
    rate_a, rate_b = r["rate_a_%"] / 100, r["rate_b_%"] / 100
    baseline = min(rate_a, rate_b)
    pct_diff = abs(rate_b - rate_a) / baseline if baseline > 0 else np.nan
    # crude mapping onto the CPA power-curve grid (same statistical logic, different metric)
    nearest_es = min(effect_sizes, key=lambda e: abs(e - pct_diff))
    power_90d = power_df[(power_df["effect_size_pct"] == nearest_es * 100) & (power_df["n_days"] == 90)]["power"].values[0]
    adequacy_rows.append({
        "pair": f"{r['group_a']} vs {r['group_b']}",
        "observed_diff_pct_of_baseline": round(pct_diff * 100, 2),
        "nearest_simulated_effect_size_pct": nearest_es * 100,
        "approx_power_with_90days": round(power_90d, 3),
        "note": "adequately powered" if power_90d >= TARGET_POWER else "under-powered at this effect size",
    })
adequacy_df = pd.DataFrame(adequacy_rows)
print(adequacy_df.to_string(index=False))
adequacy_df.to_csv("outputs/power_adequacy_fdr_pairs.csv", index=False)

print("\n=== Part 4 complete ===")
