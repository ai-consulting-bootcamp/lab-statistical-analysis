"""Part 4 · Power analysis & sample size (Step 7) + Part 5 inputs (bootstrap CIs, ranking, allocation).

Input:  daily_channel_metrics.csv, results/ttest_cpa.csv, group_metrics_summary.csv
Output: results/power_table.csv, results/min_days.csv, results/adequacy.csv, results/bootstrap_ci_cpa.csv,
        results/allocation.csv, figures/power_analysis_cpa.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)  # fixed seed: reproducible simulations
BUDGET = 500_000


def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=0.05):
    """Simulate n_sim experiments with a TRUE difference and count how often a t-test detects it (lab spec)."""
    sd = base_cpa * 0.15
    hits = 0
    for _ in range(n_sim):
        a = np.maximum(RNG.normal(base_cpa, sd, n_days), base_cpa * 0.5)  # cap at 50% of base
        b = np.maximum(RNG.normal(base_cpa * (1 + true_diff_pct), sd, n_days), base_cpa * 0.5)
        if stats.ttest_ind(a, b).pvalue < alpha:
            hits += 1
    return hits / n_sim


def days_for_power(diff_pct, base, target=0.8, max_days=2000):
    for n in [30, 60, 90, 120, 180, 240, 365, 500, 730, 1000, 1500, 2000]:
        if n > max_days:
            break
        if empirical_power_cpa(diff_pct, base, n, n_sim=400) >= target:
            return n
    return None


def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    data = np.asarray(data)
    means = [RNG.choice(data, size=len(data), replace=True).mean() for _ in range(n_bootstrap)]
    a = (1 - ci_level) / 2
    return np.percentile(means, a * 100), np.percentile(means, (1 - a) * 100)


def main():
    daily = pd.read_csv(HERE / "daily_channel_metrics.csv", parse_dates=["Date"])
    cpa_daily = daily["CPA"].replace([np.inf, -np.inf], np.nan).dropna()
    base_cpa = cpa_daily.mean()
    n_current = int(daily.groupby("Channel")["Date"].nunique().min())
    print(f"Base CPA (mean daily CPA, all channels): {base_cpa:.2f}. Current data: {n_current} days per channel.")
    print("Note: the lab's simulation assumes a daily CPA spread of 15% of the mean; "
          f"the observed spread here is {cpa_daily.std() / base_cpa:.0%} (see README).")

    effects, sizes = [0.05, 0.10, 0.15, 0.20], [30, 60, 90, 120, 180]
    rows = [{"effect_size_pct": int(e * 100), "n_days": n, "power": empirical_power_cpa(e, base_cpa, n)}
            for e in effects for n in sizes]
    power = pd.DataFrame(rows)
    power.to_csv(HERE / "results/power_table.csv", index=False)
    print(power.pivot(index="effect_size_pct", columns="n_days", values="power").round(3).to_string())

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for e, sub in power.groupby("effect_size_pct"):
        ax.plot(sub["n_days"], sub["power"], marker="o", label=f"{e}% true difference")
    ax.axhline(0.8, color="black", ls="--", lw=1, label="80% power target")
    ax.set_xlabel("Days of data per channel")
    ax.set_ylabel("Power (share of simulations detecting the difference)")
    ax.set_title("Power to detect a CPA difference (t-test, alpha = 0.05, 1,000 simulations)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "figures/power_analysis_cpa.png", dpi=120)
    plt.close(fig)

    mins = []
    for e in effects:
        n = days_for_power(e, base_cpa)
        mins.append({"effect_size_pct": int(e * 100), "min_days_for_80pct_power": n,
                     "current_days": n_current, "status": "sufficient" if n and n <= n_current else "insufficient"})
    mins = pd.DataFrame(mins)
    mins.to_csv(HERE / "results/min_days.csv", index=False)
    print("\n", mins.to_string(index=False))

    # Adequacy for pairs still significant after FDR (if any)
    cpa = pd.read_csv(HERE / "results/ttest_cpa.csv")
    adequacy = []
    for _, r in cpa[cpa["significant_fdr"]].iterrows():
        base = min(r.mean_a, r.mean_b)
        diff = abs(r.mean_b - r.mean_a) / base
        pw = empirical_power_cpa(diff, base, n_current, n_sim=500)
        adequacy.append({"pair": f"{r.group_a} vs {r.group_b}", "observed_diff_pct": round(diff * 100, 2),
                         "power_with_current_days": pw,
                         "days_for_80pct": n_current if pw >= 0.8 else days_for_power(diff, base)})
    pd.DataFrame(adequacy).to_csv(HERE / "results/adequacy.csv", index=False)
    print("\nPairs significant after FDR:", adequacy if adequacy else "none")

    # Part 5 · bootstrap 95% CI of mean daily CPA per channel
    ci = []
    for ch, sub in daily.groupby("Channel"):
        x = sub["CPA"].replace([np.inf, -np.inf], np.nan).dropna()
        lo, hi = bootstrap_ci(x)
        ci.append({"channel": ch, "mean_daily_cpa": x.mean(), "ci95_low": lo, "ci95_high": hi})
    ci = pd.DataFrame(ci).sort_values("mean_daily_cpa")
    ci.round(2).to_csv(HERE / "results/bootstrap_ci_cpa.csv", index=False)
    print("\n", ci.round(2).to_string(index=False))

    # Part 5 · composite ranking (50% CPA, lower better; 50% ROAS, higher better) and constrained allocation
    g = pd.read_csv(HERE / "group_metrics_summary.csv", index_col=0)
    rank_cpa = g["CPA"].rank(ascending=False)    # lowest CPA gets the highest rank
    rank_roas = g["ROAS"].rank(ascending=True)   # highest ROAS gets the highest rank
    g["composite_score"] = 0.5 * rank_cpa + 0.5 * rank_roas
    w = g["composite_score"] / g["composite_score"].sum()
    for _ in range(50):                          # constraints: 10%-25% per channel, re-spread until they hold
        w = w.clip(lower=0.10, upper=0.25)
        w = w / w.sum()
        if w.min() >= 0.0999 and w.max() <= 0.2501:
            break
    alloc = pd.DataFrame({"composite_score": g["composite_score"], "allocation_pct": (w * 100).round(1),
                          "allocation_usd": (w * BUDGET).round(-2)}).sort_values("composite_score", ascending=False)
    alloc.to_csv(HERE / "results/allocation.csv")
    print("\n", alloc.to_string())


if __name__ == "__main__":
    main()
