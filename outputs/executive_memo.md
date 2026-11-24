# Executive Memo — Marketing Budget Allocation

**To:** Chief Marketing Officer  
**From:** Marketing Analytics Team  
**Date:** 2026-11-24  
**Dataset:** Criteo advertising campaign data  
**Analysis period:** 31 daily observations per campaign (one campaign has 30 valid CPA observations)

## Executive Summary

Analysis of five advertising campaigns identified substantial differences
in cost per acquisition (CPA) and conversion performance.

Campaign 30801593 has the lowest average daily CPA (0.0012).
Campaign 10341182 has the highest overall conversion rate (23.64%).

A provisional allocation of $500,000 is proposed using CPA rankings.
This is a planning scenario, not a revenue-validated budget decision.

## Key Findings

- CPA: 9 of 10 pairwise comparisons were statistically significant.
- Conversion rates: 9 of 10 comparisons were significant.
- Both Bonferroni and Benjamini-Hochberg corrections retained all 9 significant comparisons in each test family.
- Fisher's exact test and Welch's t-test agreed on all 10 conversion-rate comparisons.
- Campaigns 5061834 and 17686799 had no statistically significant CPA difference (p approximately 0.76).
- Campaigns 5061834 and 30801593 had no statistically significant conversion-rate difference.
- The 95% bootstrap CPA confidence interval for campaign 30801593 was approximately 0.0010–0.0013.
- The power simulation suggests 31 days are sufficient for detecting differences of approximately 15–20% under its assumptions, but insufficient for reliable detection of 5–10% differences.


## Bootstrap 95% Confidence Intervals

Intervals are based on mean daily CPA and mean daily conversion rate (conversions / clicks).

|   campaign | metric    |     mean |   CI_lower |   CI_upper |
|-----------:|:----------|---------:|-----------:|-----------:|
|    5061834 | CPA       | 0.014811 |   0.013002 |   0.016602 |
|    5061834 | conv_rate | 0.122436 |   0.107586 |   0.139509 |
|   10341182 | CPA       | 0.003197 |   0.00302  |   0.003384 |
|   10341182 | conv_rate | 0.238687 |   0.226461 |   0.251371 |
|   15398570 | CPA       | 0.006129 |   0.005341 |   0.006943 |
|   15398570 | conv_rate | 0.176962 |   0.16131  |   0.191733 |
|   17686799 | CPA       | 0.01541  |   0.012477 |   0.018774 |
|   17686799 | conv_rate | 0.052902 |   0.044017 |   0.062133 |
|   30801593 | CPA       | 0.001177 |   0.001041 |   0.001337 |
|   30801593 | conv_rate | 0.133276 |   0.118318 |   0.149019 |

## Provisional Monthly Budget Allocation

| Campaign | Allocation | Budget |
|---|---:|---:|
| 30801593 | 33.33% | $166,666.67 |
| 10341182 | 26.67% | $133,333.33 |
| 15398570 | 20.00% | $100,000.00 |
| 5061834 | 13.33% | $66,666.67 |
| 17686799 | 6.67% | $33,333.33 |
| **Total** | **100%** | **$500,000.00** |

The allocation uses CPA-only rankings because revenue data
is unavailable. Each campaign receives between 5% and 35%.


**Allocation method:** Campaigns were ranked by observed mean daily CPA. Lower CPA received a higher ranking score and therefore a larger share of the $500,000 budget. The resulting allocations range from 6.67% to 33.33%, within the required 5%–35% limits. Because revenue is unavailable, ROAS was not used. Budget increases should be tested incrementally before full implementation.

## Recommendations

1. Prioritise campaign 30801593 for further investment testing because it has the lowest observed CPA.
2. Retain campaign 10341182 as a priority because it has the highest conversion rate.
3. Monitor campaigns 5061834 and 17686799 before making strong claims about their relative CPA performance.
4. Validate the proposed allocations through controlled budget increases rather than immediately committing the full amounts.

## Statistical Caveats

- **Dataset limitations:** Advertising costs are anonymised, and revenue is unavailable. Actual dollar CPA, ROAS, profit and profit margin cannot be established.
- **Multiple comparisons:** Bonferroni and BH-FDR corrections were applied separately to each family of ten comparisons.
- **Confidence intervals:** Bootstrap intervals quantify uncertainty in average daily CPA under the sampling assumptions.
- **Ranking fairness:** Campaigns 5061834 and 17686799 have no statistically significant difference in daily CPA (p = 0.7597). Their different CPA rankings do not prove that one is better.
- **Budget scalability:** Campaign 30801593 has the lowest observed CPA and receives the highest proposed allocation. However, we cannot confirm that it can absorb a larger budget while maintaining the same CPA.
- **Practical significance:** Statistical significance does not automatically mean financial importance. Differences must be assessed against actual spending, revenue, profitability and business impact before reallocating budgets.
- **Power:** Simulated power depends on assumed variability and effect sizes; it is not a guarantee of real-world performance.
- **External factors:** Audience targeting, seasonality, attribution, campaign overlap and diminishing returns may influence results.
- **Budget limitation:** The $500,000 allocation is illustrative and cannot be validated against actual spending capacity or revenue.

## Next Steps

1. Obtain reliable revenue and non-anonymised cost data.
2. Recalculate CPA, ROAS and profitability.
3. Test incremental budget increases and monitor marginal performance.
4. Reassess the allocation using observed financial returns and confidence intervals.
