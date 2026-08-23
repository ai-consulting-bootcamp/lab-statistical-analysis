# Marketing Channel Performance — Executive Memo

**Analyst:** Nevena  
**Dataset:** Facebook advertising campaign performance dataset  
**Campaigns analyzed:** 916, 936, 1178  
**Monthly budget considered:** $500,000

## Executive Summary

The analysis compared three Facebook advertising campaigns using cost efficiency, purchase performance, statistical significance, effect size, multiple-comparison correction, and power analysis. Campaigns 916 and 936 showed substantially better cost efficiency than campaign 1178. Campaign 1178 had an aggregate CPA of **63.83**, compared with **6.24** for campaign 916 and **15.81** for campaign 936. Pairwise Welch t-tests found campaign 1178's CPA to be significantly higher than both 916 and 936, with large effect sizes, and both differences remained significant after Bonferroni and Benjamini-Hochberg corrections. Purchase rates ranged from **32.67% to 41.38%**, but none of the pairwise differences were statistically significant. Based on the combined evidence, the recommended monthly budget allocation is **35% to campaign 916, 45% to campaign 936, and 20% to campaign 1178**.

## Key Findings

### Cost per Acquisition

Aggregate campaign CPA was:

| Campaign | CPA |
|---|---:|
| 916 | 6.24 |
| 936 | 15.81 |
| 1178 | 63.83 |

Pairwise analysis of ad-level CPA showed:

- **916 vs 936:** no statistically significant difference (`p = 0.128`).
- **916 vs 1178:** statistically significant difference with a large effect size (`Cohen's d = 1.34`).
- **936 vs 1178:** statistically significant difference with a large effect size (`Cohen's d = 1.24`).

The two significant differences remained significant after both Bonferroni and Benjamini-Hochberg FDR correction.

### Purchase Rate

Aggregate purchase rates were:

| Campaign | Purchase Rate |
|---|---:|
| 916 | 41.38% |
| 936 | 34.08% |
| 1178 | 32.67% |

Although campaign 916 had the highest observed purchase rate, Fisher's exact tests found **no statistically significant pairwise differences**. The observed ranking should therefore not be interpreted as evidence that campaign 916 has a genuinely higher purchase probability.

### Confidence Intervals

Bootstrap 95% confidence intervals for mean ad-level CPA among ads with at least one approved conversion were:

| Campaign | Mean CPA | 95% CI |
|---|---:|---:|
| 916 | 3.14 | 1.64–5.07 |
| 936 | 5.50 | 3.46–8.19 |
| 1178 | 58.41 | 52.63–64.37 |

The results reinforce the large separation between campaign 1178 and the other two campaigns.

### Data Adequacy and Power

Simulation-based power analysis showed that approximately:

- **180 observations** per group were required to detect a 5% CPA difference with at least 80% power.
- **60 observations** were required for a 10% difference.
- **30 observations** were sufficient for 15–20% differences under the simulation assumptions.

The observed CPA differences involving campaign 1178 were much larger than these scenarios, and estimated power for both significant comparisons was approximately **1.00** under the simulation assumptions.

## Budget Recommendation

| Campaign | Recommended Share | Monthly Budget |
|---|---:|---:|
| 916 | 35% | $175,000 |
| 936 | 45% | $225,000 |
| 1178 | 20% | $100,000 |
| **Total** | **100%** | **$500,000** |

Campaign 936 receives the largest allocation because it combines relatively low CPA with a much larger evidence base than campaign 916. Campaign 916 receives substantial additional investment because it showed the best observed efficiency, but its allocation is limited because its sample size is much smaller and its advantage over campaign 936 was not statistically significant. Campaign 1178 receives a reduced but non-zero allocation because its CPA was significantly worse, while retaining some budget recognizes its demonstrated ability to operate at substantially larger scale.

## Statistical Caveats

- The three campaign groups are highly unequal in size.
- Ad-level CPA is undefined for ads with zero approved conversions, so CPA comparisons include only ads that produced at least one approved conversion.
- CPA distributions are strongly right-skewed, especially for campaign 936; Welch's t-test was therefore used instead of assuming equal variances.
- The dataset contains no time variable, so trends, seasonality, and performance changes over time cannot be evaluated.
- Purchase-rate differences were not statistically significant even though their observed percentages differ.
- The power simulation assumes approximately normally distributed CPA values with standard deviation equal to 15% of baseline CPA. Actual CPA variability is considerably larger and more skewed, so the simulated power estimates should be treated as approximate.
- Statistical significance does not automatically imply business significance; effect sizes, costs, scale, and uncertainty were considered together.

## Next Steps

1. Increase campaign 936 investment while monitoring whether CPA remains stable at higher spend.
2. Scale campaign 916 cautiously and collect substantially more observations before concluding that it is superior to campaign 936.
3. Reduce campaign 1178 spend and investigate why acquisition costs are substantially higher.
4. Continue collecting campaign-level performance data, preferably with dates, to enable time-based analysis and stronger future testing.
5. Re-evaluate the allocation after sufficient new data have been collected.