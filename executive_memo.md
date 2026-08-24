# Executive Memo: Marketing Channel Budget Allocation

**Date:** August 24, 2026
**Analyst:** Nelly Pourmehr
**Dataset:** Marketing Campaign Performance Dataset (Kaggle, Manisha B), 200,000 campaigns
**Period analyzed:** January 1, 2021 to December 31, 2021
**Channels:** Email, Facebook, Google Ads, Instagram, Website, YouTube

## Executive Summary

We analyzed conversion rate, cost per acquisition (CPA), and ROI across six marketing channels using 200,000 campaign records. After applying t-tests, Fisher's exact tests, multiple comparisons correction, and power analysis, we find no statistically or practically meaningful performance difference between channels. We recommend maintaining an even budget split across all six channels rather than reallocating based on this data.

## Key Findings

**No CPA or ROI differences.** T-tests on conversion rate across all 15 channel pairs found zero significant results. All effect sizes were negligible (Cohen's d under 0.01). Bootstrap 95% confidence intervals for CPA overlap heavily across all six channels, ranging narrowly between $12,481 and $12,528.

**Fisher's exact test flagged differences, but they are not real.** 9 of 15 pairwise comparisons on conversion rate came back statistically significant. However, every odds ratio sat between 0.99 and 1.00, meaning the actual rate gap between any two channels is under 0.7 percentage points. This is a textbook case of a large sample size (millions of clicks) turning trivial differences into statistically significant ones.

**Correction results.** Bonferroni correction reduced significant Fisher results from 9 to 7. Benjamini-Hochberg FDR correction kept all 9. Neither correction changes the practical conclusion: these are not meaningful business differences.

**Power analysis confirms the gaps are noise.** We ran empirical power simulations at effect sizes of 5%, 10%, 15%, and 20%, across sample sizes from 30 to 180 days. At the actual observed effect sizes for the "significant" Fisher pairs (0.26% to 0.70%), statistical power at 90 days ranges from 0.04 to 0.07, far below the 80% threshold needed to trust a result. In other words, we do not have enough data resolution to detect differences this small, and the flagged results are consistent with random variation.

## Recommendations

**Budget allocation: even split.** With no channel showing a statistically robust and practically meaningful advantage, allocate the $500K monthly budget evenly across all six channels: approximately $83,333 per channel (16.67% each).

| Channel | Allocation | % of Budget |
|---|---|---|
| Website | $83,333 | 16.67% |
| Facebook | $83,333 | 16.67% |
| YouTube | $83,333 | 16.67% |
| Email | $83,333 | 16.67% |
| Google Ads | $83,333 | 16.67% |
| Instagram | $83,333 | 16.67% |

**Do not reallocate based on the raw Fisher's test results.** Shifting budget toward YouTube or away from Google Ads based on the uncorrected p-values would be a mistake. The underlying effect sizes are too small to act on and the power analysis shows we cannot currently distinguish them from noise.

**If you want to detect real differences, collect more data or test larger interventions.** To reliably detect a 5% CPA difference, you would need roughly 180 days of data at current volume. A 10% difference could be detected in about 60 days. If future campaigns are testing budget shifts, structure them to produce at least a 10% expected effect size to get a readable signal within a quarter.

## Statistical Caveats

- **Dataset limitations.** This is a Kaggle dataset of unknown provenance regarding real business context; campaign assignment to channel may not reflect true randomized allocation. Values across channels are unusually uniform, consistent with synthetically generated or heavily aggregated data.
- **Multiple comparisons.** With 30 total comparisons run across t-tests and Fisher's tests, we expected 1.5 false positives by chance at α=0.05 alone. Both Bonferroni and FDR corrections were applied; results reported above reflect corrected values.
- **Statistical vs. practical significance.** Several Fisher's exact test results were statistically significant purely due to sample size (millions of clicks per channel). Odds ratios near 1.00 indicate no meaningful practical effect despite low p-values.
- **Confidence intervals.** Bootstrap 95% CIs for CPA overlap across all channels, reinforcing that no channel is distinguishable from the others on this metric.
- **Power analysis limitations.** Power estimates are based on simulated CPA data with assumed normal distribution and 15% standard deviation; actual channel-level variance may differ. Results should be treated as directional, not exact.
- **External factors.** This analysis does not account for seasonality, audience overlap, attribution windows, or diminishing returns at higher spend levels, all of which affect real-world channel performance.

## Next Steps

1. Maintain even budget allocation across all six channels for the next cycle.
2. If reallocation is a business priority, run a structured test with a larger expected effect size (10%+) rather than relying on historical variation.
3. Revisit this analysis with a new, verified dataset that reflects actual campaign-level randomization if available.
4. Consider tracking raw conversion counts and revenue (not just rates) in future data collection to support ROAS-style calculations directly.