# Executive Memo — Marketing Budget Allocation

**To:** Chief Marketing Officer (CMO)  
**From:** Marketing Analytics Team  
**Date:** 2026-11-24  
**Dataset:** Sales Conversion Optimization  
**Source:** https://www.kaggle.com/datasets/loveall/clicks-conversion-tracking  
**Period:** Not available in the dataset  
**Planning budget:** $500,000 per month

## Executive Summary

The analysis evaluates 1,143 advertising records across
3 campaigns (916, 936, and 1178).

Campaign 916 has the lowest observed aggregate cost per approved
conversion, followed by campaign 936. Campaign 1178 has a substantially
higher aggregate CPA but a higher proportion of advertising records
with at least one approved conversion.

The dataset does not contain revenue, dates, or seven distinct marketing
channels. Consequently, a reliable CPA/ROAS composite score and a
production-ready allocation of the full $500,000 cannot be established.

We propose an illustrative planning scenario consisting of a
$150,000 conditional pilot envelope for the three observed campaigns
and a $350,000 uncommitted reserve for four unassessed budget positions.

These amounts are planning assumptions, not authorized expenditures
or statistically optimized allocations.

## Key Findings

### 1. Aggregate Cost per Acquisition

CPA is calculated as total advertising cost divided by total
approved conversions, including advertisements without purchases.

| Campaign | Advertising records | Aggregate CPA | Bootstrap 95% CI |
|---|---:|---:|---:|
| 916 | 54 | 6.24 | 3.92–9.73 |
| 936 | 464 | 15.81 | 12.05–20.94 |
| 1178 | 625 | 63.83 | 57.97–70.63 |

CPA is expressed in dataset cost units; the original currency
is not independently verified.

Campaign 916 has the lowest observed aggregate CPA.
However, its comparatively small advertising sample limits
confidence in scalability.

These bootstrap intervals describe uncertainty under
an independent-record resampling assumption.

### 2. Statistically Significant Differences

Welch's t-tests on advertisement-level CPA values, calculated only
for records with approved purchases, produced the following findings:

- Campaign 916 vs. 1178: campaign 916 has a mean CPA lower by
  approximately 54.15 cost units (Cohen's d = 1.316;
  BH-adjusted p < 0.001).

- Campaign 936 vs. 1178: campaign 936 has a mean CPA lower by
  approximately 50.42 cost units (Cohen's d = 1.164;
  BH-adjusted p < 0.001).

- Campaign 916 vs. 936: no statistically significant difference
  was established in the tested advertisement-level mean CPA
  (uncorrected p = 0.0928).

These t-tests measure a different quantity from aggregate CPA
and exclude records without approved purchases.

Fisher's exact tests on ad-level purchase success indicate that:

- Campaign 1178 exceeds campaign 916 by 17.64 percentage points
  (BH-adjusted p = 0.0200).
- Campaign 1178 exceeds campaign 936 by 25.01 percentage points
  (BH-adjusted p < 0.001).

Ad-level purchase success means an advertisement recorded at least
one approved purchase. It is not a click-to-purchase conversion rate.

### 3. Multiple Comparisons

Nine statistical comparisons were performed across three
metric families.

- Uncorrected: 6 significant comparisons.
- Global Bonferroni: 5 significant comparisons.
- Global BH-FDR: 6 significant comparisons.

The ad-level success comparison between campaigns 916 and 1178
was no longer significant under global Bonferroni correction.

Both statistically significant advertisement-level CPA comparisons
against campaign 1178 remained significant under the stricter correction.

### 4. Statistical Power and Data Adequacy

A hypothetical simulation with normally distributed CPA values
and relative standard deviation of 15% found:

- 5% CPA difference: 58.5% power with 90 observations per group.
- 10% CPA difference: 99.2% power with 90 observations per group.

However, observed CPA variation is substantially larger.
Prospective sample-size calculations using observed variability
suggest that detecting small CPA differences could require
thousands of independent observations per group.

The dataset has no daily observations, so these sample sizes
cannot be converted reliably into calendar days.

