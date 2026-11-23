from itertools import product
from math import ceil

from data_exploration import DATA, TABLES, FIGURES, save_plot
from statistical_analysis import ALPHA

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import nct, t, ttest_ind

TARGET = 0.80
STANDARD_CV = 0.15
EFFECTS = [0.05, 0.10, 0.15, 0.20]


def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=0.05, *, cv=0.15):
    rng = np.random.default_rng(271_828 + n_days)
    sample_shape = (n_sim, n_days)
    sd = base_cpa * cv
    floor = base_cpa * 0.50
    a = np.maximum(rng.normal(base_cpa, sd, sample_shape), floor)
    b = np.maximum(rng.normal(base_cpa * (1 + true_diff_pct), sd, sample_shape), floor)
    results = ttest_ind(a, b, axis=1, equal_var=False)
    return float((results.pvalue < alpha).mean())


def reference_power(n_days, relative_difference, alpha=ALPHA, cv=STANDARD_CV):
    # The equal-SD normal reference is a smooth planning approximation to the simulation.
    dof = 2 * n_days - 2
    critical = t.isf(alpha / 2, dof)
    noncentrality = relative_difference / cv * np.sqrt(n_days / 2)
    return nct.cdf(-critical, dof, noncentrality) + nct.sf(critical, dof, noncentrality)


def minimum_days(relative_difference, alpha=ALPHA, cv=STANDARD_CV):
    lo, hi = 2, 2
    while reference_power(hi, relative_difference, alpha, cv) < TARGET:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if reference_power(mid, relative_difference, alpha, cv) < TARGET:
            lo = mid + 1
        else:
            hi = mid
    return lo


def plan_sample_sizes(base_cpa, observed_days, bonf_alpha, higher_cv):
    rows = []
    for effect in EFFECTS:
        required = minimum_days(effect)
        rows.append({
            "effect_size_pct": round(effect * 100), "observed_days_per_campaign": observed_days,
            "minimum_days_per_arm_reference": required,
            "additional_days_vs_observed": max(0, required - observed_days),
            "observed_status_under_model": "sufficient" if required <= observed_days else "insufficient",
            "day_90_status_under_model": "sufficient" if required <= 90 else "insufficient",
            "simulated_power_at_minimum": empirical_power_cpa(effect, base_cpa, required, 8000),
            "simulated_power_at_observed_days": empirical_power_cpa(effect, base_cpa, observed_days, 8000),
            "simulated_power_at_90_days": empirical_power_cpa(effect, base_cpa, 90, 8000),
            "minimum_days_per_arm_bonferroni": minimum_days(effect, alpha=bonf_alpha),
            "minimum_days_per_arm_high_cv": minimum_days(effect, cv=higher_cv),
            "high_cv_scenario": higher_cv,
        })
    return pd.DataFrame(rows)


def assess_cpa_pairs(pairs):
    rows = []
    for row in pairs.loc[pairs["significant_fdr"]].itertuples():
        lower, higher = sorted([row.mean_a, row.mean_b])
        effect = (higher - lower) / lower
        n_days = min(row.n_a, row.n_b)
        required = minimum_days(effect)
        power_now = empirical_power_cpa(effect, lower, n_days, 8000)
        rows.append({
            "campaign_a": row.campaign_a, "campaign_b": row.campaign_b,
            "baseline_mean_cpa": lower, "effect_pct_vs_lower_cpa": effect * 100,
            "p_value_fdr": row.p_value_fdr, "current_days_per_arm": n_days,
            "conditional_power_current_days": power_now,
            "conditional_power_at_90_days": empirical_power_cpa(effect, lower, 90, 8000),
            "reference_days_for_80_pct": required,
            "additional_days_vs_current": max(0, required - n_days),
            "assessment": "at least 80% in model" if power_now >= TARGET else "below 80% in model",
        })
    return pd.DataFrame(rows)


def plot_power(curves, observed_days):
    fig, ax = plt.subplots(figsize=(10.5, 5.8), layout="constrained")
    palette = ["#295f79", "#287271", "#a46b41", "#944f78"]
    for (effect, group), color in zip(curves.groupby("effect_size_pct"), palette, strict=True):
        ax.plot(group["n_days"], group["power"], marker="o", linewidth=2, color=color, label=f"{effect:g}% CPA gap")
    ax.axhline(TARGET, color="#1c2b33", linestyle="--", linewidth=1, label="80% target")
    ax.axvline(observed_days, color="#6e777a", linestyle=":", linewidth=1.1, label=f"{observed_days} observed days")
    ax.set(title="Power to detect a difference in mean daily CPA",
           xlabel="Independent days per arm", ylabel="Simulated power", ylim=(0, 1.04))
    ax.set_yticks(np.linspace(0, 1, 6), labels=[f"{x:.0%}" for x in np.linspace(0, 1, 6)])
    ax.set_xticks(sorted(curves["n_days"].unique()))
    ax.legend(loc="lower right", ncol=2)
    save_plot(fig, "power_analysis_cpa.png")


def main():
    daily = pd.read_csv(DATA / "marketing_data.csv")
    pairs = pd.read_csv(TABLES / "cpa_pairwise.csv")
    observed_days = int(daily.groupby("campaign")["cpa"].count().min())
    base_cpa = daily["cpa"].median()
    variability = daily.groupby("campaign")["cpa"].agg(["mean", "std"])
    variability["coefficient_of_variation"] = variability["std"] / variability["mean"]
    higher_cv = ceil(variability["coefficient_of_variation"].max() * 20) / 20
    curves = pd.DataFrame([
        {"effect_size_pct": round(effect * 100), "n_days": n_days,
         "power": empirical_power_cpa(effect, base_cpa, n_days, 8000)}
        for effect, n_days in product(EFFECTS, [15, 30, 60, 90, 120, 180])
    ])
    plan = plan_sample_sizes(base_cpa, observed_days, ALPHA / len(pairs), higher_cv)
    pairs_power = assess_cpa_pairs(pairs)
    variability.to_csv(TABLES / "power_observed_variability.csv")
    curves.to_csv(TABLES / "power_curves.csv", index=False)
    plan.to_csv(TABLES / "power_sample_size.csv", index=False)
    pairs_power.to_csv(TABLES / "power_current_pairs.csv", index=False)
    print("Simulated power by effect and days per arm")
    print(curves.pivot(index="n_days", columns="effect_size_pct", values="power").round(3).to_string())
    print("\nSample size planning\n" + plan.round(3).to_string(index=False))
    print("\nConditional planning estimates for BH-significant CPA pairs")
    print(pairs_power.round(3).to_string(index=False))
    sns.set_theme(style="whitegrid", context="notebook")
    plot_power(curves, observed_days)


if __name__ == "__main__":
    main()
