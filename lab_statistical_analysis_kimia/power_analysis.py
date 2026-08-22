"""
Power Analysis — Marketing Channel ROI Comparison Lab
========================================================
Part 4: empirical power simulation, power curves, minimum sample size,
and data-adequacy assessment for the significant pairs found after FDR
correction.

Run data_exploration.py and statistical_analysis.py first.
"""

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

ALPHA = 0.05
TARGET_POWER = 0.80


def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=ALPHA, seed=42):
    rng = np.random.default_rng(seed)
    std = base_cpa * 0.15
    cap = base_cpa * 0.5
    rejections = 0
    for _ in range(n_sim):
        a = rng.normal(base_cpa, std, n_days)
        a = np.clip(a, cap, None)
        b = rng.normal(base_cpa * (1 + true_diff_pct), std, n_days)
        b = np.clip(b, cap, None)
        _, p_val = ttest_ind(a, b)
        if p_val < alpha:
            rejections += 1
    return rejections / n_sim


def build_power_curves(base_cpa, effect_sizes=(0.05, 0.10, 0.15, 0.20),
                        sample_sizes=(30, 60, 90, 120, 180), n_sim=500):
    rows = []
    for eff in effect_sizes:
        for n in sample_sizes:
            power = empirical_power_cpa(eff, base_cpa, n, n_sim=n_sim)
            rows.append({"effect_size_pct": eff * 100, "n_days": n, "power": power})
    return pd.DataFrame(rows)


def plot_power_curves(power_df, outdir="outputs"):
    import os
    os.makedirs(outdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    for eff, sub in power_df.groupby("effect_size_pct"):
        ax.plot(sub["n_days"], sub["power"], marker="o", label=f"{eff:.0f}% difference")
    ax.axhline(TARGET_POWER, color="gray", linestyle="--", label="80% power target")
    ax.set_xlabel("Sample size (days)")
    ax.set_ylabel("Statistical power")
    ax.set_title("Power curves for detecting CPA differences")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = f"{outdir}/power_analysis_cpa.png"
    plt.savefig(fname, dpi=150)
    print(f"Saved {fname}")
    plt.close()


def minimum_sample_size(base_cpa, effect_sizes=(0.05, 0.10, 0.15, 0.20),
                         candidate_days=range(10, 401, 10), n_sim=300,
                         current_data_days=90):
    rows = []
    for eff in effect_sizes:
        min_days = None
        for n in candidate_days:
            power = empirical_power_cpa(eff, base_cpa, n, n_sim=n_sim)
            if power >= TARGET_POWER:
                min_days = n
                break
        status = "sufficient" if (min_days is not None and current_data_days >= min_days) else "insufficient"
        rows.append({
            "effect_size_pct": eff * 100,
            "min_days_for_80pct_power": min_days,
            "current_data_days": current_data_days,
            "status": status,
        })
    return pd.DataFrame(rows)


def assess_significant_pairs(cpa_results_path="data/cpa_pairwise_results.csv",
                              current_data_days=90):
    empty_cols = ["group_a", "group_b", "observed_diff_pct",
                  "power_at_current_data", "days_needed_for_80pct_power"]
    try:
        cpa_results = pd.read_csv(cpa_results_path)
    except FileNotFoundError:
        print(f"{cpa_results_path} not found — run statistical_analysis.py first.")
        return pd.DataFrame(columns=empty_cols)

    if "significant_fdr" not in cpa_results.columns:
        print("No FDR-corrected results found in CPA results file.")
        return pd.DataFrame(columns=empty_cols)

    sig_pairs = cpa_results[cpa_results["significant_fdr"]]
    if len(sig_pairs) == 0:
        return pd.DataFrame(columns=empty_cols)
    rows = []
    for _, row in sig_pairs.iterrows():
        base = min(row["mean_a"], row["mean_b"])
        obs_diff_pct = abs(row["diff"]) / base if base != 0 else np.nan
        power_now = empirical_power_cpa(obs_diff_pct, base, current_data_days, n_sim=500)
        needed_days = None
        if power_now < TARGET_POWER:
            for n in range(10, 401, 10):
                if empirical_power_cpa(obs_diff_pct, base, n, n_sim=300) >= TARGET_POWER:
                    needed_days = n
                    break
        rows.append({
            "group_a": row["group_a"], "group_b": row["group_b"],
            "observed_diff_pct": obs_diff_pct * 100,
            "power_at_current_data": power_now,
            "days_needed_for_80pct_power": needed_days,
        })
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv("data/marketing_data_clean.csv")
    from data_exploration import COLUMN_MAP as cm
    base_cpa = df[cm["acquisition_cost"]].mean()
    print(f"Base CPA used for simulations: {base_cpa:.2f}")

    power_df = build_power_curves(base_cpa)
    print("\n=== Power table ===")
    print(power_df.pivot(index="n_days", columns="effect_size_pct", values="power").round(3))
    plot_power_curves(power_df)
    power_df.to_csv("data/power_curve_results.csv", index=False)

    current_days = 90
    if cm["date"] in df.columns:
        try:
            dates = pd.to_datetime(df[cm["date"]])
            current_days = max(1, (dates.max() - dates.min()).days)
        except Exception:
            pass
    min_n = minimum_sample_size(base_cpa, current_data_days=current_days)
    print(f"\n=== Minimum sample size for 80% power (current data spans ~{current_days} days) ===")
    print(min_n.to_string(index=False))
    min_n.to_csv("data/minimum_sample_size.csv", index=False)

    assessment = assess_significant_pairs(current_data_days=current_days)
    if len(assessment):
        print("\n=== Data adequacy for FDR-significant CPA pairs ===")
        print(assessment.to_string(index=False))
    else:
        print("\nNo FDR-significant CPA pairs to assess (see statistical_analysis.py output).")
    # Always write the file (even if empty) so downstream scripts can detect
    # "ran but found nothing" vs. "never ran".
    assessment.to_csv("data/power_assessment_significant_pairs.csv", index=False)

    print("\n=== Power analysis complete ===")


if __name__ == "__main__":
    main()
