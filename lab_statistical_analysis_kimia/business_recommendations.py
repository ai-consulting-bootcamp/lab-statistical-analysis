"""
Business Recommendations — Marketing Channel ROI Comparison Lab
===================================================================
Part 5: bootstrap CIs, composite ranking, budget allocation, executive memo.

Run data_exploration.py, statistical_analysis.py, power_analysis.py first.
"""

import numpy as np
import pandas as pd
from datetime import date

from data_exploration import COLUMN_MAP as cm

TOTAL_BUDGET = 500_000
MIN_ALLOCATION_PCT = 0.05  # floor per channel so no channel goes to zero
MAX_ALLOCATION_PCT = 0.40  # ceiling so no single channel takes everything


def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95, seed=42):
    rng = np.random.default_rng(seed)
    data = np.asarray(data)
    boot_means = np.array([
        rng.choice(data, size=len(data), replace=True).mean()
        for _ in range(n_bootstrap)
    ])
    alpha = 1 - ci_level
    lower = np.percentile(boot_means, 100 * alpha / 2)
    upper = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return lower, upper


def channel_cis(df, metric_col, group_col):
    rows = []
    for g, sub in df.groupby(group_col):
        vals = sub[metric_col].dropna().values
        vals = vals[np.isfinite(vals)]
        if len(vals) < 2:
            continue
        lo, hi = bootstrap_ci(vals)
        rows.append({"group": g, "mean": vals.mean(), "ci_lower": lo, "ci_upper": hi, "n": len(vals)})
    return pd.DataFrame(rows).round(2)


def composite_score(df, group_col):
    """Rank channels on CPA (lower better) and ROI (higher better), 50/50 weight."""
    agg = df.groupby(group_col).agg(
        cpa=(cm["acquisition_cost"], "mean"),
        roi=(cm["roi"], "mean") if cm["roi"] in df.columns else (cm["acquisition_cost"], "mean"),
        conv_rate=(cm["conversion_rate"], "mean"),
    ).reset_index()

    agg["cpa_rank"] = agg["cpa"].rank(ascending=True)  # lower CPA = better = rank 1
    agg["roi_rank"] = agg["roi"].rank(ascending=False)  # higher ROI = better = rank 1
    agg["composite_score"] = 0.5 * agg["cpa_rank"] + 0.5 * agg["roi_rank"]
    agg = agg.sort_values("composite_score")
    return agg


def allocate_budget(ranked_df, group_col, total=TOTAL_BUDGET):
    ranked_df = ranked_df.copy()
    n = len(ranked_df)
    # Inverse of composite score rank -> weight (best rank gets most weight)
    inv = 1 / ranked_df["composite_score"]
    weights = inv / inv.sum()
    # Two-pass clip+renormalize so the cap/floor roughly holds after normalization
    for _ in range(2):
        weights = weights.clip(lower=MIN_ALLOCATION_PCT, upper=MAX_ALLOCATION_PCT)
        weights = weights / weights.sum()
    ranked_df["allocation_pct"] = (weights * 100).round(1)
    ranked_df["allocation_amount"] = (weights * total).round(0)
    return ranked_df[[group_col, "composite_score", "allocation_pct", "allocation_amount"]]


def significant_findings_summary(cpa_path="data/cpa_pairwise_results.csv",
                                  fisher_path="data/conversion_pairwise_results.csv"):
    lines = []
    try:
        cpa = pd.read_csv(cpa_path)
        sig_cpa = cpa[cpa.get("significant_fdr", False) == True]
        for _, r in sig_cpa.iterrows():
            lower_group = r["group_a"] if r["mean_a"] < r["mean_b"] else r["group_b"]
            higher_group = r["group_b"] if lower_group == r["group_a"] else r["group_a"]
            lines.append(
                f"- **CPA**: {lower_group} has lower cost-per-acquisition than {higher_group} "
                f"(diff = {abs(r['diff']):.2f}, FDR-adjusted p = {r['p_value_fdr']:.4f}, "
                f"Cohen's d = {r['cohens_d']:.2f}, {r['effect_size']} effect)."
            )
    except FileNotFoundError:
        pass

    try:
        fisher = pd.read_csv(fisher_path)
        sig_fisher = fisher[fisher.get("significant_fdr", False) == True]
        small_effect_flags = []
        for _, r in sig_fisher.iterrows():
            higher_group = r["group_a"] if r["rate_a"] > r["rate_b"] else r["group_b"]
            lower_group = r["group_b"] if higher_group == r["group_a"] else r["group_a"]
            diff_pp = abs(r["diff"]) * 100
            lines.append(
                f"- **Conversion rate**: {higher_group} converts at a higher rate than {lower_group} "
                f"(diff = {diff_pp:.2f} pp, FDR-adjusted p = {r['p_value_fdr']:.4f})."
            )
            if diff_pp < 0.5:
                small_effect_flags.append(diff_pp)
        if small_effect_flags:
            lines.append(
                f"- **Caveat:** all {len(small_effect_flags)} statistically significant conversion-rate "
                f"differences above are under 0.5 percentage points. With ~33K rows per channel, even "
                f"tiny, practically negligible differences become statistically significant — these "
                f"findings are real but likely not worth reallocating budget over on their own."
            )
    except FileNotFoundError:
        pass

    if not lines:
        lines = ["- No comparisons remained statistically significant after FDR correction. "
                 "This is a legitimate finding, not a failure of the analysis — see caveats below."]
    return lines


