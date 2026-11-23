# Executive Memo: Marketing Channel ROI Analysis

**Date:** November 23, 2026  
**Analyst:** Julia  
**Dataset:** Marketing Campaign Performance Dataset (200k)  
**Period analyzed:** January 1, 2021 through December 31, 2021

## Executive Summary

The data does not show a statistically reliable difference in daily CPA after correction for the 15 channel-pair comparisons. Website has the lowest aggregate CPA ($281.93), while YouTube has the lowest conversion rate (7.976%). Conversion-rate differences are more readily detectable: nine of 15 pairwise comparisons remain significant after Benjamini-Hochberg correction, although the absolute differences are small (roughly 0.01 to 0.06 percentage points).

## Key Findings

### Aggregate performance

| Channel | CPA | ROAS | Conversion rate |
|---|---:|---:|---:|
| Email | $283.34 | 5.9986 | 8.0319% |
| Facebook | $283.89 | 6.0267 | 8.0183% |
| Google Ads | $285.22 | 6.0078 | 8.0079% |
| Instagram | $285.13 | 5.9865 | 7.9869% |
| Website | $281.93 | 6.0110 | 8.0244% |
| YouTube | $284.75 | 6.0010 | 7.9761% |

- Website has the lowest aggregate CPA and is the strongest CPA candidate.
- Facebook has the highest aggregate ROAS.
- Email has the highest aggregate conversion rate.
- No pair of channels has a CPA difference that remains significant after FDR correction.
- Nine conversion-rate pairs are significant after FDR correction; Bonferroni retains seven.

### Statistical comparisons

The Welch t-tests found no CPA differences at the uncorrected 0.05 level. Fisher's exact test found nine significant conversion-rate pairs before correction and nine after Benjamini-Hochberg correction. Bonferroni was more conservative, retaining seven conversion-rate pairs.

The 95% bootstrap intervals for mean daily CPA overlap substantially:

| Channel | Mean CPA | 95% CI |
|---|---:|---:|
| Email | $285.07 | $282.80-$287.64 |
| Facebook | $285.57 | $283.10-$287.98 |
| Google Ads | $286.80 | $284.34-$289.21 |
| Instagram | $286.93 | $284.16-$289.73 |
| Website | $283.62 | $281.04-$286.23 |
| YouTube | $286.44 | $283.94-$288.99 |

## Recommendations

I use a weighted rank composite with CPA at 50%, conversion rate at 30%, and ROAS at 20%. Lower CPA receives a better rank; higher conversion and ROAS receive better ranks. The resulting proposed allocation for a $500,000 monthly budget, constrained to 10%-25% per channel, is:

| Channel | Proposed allocation | Share |
|---|---:|---:|
| YouTube | $97,619 | 19.52% |
| Website | $95,238 | 19.05% |
| Email | $90,476 | 18.10% |
| Instagram | $88,095 | 17.62% |
| Facebook | $73,810 | 14.76% |
| Google Ads | $54,762 | 10.95% |

This allocation should be treated as a starting portfolio rather than a definitive reroute of budget:

1. Preserve Email and Website investment because they rank highly on conversion and CPA.
2. Maintain a controlled Facebook test; it has the highest ROAS but does not show enough CPA separation to justify an aggressive shift on CPA alone.
3. Reallocate cautiously into YouTube rather than making a large immediate change, since the ranking is composite and CPA differences are not FDR-significant.
4. Keep Google Ads near the minimum until additional experiments improve evidence.

## Data Adequacy and Power

The empirical simulation indicates that 90 days provide approximately:

- 59% power for a 5% CPA difference
- 98% power for a 10% CPA difference
- 100% power for 15% and 20% CPA differences

For 80% power, the simulation requires about 180 days for a 5% effect, 60 days for 10%, and 30 days for 15% or 20%. The current one-year date range is adequate for detecting moderate or large CPA effects, but not reliably adequate for a small 5% effect. No FDR-significant CPA pair was available for a post-test observed-effect adequacy assessment.

## Statistical Caveats

- The data is observational; channel-level association does not establish causation.
- Conversions are estimated from reported clicks and conversion rates rather than observed individual conversion outcomes.
- Revenue is derived from acquisition cost and reported ROI because no explicit revenue field is present.
- Fisher exact tests use large aggregate contingency tables, making tiny practical differences easier to classify as significant.
- CPA was tested at the campaign-date aggregate level; unobserved seasonality and channel-level targeting differences may affect uncertainty.
- Bonferroni is conservative, while Benjamini-Hochberg controls false-discovery rate.
- Composite ranks and allocation are descriptive decision aids, not a randomized-experiment result.
- External factors such as audience mix, creative quality, market saturation, and seasonality are not modeled.
- The $500K recommendation should be validated with holdout tests and production-level experimentation.

## Next Steps

1. Run 30-60 day incremental budget experiments or randomized holdouts on the highest-ranked channels.
2. Track CPA, conversion rate, ROAS, incrementality, and profit by channel in one consistent dashboard.
3. Add an explicit revenue field and observed conversions if available.
4. Re-run pairwise testing with predeclared hypotheses and preserve Bonferroni or FDR correction.
5. Reassess allocation after collecting at least 90 comparable operational days.
