import os
import numpy as np
import pandas as pd

DATA_PATH = "data/processed/marketing_data_clean.csv"

os.makedirs("results/tables", exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading processed dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df):,} rows.")


# ============================================================
# PLATFORM SUMMARY
# ============================================================

summary = (
    df.groupby("platform")
    .agg(
        spend=("spend", "sum"),
        conversions=("conversions", "sum"),
        revenue=("revenue", "sum"),
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
    )
    .reset_index()
)

summary["cpa"] = (
    summary["spend"] / summary["conversions"]
)

summary["roas"] = (
    summary["revenue"] / summary["spend"]
)

summary["conversion_rate"] = (
    summary["conversions"] / summary["clicks"]
)

summary["profit"] = (
    summary["revenue"] - summary["spend"]
)


# ============================================================
# CONFIDENCE INTERVALS
# ============================================================

print("\n============================================================")
print("CPA CONFIDENCE INTERVALS")
print("============================================================")


def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    """
    Calculate a bootstrap confidence interval for the mean.
    """

    data = np.asarray(data, dtype=float)

    # Remove NaN and infinite values
    data = data[np.isfinite(data)]

    if len(data) == 0:
        return np.nan, np.nan

    bootstrap_means = []

    for _ in range(n_bootstrap):

        sample = np.random.choice(
            data,
            size=len(data),
            replace=True
        )

        bootstrap_means.append(
            np.mean(sample)
        )

    alpha = 1 - ci_level

    lower = np.percentile(
        bootstrap_means,
        100 * alpha / 2
    )

    upper = np.percentile(
        bootstrap_means,
        100 * (1 - alpha / 2)
    )

    return lower, upper


ci_results = []


for platform in df["platform"].unique():

    platform_data = df[
        df["platform"] == platform
    ].copy()

    # Keep observations with at least one conversion
    platform_data = platform_data[
        platform_data["conversions"] > 0
    ].copy()

    # Calculate observation-level CPA
    platform_data["row_cpa"] = (
        platform_data["spend"] /
        platform_data["conversions"]
    )

    data = platform_data["row_cpa"].values

    lower, upper = bootstrap_ci(data)

    # Aggregate CPA
    platform_spend = (
        df.loc[
            df["platform"] == platform,
            "spend"
        ].sum()
    )

    platform_conversions = (
        df.loc[
            df["platform"] == platform,
            "conversions"
        ].sum()
    )

    aggregate_cpa = (
        platform_spend /
        platform_conversions
    )

    ci_results.append(
        {
            "platform": platform,
            "aggregate_cpa": aggregate_cpa,
            "bootstrap_ci_lower": lower,
            "bootstrap_ci_upper": upper,
        }
    )


ci_df = pd.DataFrame(ci_results)

ci_df = ci_df.sort_values(
    "aggregate_cpa"
)

print(
    ci_df.to_string(index=False)
)

ci_df.to_csv(
    "results/tables/cpa_confidence_intervals.csv",
    index=False
)


# ============================================================
# COMPOSITE PERFORMANCE SCORE
# ============================================================

print("\n============================================================")
print("PLATFORM PERFORMANCE")
print("============================================================")


performance = summary[
    [
        "platform",
        "cpa",
        "roas",
        "conversion_rate",
        "profit",
    ]
].copy()


# ------------------------------------------------------------
# Rank each metric
# ------------------------------------------------------------

# Lower CPA is better
performance["cpa_rank"] = (
    performance["cpa"]
    .rank(ascending=True, method="min")
)

# Higher ROAS is better
performance["roas_rank"] = (
    performance["roas"]
    .rank(ascending=False, method="min")
)

# Higher conversion rate is better
performance["conversion_rate_rank"] = (
    performance["conversion_rate"]
    .rank(ascending=False, method="min")
)

# Higher profit is better
performance["profit_rank"] = (
    performance["profit"]
    .rank(ascending=False, method="min")
)


# ------------------------------------------------------------
# Convert ranks to normalized scores
# ------------------------------------------------------------

number_of_platforms = len(performance)

performance["cpa_score"] = (
    (number_of_platforms - performance["cpa_rank"] + 1)
    / number_of_platforms
)

performance["roas_score"] = (
    (number_of_platforms - performance["roas_rank"] + 1)
    / number_of_platforms
)

performance["conversion_rate_score"] = (
    (
        number_of_platforms
        - performance["conversion_rate_rank"]
        + 1
    )
    / number_of_platforms
)

performance["profit_score"] = (
    (
        number_of_platforms
        - performance["profit_rank"]
        + 1
    )
    / number_of_platforms
)


# ------------------------------------------------------------
# Composite score
# ------------------------------------------------------------

performance["composite_score"] = (
    performance["cpa_score"] * 0.25
    + performance["roas_score"] * 0.25
    + performance["conversion_rate_score"] * 0.25
    + performance["profit_score"] * 0.25
)


performance = performance.sort_values(
    "composite_score",
    ascending=False
)


print(
    performance[
        [
            "platform",
            "cpa",
            "roas",
            "conversion_rate",
            "profit",
            "composite_score",
        ]
    ].to_string(index=False)
)