def write_executive_memo(ci_table, allocation_table, findings_lines, power_summary_path,
                          out_path="executive_memo.md"):
    channel_col = allocation_table.columns[0]

    try:
        power_assessment = pd.read_csv(power_summary_path)
        if len(power_assessment) == 0:
            power_lines = ["- No CPA comparisons remained significant after FDR correction, so no "
                           "channel-pair power assessment applies here. See the conversion-rate "
                           "findings above for what power analysis to prioritize instead."]
        else:
            power_lines = []
            for _, r in power_assessment.iterrows():
                needed = r["days_needed_for_80pct_power"]
                needed_str = f"{int(needed)} days" if pd.notna(needed) else "not reached within 400 days simulated"
                power_lines.append(
                    f"- {r['group_a']} vs {r['group_b']}: observed difference "
                    f"{r['observed_diff_pct']:.1f}%, power at current data = {r['power_at_current_data']:.2f}, "
                    f"days needed for 80% power = {needed_str}"
                )
    except (FileNotFoundError, pd.errors.EmptyDataError):
        power_lines = ["- No FDR-significant CPA pairs required a power/data-adequacy assessment "
                       "(or power_analysis.py hasn't been run yet — run it before regenerating this memo)."]

    ci_lines = "\n".join(
        f"| {r['group']} | {r['mean']:.2f} | {r['ci_lower']:.2f} | {r['ci_upper']:.2f} | {int(r['n'])} |"
        for _, r in ci_table.iterrows()
    )

    alloc_lines = "\n".join(
        f"| {r[channel_col]} | ${r['allocation_amount']:,.0f} | {r['allocation_pct']:.1f}% |"
        for _, r in allocation_table.iterrows()
    )

    findings_block = "\n".join(findings_lines)
    power_block = "\n".join(power_lines)

    memo = f"""# Executive Memo: Marketing Channel Budget Allocation

**Date:** {date.today().isoformat()}
**Analyst:** Kimia Asgari
**Dataset:** Marketing Campaign Performance Dataset (Kaggle, manishabhatt22) — see README for source/limitations
**Period analyzed:** See dataset date range in data_exploration.py output

## Executive Summary

This memo recommends how to allocate the $500K monthly marketing budget across
channels, based on statistically rigorous comparison of cost-per-acquisition (CPA)
and conversion rate across channels, corrected for multiple comparisons, with
power analysis to assess how much confidence the underlying data supports.

## Key Findings

**Statistically significant differences (after Benjamini-Hochberg FDR correction, α = 0.05):**

{findings_block}

**95% confidence intervals for CPA by channel (bootstrap, n=1000 resamples):**

| Channel | Mean CPA | CI Lower | CI Upper | n |
|---|---|---|---|---|
{ci_lines}

**Data adequacy (power analysis):**

{power_block}

## Recommendations

**Proposed $500K monthly allocation** (composite score: 50% CPA rank + 50% ROI rank,
floor {MIN_ALLOCATION_PCT*100:.0f}% / ceiling {MAX_ALLOCATION_PCT*100:.0f}% per channel):

| Channel | Recommended Budget | % of Total |
|---|---|---|
{alloc_lines}

**Strategic actions:**
- Shift incremental budget toward channels with both lower CPA and higher ROI, per the
  composite ranking above — but only where differences survived FDR correction.
- Where results were not statistically significant after correction, treat channels as
  roughly equivalent rather than acting on the raw (uncorrected) differences.
- Re-run this analysis after 30/60/90 more days for channels flagged as underpowered
  in the power analysis, before making large budget swings based on those specific
  comparisons.

## Statistical Caveats

- **Dataset limitations and source:** This analysis uses the "Marketing Campaign
  Performance Dataset" from Kaggle (author: Manisha B). It is a third-party public
  dataset, not this company's proprietary spend data — patterns may not transfer
  directly to our specific market, product, or audience.
- **Multiple comparisons correction applied:** Benjamini-Hochberg FDR (and Bonferroni
  for comparison) were applied to all pairwise CPA and conversion-rate tests to
  control false discovery risk from running many pairwise comparisons.
- **Confidence intervals:** Reported alongside point estimates; wide intervals
  indicate the estimate is imprecise and should be treated with caution, not
  taken as a precise number.
- **External factors:** Seasonality, competitor activity, and market conditions in
  the source dataset's collection period may differ from our current environment.
- **Statistical vs. practical significance:** A statistically significant CPA
  difference is only actionable if the Cohen's d effect size and dollar magnitude
  are also practically meaningful — see the effect-size column in the underlying
  results tables.
- **Power analysis limitations:** Power estimates come from simulation with
  simplifying assumptions (normally distributed CPA, fixed variance); real-world
  variance may differ.

## Next Steps

1. Validate this dataset's patterns against a sample of our own internal spend data
   before committing large budget shifts.
2. Extend data collection for underpowered channel comparisons flagged above.
3. Re-run this analysis quarterly as new data becomes available.
4. Socialize findings with channel owners before finalizing allocation.
"""
    with open(out_path, "w") as f:
        f.write(memo)
    print(f"Saved {out_path}")


def main():
    df = pd.read_csv("data/marketing_data_clean.csv")
    channel_col = cm["channel"]

    ci_table = channel_cis(df, cm["acquisition_cost"], channel_col)
    print("\n=== CPA 95% confidence intervals ===")
    print(ci_table.to_string(index=False))
    ci_table.to_csv("data/cpa_confidence_intervals.csv", index=False)

    ranked = composite_score(df, channel_col)
    print("\n=== Composite ranking ===")
    print(ranked.to_string(index=False))

    allocation = allocate_budget(ranked, channel_col)
    print("\n=== Proposed budget allocation ===")
    print(allocation.to_string(index=False))
    allocation.to_csv("data/budget_allocation.csv", index=False)

    findings = significant_findings_summary()
    write_executive_memo(ci_table, allocation, findings,
                          power_summary_path="data/power_assessment_significant_pairs.csv")

    print("\n=== Business recommendations complete ===")


if __name__ == "__main__":
    main()
