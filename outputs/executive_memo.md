# Executive memo — Marketing budget allocation

**To:** CMO  
**From:** Sandra  
**Date:** 23 November 2026  
**Dataset:** Digital Marketing Metrics & KPIs to Measure  
**Source:** https://www.kaggle.com/datasets/sinderpreet/analyze-the-marketing-spending  
**Period:** 1–28 February 2021

## Executive summary

Influencer has the lowest monthly CPA and the highest ROAS.
Social has a ROAS below 1, so its attributed revenue is lower
than its advertising cost.

The table below is a starting budget scenario for the lab.
It is not a proven optimal allocation or a forecast.
Test changes before using this plan for a real business.

## Key findings

- The original data contains 308 campaign-day records.
  We grouped them into four categories with 28 days each.
- Monthly CPA is 2,755.58 for influencer, 3,209.88 for media,
  4,179.23 for search and 5,236.62 for social.
  These amounts use the dataset's unverified currency.
- ROAS is 2.54 for influencer, 1.22 for media,
  1.07 for search and 0.86 for social.
- All six daily CPA comparisons remain significant after
  Bonferroni and BH correction. All CPA effect sizes are large.
- All six conversion comparisons remain significant with BH
  for both Welch and Fisher.
- Bonferroni keeps four Welch conversion comparisons and five
  Fisher comparisons. Influencer versus media does not remain
  significant with Bonferroni in either conversion test.
- The monthly conversion gap between influencer and media is
  only about 0.029 percentage points. Statistical significance
  alone does not show business value.

## Data adequacy

At 28 days, simulated power is 19.3% for a 5% CPA difference,
66.9% for 10%, 95.8% for 15% and 99.7% for 20%.

For a 5% difference, 180 days is the smallest tested sample size
reaching 80% power. For 10%, it is 60 days.
These are tested sizes, not exact minimum requirements.

The simulation assumes independent days, a standard deviation
of 15% of baseline CPA, and uncorrected alpha of 0.05.
Planning with Bonferroni would require a separate power calculation.
Scenarios using observed gaps do not independently confirm findings.

## Recommendations

| Channel | Budget share | Budget (USD) |
| --- | --- | --- |
| influencer | 35.00% | 175,000.00 |
| media | 32.50% | 162,500.00 |
| search | 21.67% | 108,333.33 |
| social | 10.83% | 54,166.67 |

Total proposed budget: **500,000 USD**.

The score uses monthly CPA and ROAS with equal weights.
Higher scores receive more budget, with a 5% minimum and
35% maximum per category. Both metrics give the same ranking.

Prioritize controlled tests in influencer and media.
Review social campaigns before increasing their budget.
Keep search under review because its ROAS is only slightly above 1.

The ranking does not measure uncertainty, future capacity or
returns from additional spending. The 35% cap is a planning rule,
not evidence that a channel can absorb that amount.
The plan retains some social budget for testing; this does not
show that social is profitable.

## Confidence intervals

The following intervals describe mean daily CPA in dataset
currency units, using 1,000 bootstrap samples.

| Channel | Valid days | Mean daily CPA | 95% interval |
| --- | --- | --- | --- |
| influencer | 28 | 2,716.16 | 2,560.70–2,847.84 |
| media | 27 | 3,071.59 | 2,904.57–3,223.27 |
| search | 27 | 4,210.97 | 4,012.07–4,484.91 |
| social | 28 | 5,242.34 | 5,001.01–5,498.56 |

These means differ from monthly CPA, which is total cost divided
by total conversions.

## Statistical caveats

- The file was downloaded from Kaggle. Its original business
  source, real or synthetic status, currency and attribution rules
  were not independently verified.
- Data covers only one month in 2021. It does not establish
  current performance or seasonal patterns.
- Channel categories contain different campaign mixes.
  Observational differences do not prove causation.
- Welch follows the lab template. Channels share dates, so
  common daily effects may affect independence.
- Fisher assumes independent clicks with binary conversion
  outcomes. Repeated users or multiple orders cannot be checked.
- Corrections apply separately to three families of six tests.
  They do not jointly control error across all 18 tests.
  BH is reported for exploration; Bonferroni provides a more
  cautious comparison. No correction makes a result certain.
- Media and search each have one day with zero conversions.
  Daily CPA analysis excludes those undefined ratios.
  Monthly CPA includes all costs. The exclusion may affect
  daily mean comparisons.
- Bootstrap intervals are individual 95% intervals, without
  multiple-comparison adjustment or time-dependence adjustment.
- Revenue minus advertising cost is not net profit.
  Product, delivery and other business costs are missing.
- The USD allocation is a lab scenario. Historical amounts
  were not converted to USD, and future returns are not predicted.

## Next steps

1. Verify source, currency, tracking and conversion definitions.
2. Define a useful business improvement before a new test.
3. Plan sample size using realistic variability and the chosen
   correction, then run a fixed-size controlled test.
4. Check channel capacity, attribution and full costs.
5. Monitor CPA, ROAS and conversion quality during any rollout.
