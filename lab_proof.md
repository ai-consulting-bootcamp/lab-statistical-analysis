# Lab proof — Marketing Channel Statistical Analysis

**Student:** Sandra  
**Date:** 23 November 2026

## 1. Code and input

- [Completed notebook](lab_statistical_analysis_STUDENT.ipynb)
- [Original input](Marketing.csv)
- [Prepared dataset](outputs/marketing_data.csv)
- [Setup and file map](README.md)

Dataset: [Digital Marketing Metrics & KPIs to Measure — Kaggle](https://www.kaggle.com/datasets/sinderpreet/analyze-the-marketing-spending)

The input contains 308 campaign-day records and 11 columns,
covering 1–28 February 2021.

The original business source, real or synthetic status,
currency and attribution rules were not independently verified.

## 2. Recorded run

Environment: Python 3.11, Jupyter in VS Code, bootcamp-env.

I ran the notebook cells in order using Marketing.csv as input.
The submitted notebook contains the saved outputs.

Preparation:
- Renamed date, channel, cost and conversion columns.
- Checked missing values, negative values and invalid counts.
- Checked duplicate campaign-date records.
- Found no invalid rows.
- Summed campaign data by channel category and date.
- Produced 112 records: four categories with 28 days each.
- Kept two records with zero conversions.

The analysis includes:
- Monthly metrics and daily distributions.
- Six Welch comparisons for daily CPA.
- Six Welch comparisons for daily conversion rates.
- Six Fisher comparisons using monthly counts.
- Cohen's d for the Welch comparisons.
- Bonferroni and BH corrections within each test family.
- Power simulations and sample size planning.
- Bootstrap confidence intervals.
- A proposed USD 500,000 budget scenario.

## 3. Evidence and results

### Multiple comparisons

| Test family | Uncorrected | Bonferroni | BH-FDR |
| --- | ---: | ---: | ---: |
| Daily CPA — Welch | 6 | 6 | 6 |
| Daily conversion rate — Welch | 6 | 4 | 6 |
| Monthly conversion counts — Fisher | 6 | 5 | 6 |

Each correction applies to a separate family of six tests.
This does not jointly control error across all 18 tests.
Losing significance does not prove that a result was false.

Supporting tables:
- [Monthly channel metrics](outputs/channel_summary.csv)
- [Daily variability](outputs/channel_variability.csv)
- [CPA comparisons](outputs/cpa_ttests.csv)
- [Daily conversion comparisons](outputs/conversion_rate_ttests.csv)
- [Conversion counts](outputs/conversion_counts.csv)
- [Fisher comparisons](outputs/fisher_results.csv)
- [Test agreement](outputs/conversion_test_comparison.csv)
- [Correction summary](outputs/correction_summary.csv)

### Power and uncertainty

With 28 days, simulated power was:
- 19.3% for a 5% CPA difference.
- 66.9% for a 10% difference.
- 95.8% for a 15% difference.
- 99.7% for a 20% difference.

For a 5% difference, 180 days was the smallest tested size
reaching 80% power. This is not the exact minimum.

The simulation assumes independent days, a standard deviation
of 15% of baseline CPA and uncorrected alpha of 0.05.
Scenarios based on observed gaps are not independent validation.

- [Power results](outputs/power_results.csv)
- [Sample size plan](outputs/sample_size_plan.csv)
- [Observed-gap scenarios](outputs/cpa_pair_power.csv)
- [Mean daily CPA confidence intervals](outputs/cpa_confidence_intervals.csv)

### Charts

- [Monthly metrics](outputs/group_metrics_overview.png)
- [Daily distributions](outputs/group_distributions.png)
- [CPA p-value heatmap](outputs/metric_comparison_heatmap.png)
- [Monthly conversion rates](outputs/rate_comparison.png)
- [Correction comparison](outputs/correction_comparison.png)
- [Power curves](outputs/power_analysis_cpa.png)

## 4. Final output

- [Executive memo](outputs/executive_memo.md)
- [Budget allocation](outputs/budget_allocation.csv)

| Channel | Proposed share | Proposed budget (USD) |
| --- | ---: | ---: |
| Influencer | 35.00% | 175,000.00 |
| Media | 32.50% | 162,500.00 |
| Search | 21.67% | 108,333.33 |
| Social | 10.83% | 54,166.67 |
| Total | 100.00% | 500,000.00 |

The score gives equal weight to monthly CPA and ROAS.
Shares have a 5% minimum and a 35% maximum.

Influencer has the lowest monthly CPA and highest ROAS.
Social has a ROAS below 1.

This allocation is a planning scenario, not a proven optimum
or a forecast. Historical currency was not converted to USD.
Controlled tests and capacity checks are needed before rollout.

## 5. Limitation encountered

Media and search each have one day with zero conversions.
Daily CPA is undefined for those days.

I kept both records in the prepared dataset and monthly totals.
Daily CPA comparisons and bootstrap intervals use only days
with defined CPA: 27 for media and search, 28 for the others.
This exclusion may affect the daily comparisons.

Other limits:
- Only one month of historical data is available.
- Shared dates and time dependence may affect independence.
- Fisher's independent binary outcome assumption cannot be
  fully checked from aggregated click and order counts.
- Bootstrap intervals do not adjust for time dependence or
  multiple comparisons.
- Revenue minus advertising cost is not net profit.
- Observational comparisons do not prove causation.

## 6. Optional work

The optional reflection was not completed.