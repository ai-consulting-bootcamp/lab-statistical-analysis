from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "marketing_data.csv"
RESULTS_DIR = BASE_DIR / "results"


# ---------------------------------------------------------
# Load prepared data
# ---------------------------------------------------------

df = pd.read_csv(DATA_FILE)

# ---------------------------------------------------------
# Empirical CPA power simulation
# ---------------------------------------------------------

def empirical_power_cpa(true_diff_pct, base_cpa, n_observations, n_sim=1000, alpha=0.05):
    significant_results = 0

    mean_a = base_cpa
    mean_b = base_cpa * (1 + true_diff_pct)
    std = base_cpa * 0.15
    minimum_cpa = base_cpa * 0.50

    for _ in range(n_sim):
        group_a = np.random.normal(mean_a, std, n_observations)
        group_b = np.random.normal(mean_b, std, n_observations)

        group_a = np.clip(group_a, minimum_cpa, None)
        group_b = np.clip(group_b, minimum_cpa, None)

        _, p_value = ttest_ind(group_a, group_b, equal_var=False)

        if p_value < alpha:
            significant_results += 1

    return significant_results / n_sim


# ---------------------------------------------------------
# Power scenarios
# ---------------------------------------------------------

np.random.seed(42)

effect_sizes = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [30, 60, 90, 120, 180]

base_cpa = df["CPA"].median()

power_results = []

for effect_size in effect_sizes:
    for sample_size in sample_sizes:
        power = empirical_power_cpa(
            true_diff_pct=effect_size,
            base_cpa=base_cpa,
            n_observations=sample_size,
        )

        power_results.append({
            "effect_size_pct": effect_size * 100,
            "n_observations": sample_size,
            "power": power,
        })

power_df = pd.DataFrame(power_results)


# ---------------------------------------------------------
# Display power results
# ---------------------------------------------------------

print("\n--- CPA POWER ANALYSIS ---")

power_table = power_df.pivot(
    index="n_observations",
    columns="effect_size_pct",
    values="power",
)

print(power_table.round(3))


# ---------------------------------------------------------
# Plot power curves
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 6))

for effect_size in effect_sizes:
    subset = power_df[power_df["effect_size_pct"] == effect_size * 100]
    ax.plot(subset["n_observations"], subset["power"], marker="o", label=f"{effect_size:.0%} difference")

ax.axhline(0.80, linestyle="--", label="80% power")

ax.set_xlabel("Observations per Campaign")
ax.set_ylabel("Statistical Power")
ax.set_title("Power to Detect CPA Differences")
ax.set_ylim(0, 1.05)
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()

POWER_FILE = RESULTS_DIR / "power_analysis_cpa.png"
plt.savefig(POWER_FILE, dpi=150, bbox_inches="tight")
plt.close()

print(f"\nPower curve saved to: {POWER_FILE}")

# ---------------------------------------------------------
# Minimum sample size for 80% power
# ---------------------------------------------------------

minimum_sample_results = []

for effect_size in effect_sizes:
    subset = power_df[
        (power_df["effect_size_pct"] == effect_size * 100)
        & (power_df["power"] >= 0.80)
    ]

    minimum_n = subset["n_observations"].min() if not subset.empty else np.nan

    minimum_sample_results.append({
        "effect_size_pct": effect_size * 100,
        "minimum_observations_for_80_power": minimum_n,
    })

minimum_sample_df = pd.DataFrame(minimum_sample_results)

print("\n--- MINIMUM SAMPLE SIZE FOR 80% POWER ---")
print(minimum_sample_df.to_string(index=False))


# ---------------------------------------------------------
# Save power-analysis results
# ---------------------------------------------------------

POWER_RESULTS_FILE = RESULTS_DIR / "power_analysis_results.csv"
SAMPLE_SIZE_FILE = RESULTS_DIR / "minimum_sample_size.csv"

power_df.to_csv(POWER_RESULTS_FILE, index=False)
minimum_sample_df.to_csv(SAMPLE_SIZE_FILE, index=False)

print(f"\nPower results saved to: {POWER_RESULTS_FILE}")
print(f"Sample-size results saved to: {SAMPLE_SIZE_FILE}")


# ---------------------------------------------------------
# Power simulation for unequal group sizes
# ---------------------------------------------------------

def empirical_power_cpa_pair(true_diff_pct, base_cpa, n_a, n_b, n_sim=1000, alpha=0.05):
    significant_results = 0

    mean_a = base_cpa
    mean_b = base_cpa * (1 + true_diff_pct)
    std = base_cpa * 0.15
    minimum_cpa = base_cpa * 0.50

    for _ in range(n_sim):
        group_a = np.random.normal(mean_a, std, n_a)
        group_b = np.random.normal(mean_b, std, n_b)

        group_a = np.clip(group_a, minimum_cpa, None)
        group_b = np.clip(group_b, minimum_cpa, None)

        _, p_value = ttest_ind(group_a, group_b, equal_var=False)

        if p_value < alpha:
            significant_results += 1

    return significant_results / n_sim

# ---------------------------------------------------------
# Load significant CPA comparisons
# ---------------------------------------------------------

CPA_RESULTS_FILE = RESULTS_DIR / "cpa_pairwise_comparisons.csv"

cpa_results = pd.read_csv(CPA_RESULTS_FILE)

significant_pairs = cpa_results[cpa_results["significant_fdr"]].copy()


# ---------------------------------------------------------
# Assess current data adequacy
# ---------------------------------------------------------

adequacy_results = []

for _, row in significant_pairs.iterrows():
    mean_a = row["mean_cpa_a"]
    mean_b = row["mean_cpa_b"]

    baseline_cpa = min(mean_a, mean_b)
    observed_difference_pct = abs(mean_b - mean_a) / baseline_cpa

    power = empirical_power_cpa_pair(
        true_diff_pct=observed_difference_pct,
        base_cpa=baseline_cpa,
        n_a=int(row["n_a"]),
        n_b=int(row["n_b"]),
    )

    adequacy_results.append({
        "campaign_a": int(row["campaign_a"]),
        "campaign_b": int(row["campaign_b"]),
        "n_a": int(row["n_a"]),
        "n_b": int(row["n_b"]),
        "mean_cpa_a": mean_a,
        "mean_cpa_b": mean_b,
        "observed_difference_pct": observed_difference_pct * 100,
        "estimated_power": power,
        "adequate_80_power": power >= 0.80,
    })

adequacy_df = pd.DataFrame(adequacy_results)

print("\n--- CURRENT DATA ADEQUACY ---")
print(adequacy_df.round(3).to_string(index=False))

# ---------------------------------------------------------
# Save data-adequacy results
# ---------------------------------------------------------

ADEQUACY_FILE = RESULTS_DIR / "current_data_adequacy.csv"
adequacy_df.to_csv(ADEQUACY_FILE, index=False)

print(f"\nData-adequacy results saved to: {ADEQUACY_FILE}")

