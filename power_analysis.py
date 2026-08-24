from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

DATASET_NAME = "Solstice SaaS Growth Pack - channel_performance"
DATASET_URL = "https://huggingface.co/datasets/solsticestudioai/saas-growth-pack"
ANALYST = "Parisa Dehghani"
TARGET_POWER = 0.80


def empirical_power_cpa(
    true_diff_pct,
    base_cpa,
    n_days,
    n_sim=1000,
    alpha=0.05,
    rng=None,
):
    """Estimate power using the simulation requested in the lab."""
    if rng is None:
        rng = np.random.default_rng(42)

    std = base_cpa * 0.15
    significant = 0

    for _ in range(n_sim):
        a = rng.normal(base_cpa, std, n_days)
        b = rng.normal(base_cpa * (1 + true_diff_pct), std, n_days)

        # Keep simulated CPA positive and cap extreme low values at 50% of base.
        a = np.clip(a, base_cpa * 0.5, None)
        b = np.clip(b, base_cpa * 0.5, None)

        _, p_value = ttest_ind(a, b, equal_var=False)
        if p_value < alpha:
            significant += 1

    return significant / n_sim


def minimum_days_for_power(effect_pct, base_cpa, rng):
    candidates = [30, 60, 90, 120, 180, 240, 365]
    for n_days in candidates:
        power = empirical_power_cpa(
            effect_pct, base_cpa, n_days, n_sim=500, rng=rng
        )
        if power >= TARGET_POWER:
            return n_days
    return ">365"


def markdown_table(df, columns):
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join(["---"] * len(columns)) + "|"
    rows = []
    for _, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if col == "recommended_budget":
                values.append(f"${value:,.0f}")
            elif col == "budget_pct":
                values.append(f"{value:.1%}")
            elif isinstance(value, (float, np.floating)):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, sep] + rows)


