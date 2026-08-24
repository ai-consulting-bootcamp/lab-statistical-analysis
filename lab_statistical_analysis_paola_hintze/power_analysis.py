"""Power, bootstrap confidence intervals, and constrained budget allocation."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-paola-stat-lab")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import ttest_ind


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
SEED = 20260824
TARGET_POWER = 0.80


def empirical_power_cpa(
    true_diff_pct: float,
    base_cpa: float,
    n_days: int,
    n_sim: int = 1000,
    alpha: float = 0.05,
    seed: int = SEED,
) -> float:
    """Monte Carlo power for a two-sided Welch test under the lab assumptions."""
    rng = np.random.default_rng(seed + n_days + round(true_diff_pct * 10_000))
    std = base_cpa * 0.15
    a = np.clip(
        rng.normal(base_cpa, std, size=(n_sim, n_days)),
        base_cpa * 0.50,
        None,
    )
    b_mean = base_cpa * (1 + true_diff_pct)
    b = np.clip(
        rng.normal(b_mean, std, size=(n_sim, n_days)),
        base_cpa * 0.50,
        None,
    )
    p_values = ttest_ind(a, b, axis=1, equal_var=False).pvalue
    return float(np.mean(p_values < alpha))


def bootstrap_ci(
    values: np.ndarray,
    n_bootstrap: int = 2000,
    ci_level: float = 0.95,
    seed: int = SEED,
) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        return np.nan, np.nan
    rng = np.random.default_rng(seed + values.size)
    samples = rng.choice(values, size=(n_bootstrap, values.size), replace=True)
    means = samples.mean(axis=1)
    tail = (1 - ci_level) / 2
    return tuple(np.quantile(means, [tail, 1 - tail]))


def constrained_allocation(
    weights: pd.Series,
    total: float = 500_000,
    minimum: float = 25_000,
    maximum: float = 125_000,
) -> pd.Series:
    """Water-fill normalized positive weights subject to min/max channel budgets."""
    allocation = pd.Series(minimum, index=weights.index, dtype=float)
    remaining = total - allocation.sum()
    active = set(weights.index)
    while remaining > 0.01 and active:
        active_index = list(active)
        active_weights = weights.loc[active_index]
        proposed = remaining * active_weights / active_weights.sum()
        capped_any = False
        for channel in active_index:
            capacity = maximum - allocation[channel]
            if proposed[channel] >= capacity:
                allocation[channel] += capacity
                remaining -= capacity
                active.remove(channel)
                capped_any = True
        if not capped_any:
            allocation.loc[active_index] += proposed
            remaining = 0.0
    if not np.isclose(allocation.sum(), total, atol=0.05):
        raise ValueError("Constrained allocation does not sum to the budget")
    return allocation


def create_power_grid(base_cpa: float) -> pd.DataFrame:
    effects = [0.05, 0.10, 0.15, 0.20]
    days = [30, 60, 90, 120, 180]
    rows = []
    for effect in effects:
        for n_days in days:
            rows.append(
                {
                    "effect_size_pct": int(effect * 100),
                    "n_days_per_channel": n_days,
                    "power": empirical_power_cpa(effect, base_cpa, n_days),
                }
            )
    return pd.DataFrame(rows)


def minimum_tested_days(power_grid: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for effect, group in power_grid.groupby("effect_size_pct"):
        eligible = group.loc[group["power"] >= TARGET_POWER, "n_days_per_channel"]
        minimum = int(eligible.min()) if not eligible.empty else np.nan
        power_90 = float(group.loc[group["n_days_per_channel"].eq(90), "power"].iloc[0])
        rows.append(
            {
                "effect_size_pct": int(effect),
                "minimum_tested_days_for_80pct_power": minimum,
                "power_at_90_days": power_90,
                "current_90_days_status": "sufficient" if power_90 >= TARGET_POWER else "insufficient",
            }
        )
    return pd.DataFrame(rows)


def plot_power(grid: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    for effect, group in grid.groupby("effect_size_pct"):
        ax.plot(
            group["n_days_per_channel"],
            group["power"],
            marker="o",
            label=f"{effect}% CPA difference",
        )
    ax.axhline(TARGET_POWER, color="black", linestyle="--", label="80% target")
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Days per channel")
    ax.set_ylabel("Estimated statistical power")
    ax.set_title("Empirical power for two-channel CPA comparisons")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "power_analysis_cpa.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def assess_observed_pairs(frame: pd.DataFrame, base_cpa: float) -> pd.DataFrame:
    comparisons = pd.read_csv(OUTPUTS / "cpa_pairwise_comparisons.csv")
    significant = comparisons.loc[comparisons["significant_fdr"]].copy()
    rows = []
    search_days = [30, 60, 90, 120, 180, 240, 300, 365]
    for row in significant.itertuples():
        smaller = min(row.mean_cpa_a, row.mean_cpa_b)
        observed = abs(row.mean_cpa_b - row.mean_cpa_a) / smaller
        power_90 = empirical_power_cpa(observed, smaller, 90, n_sim=750)
        minimum = np.nan
        for days in search_days:
            if empirical_power_cpa(observed, smaller, days, n_sim=500) >= TARGET_POWER:
                minimum = days
                break
        rows.append(
            {
                "group_a": row.group_a,
                "group_b": row.group_b,
                "observed_difference_pct": observed * 100,
                "fdr_adjusted_p_value": row.p_value_fdr,
                "cohen_d": row.cohen_d,
                "estimated_power_at_90_days": power_90,
                "minimum_tested_days_for_80pct_power": minimum,
                "note": "Power model uses the lab's normal/15% SD assumptions, not the sparse empirical CPA distribution.",
            }
        )
    return pd.DataFrame(rows)


def create_confidence_intervals(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for channel, group in frame.groupby("channel"):
        values = group["cpa"].dropna().to_numpy()
        lower, upper = bootstrap_ci(values)
        rows.append(
            {
                "channel": channel,
                "conversion_positive_days": int(values.size),
                "mean_daily_cpa": float(values.mean()),
                "ci_95_lower": lower,
                "ci_95_upper": upper,
                "estimand": "Mean daily CPA conditional on at least one conversion",
            }
        )
    return pd.DataFrame(rows).sort_values("mean_daily_cpa")


def create_budget_allocation(summary: pd.DataFrame) -> pd.DataFrame:
    ranked = summary.set_index("channel").copy()
    n = len(ranked)
    ranked["cpa_points"] = n + 1 - ranked["cpa"].rank(method="average", ascending=True)
    ranked["roas_points"] = n + 1 - ranked["roas"].rank(method="average", ascending=False)
    ranked["conversion_points"] = n + 1 - ranked["conversion_rate"].rank(
        method="average", ascending=False
    )
    ranked["margin_points"] = n + 1 - ranked["profit_margin"].rank(
        method="average", ascending=False
    )
    ranked["composite_points"] = (
        0.35 * ranked["cpa_points"]
        + 0.35 * ranked["roas_points"]
        + 0.20 * ranked["conversion_points"]
        + 0.10 * ranked["margin_points"]
    )
    ranked["recommended_budget"] = constrained_allocation(ranked["composite_points"])
    ranked["budget_share"] = ranked["recommended_budget"] / 500_000
    ranked["historical_cost_share"] = ranked["cost"] / ranked["cost"].sum()
    ranked["change_vs_historical_share_pp"] = (
        ranked["budget_share"] - ranked["historical_cost_share"]
    ) * 100
    ranked["allocation_rule"] = "Composite rank with 5% floor and 25% cap"
    return ranked.reset_index().sort_values("recommended_budget", ascending=False)


def plot_budget(allocation: pd.DataFrame) -> None:
    ordered = allocation.sort_values("recommended_budget")
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(ordered["channel"], ordered["recommended_budget"], color="#5B8FF9")
    ax.bar_label(bars, labels=[f"${value/1000:.0f}K" for value in ordered["recommended_budget"]], padding=4)
    ax.set_title("Guardrailed allocation of the $500K monthly test budget")
    ax.set_xlabel("Recommended monthly budget (USD)")
    fig.tight_layout()
    fig.savefig(FIGURES / "budget_allocation.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    frame = pd.read_csv(DATA / "marketing_data.csv", parse_dates=["date"])
    summary = pd.read_csv(OUTPUTS / "group_performance_summary.csv")
    base_cpa = float(summary["cpa"].median())
    grid = create_power_grid(base_cpa)
    grid.to_csv(OUTPUTS / "power_analysis_results.csv", index=False)
    minimum = minimum_tested_days(grid)
    minimum.to_csv(OUTPUTS / "sample_size_recommendations.csv", index=False)
    observed = assess_observed_pairs(frame, base_cpa)
    observed.to_csv(OUTPUTS / "observed_pair_power.csv", index=False)
    confidence = create_confidence_intervals(frame)
    confidence.to_csv(OUTPUTS / "cpa_bootstrap_confidence_intervals.csv", index=False)
    allocation = create_budget_allocation(summary)
    allocation.to_csv(OUTPUTS / "budget_allocation.csv", index=False)
    plot_power(grid)
    plot_budget(allocation)
    print("Power grid:\n", grid.pivot(index="n_days_per_channel", columns="effect_size_pct", values="power"))
    print("\nSample size recommendations:\n", minimum.to_string(index=False))
    print("\nBudget allocation:\n", allocation[["channel", "recommended_budget", "budget_share"]].to_string(index=False))


if __name__ == "__main__":
    main()

