from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind


HERE = Path(__file__).resolve().parent
DATA = HERE / "marketing_data.csv"


def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=500, alpha=0.05, rng=None):
    rng = rng or np.random.default_rng()
    std_a = base_cpa * 0.15
    std_b = base_cpa * (1 + true_diff_pct) * 0.15
    rejections = 0
    for _ in range(n_sim):
        a = rng.normal(base_cpa, std_a, n_days)
        b = rng.normal(base_cpa * (1 + true_diff_pct), std_b, n_days)
        a = np.clip(a, 0.5 * base_cpa, None)
        b = np.clip(b, 0.5 * base_cpa * (1 + true_diff_pct), None)
        rejections += ttest_ind(a, b, equal_var=False).pvalue < alpha
    return rejections / n_sim


def main():
    rng = np.random.default_rng(42)
    df = pd.read_csv(DATA)
    daily = df.groupby(["Date", "Channel_Used"], as_index=False).agg(
        Cost=("Acquisition_Cost", "sum"),
        Conversions=("Conversions", "sum"),
    )
    daily["CPA"] = daily["Cost"] / daily["Conversions"].replace(0, np.nan)
    base_cpa = daily["CPA"].dropna().median()

    effect_sizes = [0.05, 0.10, 0.15, 0.20]
    sample_sizes = [30, 60, 90, 120, 180]
    rows = []
    for effect in effect_sizes:
        for n_days in sample_sizes:
            rows.append({
                "effect_size_pct": int(effect * 100),
                "n_days": n_days,
                "power": empirical_power_cpa(effect, base_cpa, n_days, rng=rng),
            })
    power = pd.DataFrame(rows)
    power.to_csv(HERE / "power_analysis_results.csv", index=False, float_format="%.4f")
    print("\nPower analysis:")
    print(power.to_string(index=False))

    minimum_rows = []
    for effect in effect_sizes:
        subset = power.loc[power["effect_size_pct"] == int(effect * 100)]
        reached = subset.loc[subset["power"] >= 0.80]
        minimum = int(reached["n_days"].min()) if not reached.empty else np.nan
        minimum_rows.append({
            "effect_size_pct": int(effect * 100),
            "minimum_days_needed": minimum,
            "current_90_day_status": "sufficient" if pd.notna(minimum) and minimum <= 90 else "insufficient",
        })
    minimum = pd.DataFrame(minimum_rows)
    minimum.to_csv(HERE / "minimum_sample_sizes.csv", index=False)
    print("\nMinimum sample sizes:")
    print(minimum.to_string(index=False))

    fig, ax = plt.subplots(figsize=(9, 6))
    for effect in effect_sizes:
        subset = power.loc[power["effect_size_pct"] == int(effect * 100)]
        ax.plot(subset["n_days"], subset["power"], marker="o", label=f"{int(effect * 100)}% difference")
    ax.axhline(0.80, color="red", linestyle="--", label="80% target")
    ax.set_xlabel("Days")
    ax.set_ylabel("Statistical power")
    ax.set_ylim(0, 1)
    ax.set_title("Empirical Power for Detecting CPA Differences")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(HERE / "power_analysis_cpa.png", dpi=150)
    plt.close(fig)

    cpa = pd.read_csv(HERE / "cpa_comparisons.csv")
    significant = cpa.loc[cpa["significant_fdr"]]
    assessment_rows = []
    for row in significant.itertuples():
        baseline = min(abs(row.mean_a), abs(row.mean_b))
        observed_pct = abs(row.percentage_difference) / 100
        observed_power = empirical_power_cpa(observed_pct, baseline, 90, rng=rng)
        estimate = np.nan
        if observed_power < 0.8:
            for n_days in range(30, 361, 30):
                candidate = empirical_power_cpa(observed_pct, baseline, n_days, rng=rng)
                if candidate >= 0.8:
                    estimate = n_days
                    break
        assessment_rows.append({
            "comparison": f"{row.group_a} vs {row.group_b}",
            "observed_difference_pct": abs(row.percentage_difference),
            "baseline_cpa": baseline,
            "power_at_90_days": observed_power,
            "days_needed_for_80pct": estimate,
        })
    assessment = pd.DataFrame(
        assessment_rows,
        columns=[
            "comparison",
            "observed_difference_pct",
            "baseline_cpa",
            "power_at_90_days",
            "days_needed_for_80pct",
        ],
    )
    assessment.to_csv(HERE / "current_data_adequacy.csv", index=False, float_format="%.4f")
    print("\nCurrent data adequacy:")
    print(assessment.to_string(index=False))


if __name__ == "__main__":
    main()