def main():
    required_files = [
        "daily_channel_metrics.csv",
        "cpa_pairwise_results.csv",
        "fisher_pairwise_results.csv",
        "budget_allocation.csv",
        "confidence_intervals.csv",
        "channel_summary.csv",
    ]
    for name in required_files:
        if not (ROOT / name).exists():
            raise FileNotFoundError(
                f"{name} is missing. Run data_exploration.py and "
                f"statistical_analysis.py first."
            )

    daily = pd.read_csv(ROOT / "daily_channel_metrics.csv")
    cpa_results = pd.read_csv(ROOT / "cpa_pairwise_results.csv")
    fisher_results = pd.read_csv(ROOT / "fisher_pairwise_results.csv")
    budget = pd.read_csv(ROOT / "budget_allocation.csv")
    ci_df = pd.read_csv(ROOT / "confidence_intervals.csv")
    channel_summary = pd.read_csv(ROOT / "channel_summary.csv")

    base_cpa = float(daily["cpa"].replace([np.inf, -np.inf], np.nan).median())
    if not np.isfinite(base_cpa) or base_cpa <= 0:
        raise RuntimeError("Could not determine a valid base CPA for power analysis.")

    rng = np.random.default_rng(42)
    effect_sizes = [0.05, 0.10, 0.15, 0.20]
    sample_sizes = [30, 60, 90, 120, 180]

    rows = []
    for effect in effect_sizes:
        for n_days in sample_sizes:
            power = empirical_power_cpa(
                effect,
                base_cpa,
                n_days,
                n_sim=1000,
                rng=rng,
            )
            rows.append(
                {
                    "effect_size_pct": int(effect * 100),
                    "n_days": n_days,
                    "power": power,
                }
            )

    power_df = pd.DataFrame(rows)
    power_df.to_csv(ROOT / "power_results.csv", index=False)

    # Power curves.
    fig, ax = plt.subplots(figsize=(9, 6))
    for effect_pct, group in power_df.groupby("effect_size_pct"):
        ax.plot(
            group["n_days"],
            group["power"],
            marker="o",
            label=f"{effect_pct}% CPA difference",
        )
    ax.axhline(0.80, linestyle="--", linewidth=1, label="80% target")
    ax.set_xlabel("Days per group")
    ax.set_ylabel("Estimated power")
    ax.set_ylim(0, 1.02)
    ax.set_title("CPA power analysis")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "power_analysis_cpa.png", dpi=160)
    plt.close(fig)

    # Minimum sample size recommendation.
    recommendation_rows = []
    for effect in effect_sizes:
        subset = power_df[power_df["effect_size_pct"] == int(effect * 100)]
        sufficient = subset[subset["power"] >= TARGET_POWER]
        if sufficient.empty:
            minimum = ">180"
        else:
            minimum = int(sufficient["n_days"].min())

        power_90 = float(subset.loc[subset["n_days"] == 90, "power"].iloc[0])
        recommendation_rows.append(
            {
                "effect_size_pct": int(effect * 100),
                "minimum_days_for_80pct_power": minimum,
                "power_at_90_days": power_90,
                "current_90_days_status": (
                    "sufficient" if power_90 >= TARGET_POWER else "insufficient"
                ),
            }
        )

    rec_df = pd.DataFrame(recommendation_rows)
    rec_df.to_csv(ROOT / "sample_size_recommendations.csv", index=False)

    # Assess FDR-significant observed CPA differences.
    observed_rows = []
    sig_cpa = cpa_results[cpa_results["significant_fdr"] == True].copy()  # noqa: E712
    for _, row in sig_cpa.iterrows():
        mean_a = float(row["mean_cpa_a"])
        mean_b = float(row["mean_cpa_b"])
        baseline = min(mean_a, mean_b)

        if baseline <= 0:
            continue

        observed_pct = abs(mean_b - mean_a) / baseline
        observed_power = empirical_power_cpa(
            observed_pct,
            baseline,
            90,
            n_sim=1000,
            rng=rng,
        )
        needed = (
            90
            if observed_power >= TARGET_POWER
            else minimum_days_for_power(observed_pct, baseline, rng)
        )

        observed_rows.append(
            {
                "group_a": row["group_a"],
                "group_b": row["group_b"],
                "observed_difference_pct": observed_pct * 100,
                "power_at_90_days": observed_power,
                "estimated_days_for_80pct_power": needed,
            }
        )

    observed_df = pd.DataFrame(observed_rows)
    observed_df.to_csv(ROOT / "observed_difference_power.csv", index=False)

    print("\nPower table:")
    print(
        power_df.pivot(
            index="effect_size_pct", columns="n_days", values="power"
        ).round(3)
    )
    print("\nSample-size recommendations:")
    print(rec_df.to_string(index=False))

    # -----------------------------
    # Build required executive memo
    # -----------------------------
    budget = budget.sort_values("recommended_budget", ascending=False)
    top = budget.iloc[0]
    second = budget.iloc[1]

    best_cpa = channel_summary.loc[channel_summary["cpa"].idxmin()]
    best_roas = channel_summary.loc[channel_summary["roas"].idxmax()]

    cpa_sig_count = int(cpa_results["significant_fdr"].sum())
    fisher_sig_count = int(fisher_results["significant_fdr"].sum())

    effects_powered_90 = int(
        (rec_df["current_90_days_status"] == "sufficient").sum()
    )

    cpa_sig = cpa_results[cpa_results["significant_fdr"] == True].sort_values(  # noqa: E712
        "p_value_fdr"
    )
    fisher_sig = fisher_results[
        fisher_results["significant_fdr"] == True  # noqa: E712
    ].sort_values("p_value_fdr")

    finding_lines = []
    for _, row in cpa_sig.head(3).iterrows():
        finding_lines.append(
            f"- **CPA:** {row['group_a']} vs {row['group_b']} remained "
            f"significant after FDR correction "
            f"(adjusted p={row['p_value_fdr']:.4g}, "
            f"Cohen's d={row['cohen_d']:.2f}, {row['effect_size']} effect)."
        )
    if cpa_sig.empty:
        finding_lines.append(
            "- **CPA:** No pairwise CPA difference remained significant after FDR correction."
        )

    for _, row in fisher_sig.head(3).iterrows():
        finding_lines.append(
            f"- **Conversion rate:** {row['group_a']} vs {row['group_b']} "
            f"remained significant after FDR correction "
            f"(adjusted p={row['p_value_fdr']:.4g}, "
            f"odds ratio={row['odds_ratio']:.2f})."
        )
    if fisher_sig.empty:
        finding_lines.append(
            "- **Conversion rate:** No pairwise conversion-rate difference remained significant after FDR correction."
        )

    budget_table = markdown_table(
        budget[["channel", "recommended_budget", "budget_pct"]],
        ["channel", "recommended_budget", "budget_pct"],
    )

    ci_table = markdown_table(
        ci_df[["channel", "mean_daily_cpa", "ci_95_lower", "ci_95_upper"]],
        ["channel", "mean_daily_cpa", "ci_95_lower", "ci_95_upper"],
    )

    period_start = pd.to_datetime(
        pd.read_csv(ROOT / "marketing_data.csv")["date"]
    ).min().date()
    period_end = pd.to_datetime(
        pd.read_csv(ROOT / "marketing_data.csv")["date"]
    ).max().date()

    memo = f"""# Executive Memo: Marketing Channel Budget Recommendation

**Date:** {date.today().isoformat()}  
**Analyst:** {ANALYST}  
**Dataset:** {DATASET_NAME}  
**Source:** {DATASET_URL}  
**Period analyzed:** {period_start} to {period_end}

## Executive Summary

I analyzed seven marketing channels using daily impressions, clicks, conversions, cost, and attributed revenue. Pairwise CPA differences were tested with Welch independent t-tests and Cohen's d, conversion-rate differences were tested with Fisher's exact test, and both Bonferroni and Benjamini-Hochberg FDR corrections were applied to limit false discoveries. The recommended $500,000 monthly allocation gives the largest share to **{top['channel']} (${top['recommended_budget']:,.0f}, {top['budget_pct']:.1%})**, followed by **{second['channel']} (${second['recommended_budget']:,.0f}, {second['budget_pct']:.1%})**. The best aggregate CPA was **{best_cpa['channel']} ({best_cpa['cpa']:.2f})**, while the best aggregate ROAS was **{best_roas['channel']} ({best_roas['roas']:.2f}x)**. These recommendations should be treated as an evidence-based prioritization exercise rather than a production budget decision because the Hugging Face dataset is synthetic benchmark data.

## Key Findings

- FDR-significant CPA comparisons: **{cpa_sig_count}**
- FDR-significant conversion-rate comparisons: **{fisher_sig_count}**
- At 90 days, **{effects_powered_90} of 4** simulated CPA effect sizes (5%, 10%, 15%, 20%) reached the 80% power target.
{chr(10).join(finding_lines)}

## Recommended $500K Monthly Budget

The allocation uses a simple composite score: 40% CPA rank, 40% ROAS rank, and 20% conversion-rate rank, with each channel constrained to a reasonable 5%-25% range.

{budget_table}

## 95% Bootstrap Confidence Intervals for Daily CPA

{ci_table}

## Statistical Caveats

- The selected Hugging Face dataset is **100% synthetic**, so the results demonstrate the statistical workflow but should not be used as real e-commerce evidence.
- The analysis pools six synthetic companies and aggregates them into daily channel totals; a real company may have different audiences, attribution rules, prices, and channel mix.
- Daily observations may have time dependence, while the pairwise t-tests treat observations as independent.
- Multiple comparisons were corrected with both Bonferroni and Benjamini-Hochberg; business decisions use the FDR-adjusted results.
- Statistical significance does not automatically imply practical significance, so Cohen's d and the size of CPA/rate differences should be considered together.
- CPA confidence intervals use nonparametric bootstrap resampling and summarize uncertainty in the observed 90-day period.
- The power analysis assumes approximately normal CPA with a standard deviation equal to 15% of baseline CPA; real campaign variance may differ.

## Recommendations

1. Use the allocation table as a **starting hypothesis**, not an automatic budget transfer.
2. Prioritize the top-ranked channels for controlled incremental-budget tests, while retaining minimum spend in every channel.
3. Do not shift budget based only on uncorrected p-values; use the FDR-adjusted findings and effect sizes.
4. For effect sizes that did not reach 80% power at 90 days, collect the additional sample size indicated in `sample_size_recommendations.csv`.
5. Re-run this exact workflow on the company's real e-commerce channel data before implementing the full $500K allocation.

## Next Steps

Run a controlled 30-90 day budget experiment on the highest-priority channels, track the same conversion definition and attribution window across all channels, and update the analysis when new observations arrive.
"""

    (ROOT / "executive_memo.md").write_text(memo, encoding="utf-8")

    print("\nSaved:")
    print("- power_results.csv")
    print("- sample_size_recommendations.csv")
    print("- observed_difference_power.csv")
    print("- outputs/power_analysis_cpa.png")
    print("- executive_memo.md")


if __name__ == "__main__":
    main()