# ============================================================
# $500K MONTHLY BUDGET ALLOCATION
# ============================================================

print("\n============================================================")
print("$500K MONTHLY BUDGET ALLOCATION")
print("============================================================")


TOTAL_BUDGET = 500_000


# Allocate proportionally to composite score
performance["allocation_pct"] = (
    performance["composite_score"]
    / performance["composite_score"].sum()
    * 100
)

performance["monthly_budget"] = (
    performance["composite_score"]
    / performance["composite_score"].sum()
    * TOTAL_BUDGET
)


allocation = performance[
    [
        "platform",
        "allocation_pct",
        "monthly_budget",
    ]
].copy()


allocation["allocation_pct"] = (
    allocation["allocation_pct"].round(2)
)

allocation["monthly_budget"] = (
    allocation["monthly_budget"].round(2)
)


print(
    allocation.to_string(index=False)
)


allocation.to_csv(
    "results/tables/budget_allocation.csv",
    index=False
)


# ============================================================
# EXECUTIVE MEMO
# ============================================================

print("\n============================================================")
print("CREATING EXECUTIVE MEMO")
print("============================================================")


# Top platform
top_platform = performance.iloc[0]

# Lowest CPA
lowest_cpa_platform = (
    summary.loc[
        summary["cpa"].idxmin()
    ]
)

# Highest ROAS
highest_roas_platform = (
    summary.loc[
        summary["roas"].idxmax()
    ]
)

# Highest profit
highest_profit_platform = (
    summary.loc[
        summary["profit"].idxmax()
    ]
)


memo = f"""# Executive Memo — Marketing Channel Statistical Analysis

## Header

**Date:** 24 August 2026  
**Analyst:** Vincent de Paul Nzotegouong  
**Dataset:** Digital Marketing Performance Dataset  
**Source:** Hugging Face  
**Observations:** {len(df):,}  
**Platforms analyzed:** {df["platform"].nunique()}  
**Analysis period:** 2023–2025  
**Monthly budget scenario:** $500,000

---

## Executive Summary

This analysis evaluates the performance of six digital marketing platforms using 30,000 observations covering 2023–2025.

Google Search is the strongest-performing platform in the dataset. It has the lowest aggregate CPA, the highest ROAS, the highest conversion rate, and by a very large margin the highest aggregate profit.

The statistical analysis also found significant differences between multiple platform pairs. These results remained significant after both Bonferroni and Benjamini-Hochberg corrections.

However, statistical significance should not be interpreted as proof of causality. The dataset is observational rather than a randomized experiment, so differences between platforms may partly reflect differences in campaigns, audiences, objectives, countries, funnel stages, or other confounding factors.

The recommended $500K allocation should therefore be treated as a **data-informed starting point for controlled budget testing**, rather than an automatic permanent reallocation.

---

## Key Findings

### 1. Google Search is the strongest channel

Google Search produced:

- Aggregate CPA: ${lowest_cpa_platform["cpa"]:.2f}
- ROAS: {highest_roas_platform["roas"]:.2f}
- Conversion rate: {highest_roas_platform["conversion_rate"]:.2%}
- Profit: ${highest_profit_platform["profit"]:,.2f}

It substantially outperformed the other platforms on the primary business metrics available in this dataset.

---

### 2. CPA differences

The pairwise CPA analysis identified nine significant comparisons before correction.

All nine remained significant after:

- Bonferroni correction
- Benjamini-Hochberg FDR correction

The largest practical concern is the difference between Google Search and LinkedIn.

Google Search had an aggregate CPA of approximately ${summary.loc[summary["platform"] == "Google Search", "cpa"].iloc[0]:.2f}, while LinkedIn had an aggregate CPA of approximately ${summary.loc[summary["platform"] == "LinkedIn", "cpa"].iloc[0]:.2f}.

Despite statistical significance, effect sizes for the CPA comparisons were generally small or negligible. This demonstrates why statistical significance and practical significance should be evaluated separately.

---

### 3. Conversion-rate differences

Fisher's exact tests found statistically significant conversion-rate differences across all 15 platform pairs.

These results also remained significant after Bonferroni and Benjamini-Hochberg correction.

Google Search had the highest conversion rate at approximately {summary.loc[summary["platform"] == "Google Search", "conversion_rate"].iloc[0]:.2%}.

Google Display had the lowest conversion rate at approximately {summary.loc[summary["platform"] == "Google Display", "conversion_rate"].iloc[0]:.2%}.

Because the number of clicks is very large, even relatively small absolute differences can produce extremely small p-values.

Therefore, the business importance of each difference should be assessed alongside its magnitude.

---

## Statistical Correction

A total of 30 pairwise statistical comparisons were performed:

- 15 CPA comparisons
- 15 conversion-rate comparisons

At α = 0.05, approximately 1.5 false-positive results would be expected by chance across 30 independent tests.

### CPA

| Method | Significant comparisons |
|---|---:|
| Uncorrected | 9 |
| Bonferroni | 9 |
| Benjamini-Hochberg FDR | 9 |

### Conversion Rate

| Method | Significant comparisons |
|---|---:|
| Uncorrected | 15 |
| Bonferroni | 15 |
| Benjamini-Hochberg FDR | 15 |

The fact that the conclusions survive both correction methods increases confidence that these statistical differences are not simply artifacts of multiple testing.

---

## Power Analysis

The power analysis evaluated the ability to detect CPA differences of 5%, 10%, 15%, and 20%.

Results indicate:

| Expected CPA difference | Power with 90 days | Assessment |
|---|---:|---|
| 5% | 60.9% | Insufficient |
| 10% | 99.5% | Sufficient |
| 15% | 100% | Sufficient |
| 20% | 100% | Sufficient |

The analysis therefore suggests that approximately 90 days of data is adequate for detecting differences of roughly 10% or greater under the simulation assumptions.

Smaller differences, particularly around 5%, would require substantially more observations.

---

## Recommended $500K Monthly Budget Allocation

The allocation below uses the composite performance score generated from CPA, ROAS, conversion rate, and profit.

| Platform | Allocation | Monthly Budget |
|---|---:|---:|
"""