## Illustrative Monthly Budget Scenario

The following scenario uses aggregate CPA rankings for observed
campaigns and reserves the remaining budget for unassessed positions.

It does not use ROAS because revenue is unavailable.

| Budget position | Evidence status | Share | Amount |
|---|---|---:|---:|
| Campaign 916 | Observed - pilot only | 15.0% | $75,000 |
| Campaign 936 | Observed - pilot only | 10.0% | $50,000 |
| Campaign 1178 | Observed - pilot only | 5.0% | $25,000 |
| Unassessed channel 1 | Reserved - not committed | 17.5% | $87,500 |
| Unassessed channel 2 | Reserved - not committed | 17.5% | $87,500 |
| Unassessed channel 3 | Reserved - not committed | 17.5% | $87,500 |
| Unassessed channel 4 | Reserved - not committed | 17.5% | $87,500 |
| **Total** | | **100%** | **$500,000** |

**Conditional pilot planning envelope:** $150,000 (30%).

**Uncommitted reserve:** $350,000 (70%).

All seven planning positions comply with the 5% minimum and
35% maximum share constraints.

The four unassessed positions are placeholders, not identified
marketing channels or approved expenditures.

The pilot amounts must not be interpreted as validated spending
capacities. In particular, historical observed spending was far
below the proposed pilot envelopes.

## Recommendations

1. **Prioritize validation of campaign 916.**
   Its observed aggregate CPA is lowest, but its small scale
   requires further testing before budget expansion.

2. **Use campaign 936 as a secondary validation candidate.**
   It has a relatively low aggregate CPA and more observations,
   but no statistically significant difference from campaign 916
   was established using the advertisement-level Welch test.

3. **Review campaign 1178 for efficiency improvements.**
   Its higher ad-level purchase success does not compensate
   automatically for its substantially higher aggregate CPA.

4. **Do not release the full proposed budget immediately.**
   Conduct staged experiments and review marginal CPA, conversion
   volume, and actual financial returns before authorizing spend.

5. **Keep the $350,000 reserve uncommitted** until additional
   channels are identified and evaluated using comparable data.

## Statistical Caveats

- **Dataset scope:** Only three advertising campaigns are observed,
  rather than seven distinct marketing channels.
- **Missing revenue:** ROAS, profit, and contribution margin
  cannot be estimated.
- **Missing time data:** Monthly trends and time-based power
  calculations cannot be verified.
- **Attribution inconsistencies:** Some advertising records contain
  more approved conversions than clicks, including records with
  conversions but zero clicks. These rows were retained rather
  than silently discarded.
- **Selection bias:** Individual-ad CPA analyses exclude ads
  without approved purchases.
- **Independence:** Advertising records may be correlated;
  independence assumptions have not been verified.
- **Confounding:** Campaigns have very different historical
  spending levels, impressions, and potential audiences.
- **Causality:** Observational comparisons do not establish
  that reallocating budget will improve performance.
- **Multiple comparisons:** Corrected significance is more
  defensible than uncorrected significance but does not
  eliminate dataset limitations.
- **Confidence intervals:** Bootstrap intervals rely on
  representative, sufficiently independent advertising records.
- **Practical significance:** A statistically significant
  difference does not guarantee better marginal performance
  at a substantially higher spending level.

## Next Steps

1. Obtain dated campaign-level spending, clicks, approved
   conversions, and attributable revenue.
2. Validate conversion definitions and attribution logic.
3. Identify the remaining four actual marketing channels.
4. Define a prospective experiment with a primary KPI,
   minimum detectable effect, sample-size target, and
   decision thresholds.
5. Run small, controlled budget pilots and assess marginal
   CPA and financial returns.
6. Reassess allocation after sufficient representative
   evidence is collected.

## Final Decision

**Recommendation: Conditional pilot planning only.**

The analysis identifies promising campaigns but does not
support an immediate, fully committed $500,000 monthly allocation.

Additional data and controlled testing are necessary before
scaling marketing spend responsibly.
