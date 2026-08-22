# Executive Memo: Marketing Channel Budget Allocation

**Date:** 2026-08-22
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

- **Conversion rate**: Email converts at a higher rate than Google Ads (diff = 0.02 pp, FDR-adjusted p = 0.0136).
- **Conversion rate**: Email converts at a higher rate than Instagram (diff = 0.05 pp, FDR-adjusted p = 0.0000).
- **Conversion rate**: Email converts at a higher rate than YouTube (diff = 0.06 pp, FDR-adjusted p = 0.0000).
- **Conversion rate**: Facebook converts at a higher rate than Instagram (diff = 0.03 pp, FDR-adjusted p = 0.0011).
- **Conversion rate**: Facebook converts at a higher rate than YouTube (diff = 0.04 pp, FDR-adjusted p = 0.0000).
- **Conversion rate**: Google Ads converts at a higher rate than Instagram (diff = 0.02 pp, FDR-adjusted p = 0.0319).
- **Conversion rate**: Google Ads converts at a higher rate than YouTube (diff = 0.03 pp, FDR-adjusted p = 0.0010).
- **Conversion rate**: Website converts at a higher rate than Instagram (diff = 0.04 pp, FDR-adjusted p = 0.0001).
- **Conversion rate**: Website converts at a higher rate than YouTube (diff = 0.05 pp, FDR-adjusted p = 0.0000).
- **Caveat:** all 9 statistically significant conversion-rate differences above are under 0.5 percentage points. With ~33K rows per channel, even tiny, practically negligible differences become statistically significant — these findings are real but likely not worth reallocating budget over on their own.

**95% confidence intervals for CPA by channel (bootstrap, n=1000 resamples):**

| Channel | Mean CPA | CI Lower | CI Upper | n |
|---|---|---|---|---|
| Email | 12526.39 | 12479.89 | 12573.93 | 33599 |
| Facebook | 12510.90 | 12459.99 | 12557.71 | 32819 |
| Google Ads | 12528.03 | 12484.48 | 12572.60 | 33438 |
| Instagram | 12491.76 | 12448.49 | 12539.31 | 33392 |
| Website | 12487.81 | 12437.26 | 12531.82 | 33360 |
| YouTube | 12481.39 | 12434.63 | 12525.66 | 33392 |

**Data adequacy (power analysis):**

- No CPA comparisons remained significant after FDR correction, so no channel-pair power assessment applies here. See the conversion-rate findings above for what power analysis to prioritize instead.

## Recommendations

**Proposed $500K monthly allocation** (composite score: 50% CPA rank + 50% ROI rank,
floor 5% / ceiling 40% per channel):

| Channel | Recommended Budget | % of Total |
|---|---|---|
| Website | $131,579 | 26.3% |
| Facebook | $105,263 | 21.1% |
| YouTube | $87,719 | 17.5% |
| Email | $58,480 | 11.7% |
| Instagram | $58,480 | 11.7% |
| Google Ads | $58,480 | 11.7% |

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
