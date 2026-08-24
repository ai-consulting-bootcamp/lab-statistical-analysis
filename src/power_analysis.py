import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

DATA_PATH = "data/processed/marketing_data_clean.csv"
OUTPUT_TABLE = "results/tables/power_analysis_results.csv"
OUTPUT_FIGURE = "results/figures/power_analysis_cpa.png"

os.makedirs("results/tables", exist_ok=True)
os.makedirs("results/figures", exist_ok=True)


def empirical_power_cpa(
    true_diff_pct,
    base_cpa,
    n_days,
    n_sim=1000,
    alpha=0.05
):
    """
    Estimate statistical power through simulation.
    """

    std = base_cpa * 0.15
    mean_b = base_cpa * (1 + true_diff_pct)

    significant = 0

    for _ in range(n_sim):
        group_a = np.random.normal(
            base_cpa,
            std,
            n_days
        )

        group_b = np.random.normal(
            mean_b,
            std,
            n_days
        )

        # Prevent unrealistic negative CPA values
        group_a = np.maximum(group_a, base_cpa * 0.5)
        group_b = np.maximum(group_b, base_cpa * 0.5)

        _, p_value = ttest_ind(
            group_a,
            group_b,
            equal_var=False
        )

        if p_value < alpha:
            significant += 1

    return significant / n_sim


print("Loading processed dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df):,} rows.")


# ---------------------------------------------------------
# BASE CPA
# ---------------------------------------------------------

platform_summary = (
    df.groupby("platform")
    .agg(
        spend=("spend", "sum"),
        conversions=("conversions", "sum")
    )
    .reset_index()
)

platform_summary["cpa"] = (
    platform_summary["spend"] /
    platform_summary["conversions"]
)

base_cpa = platform_summary["cpa"].median()

print("\n============================================================")
print("POWER ANALYSIS")
print("============================================================")

print(f"Base CPA used for simulation: ${base_cpa:.2f}")


# ---------------------------------------------------------
# POWER GRID
# ---------------------------------------------------------

effect_sizes = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [30, 60, 90, 120, 180]

results = []

print("\nCalculating statistical power...")

for effect in effect_sizes:

    for n_days in sample_sizes:

        power = empirical_power_cpa(
            true_diff_pct=effect,
            base_cpa=base_cpa,
            n_days=n_days,
            n_sim=1000
        )

        results.append({
            "effect_size_pct": effect * 100,
            "n_days": n_days,
            "power": power
        })

        print(
            f"Effect: {effect*100:.0f}% | "
            f"Days: {n_days:3d} | "
            f"Power: {power:.3f}"
        )


power_df = pd.DataFrame(results)

power_df.to_csv(
    OUTPUT_TABLE,
    index=False
)


# ---------------------------------------------------------
# MINIMUM SAMPLE SIZE FOR 80% POWER
# ---------------------------------------------------------

print("\n============================================================")
print("MINIMUM SAMPLE SIZE FOR 80% POWER")
print("============================================================")

minimum_samples = []

for effect in effect_sizes:

    subset = power_df[
        power_df["effect_size_pct"] == effect * 100
    ]

    sufficient = subset[
        subset["power"] >= 0.80
    ]

    if len(sufficient) > 0:
        min_days = sufficient["n_days"].min()
        status = "Sufficient with current 90 days"
    else:
        min_days = "More than 180 days"
        status = "Insufficient within tested range"

    minimum_samples.append({
        "effect_size_pct": effect * 100,
        "minimum_days": min_days,
        "status": status
    })

    print(
        f"{effect*100:.0f}% effect → "
        f"{min_days} days → {status}"
    )


minimum_df = pd.DataFrame(minimum_samples)


# ---------------------------------------------------------
# CURRENT DATA ADEQUACY
# ---------------------------------------------------------

print("\n============================================================")
print("CURRENT DATA ADEQUACY — 90 DAYS")
print("============================================================")

for effect in effect_sizes:

    row = power_df[
        (power_df["effect_size_pct"] == effect * 100) &
        (power_df["n_days"] == 90)
    ]

    power = row["power"].iloc[0]

    status = (
        "SUFFICIENT"
        if power >= 0.80
        else "INSUFFICIENT"
    )

    print(
        f"{effect*100:.0f}% difference: "
        f"power={power:.3f} → {status}"
    )


# ---------------------------------------------------------
# POWER CURVE
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))

for effect in effect_sizes:

    subset = power_df[
        power_df["effect_size_pct"] == effect * 100
    ]

    plt.plot(
        subset["n_days"],
        subset["power"],
        marker="o",
        label=f"{effect*100:.0f}% effect"
    )

plt.axhline(
    0.80,
    linestyle="--",
    label="80% target"
)

plt.xlabel("Number of Days")
plt.ylabel("Statistical Power")
plt.title("CPA Power Analysis")
plt.ylim(0, 1.05)
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_FIGURE,
    dpi=150
)

plt.close()


# ---------------------------------------------------------
# SAVE SAMPLE SIZE SUMMARY
# ---------------------------------------------------------

minimum_df.to_csv(
    "results/tables/minimum_sample_size.csv",
    index=False
)


print("\n============================================================")
print("POWER ANALYSIS COMPLETED")
print("============================================================")

print("\nFiles created:")
print(f"- {OUTPUT_TABLE}")
print("- results/tables/minimum_sample_size.csv")
print(f"- {OUTPUT_FIGURE}")