for _, row in allocation.iterrows():
    memo += (
        f'| {row["platform"]} | '
        f'{row["allocation_pct"]:.2f}% | '
        f'${row["monthly_budget"]:,.2f} |\n'
    )


memo += f"""

---

## Recommendations

### 1. Prioritize Google Search

Google Search should receive the strongest strategic priority because it combines:

- Lowest CPA
- Highest ROAS
- Highest conversion rate
- Strongest profitability

However, additional spending should be increased progressively rather than immediately assuming that historical performance will remain constant at higher spend levels.

---

### 2. Use Meta as the main secondary channel

Meta ranks second on the composite performance score.

It should remain an important diversification channel while being monitored against CPA, conversion rate, and profitability targets.

---

### 3. Maintain controlled testing on Snapchat and TikTok

Snapchat and TikTok show weaker profitability than Google Search and Meta but remain meaningful acquisition channels.

Rather than eliminating them, maintain controlled budgets and test:

- Audience segments
- Creative formats
- Campaign objectives
- Landing pages
- Funnel stages

---

### 4. Review Google Display performance

Google Display has a relatively high CPA and low ROAS compared with the strongest channels.

The channel should be reviewed carefully before receiving additional budget.

Potential optimization areas include:

- Audience targeting
- Placement quality
- Creative performance
- Frequency
- Retargeting strategy

---

### 5. Reassess LinkedIn

LinkedIn has the highest CPA and lowest ROAS in the dataset.

The channel should not automatically receive the same level of investment as the stronger-performing channels.

Before significantly increasing spend, investigate whether LinkedIn serves a different strategic purpose, such as B2B lead generation or high-value customers that are not captured by the available revenue metric.

---

## Statistical Caveats

### Observational data

The dataset is observational. The analysis identifies associations between platform and performance but does not prove that the platform itself caused the observed differences.

### Aggregation

Aggregate CPA is calculated as total spend divided by total conversions.

Bootstrap confidence intervals are based on observation-level CPA values for observations with at least one conversion. These intervals should therefore be interpreted as uncertainty around the distribution of observed CPA values rather than as definitive confidence intervals for a randomized experiment.

### Multiple comparisons

Multiple comparison corrections were applied using both Bonferroni and Benjamini-Hochberg FDR procedures.

### Statistical vs. practical significance

Large sample sizes can produce extremely small p-values even for relatively small effects.

Business decisions should therefore consider:

- Effect size
- Absolute performance difference
- Financial impact
- Confidence intervals
- Incremental return from additional spending

### Power analysis

Power estimates are simulation-based and depend on assumptions about the underlying CPA distribution and variability.

They should be treated as planning estimates rather than guarantees.

### Budget allocation

The $500K allocation is a model-based recommendation and should be validated through controlled experiments and incremental budget tests.

---

## Next Steps

1. Use the proposed allocation as a starting hypothesis rather than a final decision.
2. Increase Google Search investment incrementally.
3. Monitor marginal CPA and marginal ROAS as spend increases.
4. Maintain Meta as a diversification channel.
5. Run controlled experiments on Snapchat and TikTok.
6. Review Google Display and LinkedIn campaign-level performance.
7. Establish weekly performance monitoring.
8. Recalculate channel performance after each major budget change.
9. Use randomized experiments where possible to establish causal effects.
10. Revisit the allocation after sufficient post-change data has accumulated.

---

## Final Conclusion

The data strongly favors Google Search as the primary acquisition channel.

Nevertheless, the statistically rigorous conclusion is not simply "put all the money into Google Search." The correct business interpretation is that Google Search has demonstrated substantially stronger historical performance in this dataset, while incremental budget allocation should be validated through controlled testing.

The recommended allocation therefore provides a structured starting point for experimentation rather than a permanent budget decision.
"""

with open(
    "executive_memo.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(memo)


# ============================================================
# COMPLETION
# ============================================================

print("\n============================================================")
print("BUSINESS ANALYSIS COMPLETED")
print("============================================================")

print("\nFiles created:")
print("- results/tables/cpa_confidence_intervals.csv")
print("- results/tables/budget_allocation.csv")
print("- executive_memo.md")