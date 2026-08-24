# Executive Memo: Marketing Channel Budget Recommendation

**Date:** 2026-08-25  
**Analyst:** Parisa Dehghani  
**Dataset:** Solstice SaaS Growth Pack - channel_performance  
**Source:** https://huggingface.co/datasets/solsticestudioai/saas-growth-pack  
**Period analyzed:** 2026-01-01 to 2026-03-31

## Executive Summary

I analyzed seven marketing channels using daily impressions, clicks, conversions, cost, and attributed revenue. Pairwise CPA differences were tested with Welch independent t-tests and Cohen's d, conversion-rate differences were tested with Fisher's exact test, and both Bonferroni and Benjamini-Hochberg FDR corrections were applied to limit false discoveries. The recommended $500,000 monthly allocation gives the largest share to **Referral ($125,000, 25.0%)**, followed by **SEO ($106,061, 21.2%)**. The best aggregate CPA was **Referral (77.85)**, while the best aggregate ROAS was **Referral (6.61x)**. These recommendations should be treated as an evidence-based prioritization exercise rather than a production budget decision because the Hugging Face dataset is synthetic benchmark data.

## Key Findings

- FDR-significant CPA comparisons: **16**
- FDR-significant conversion-rate comparisons: **15**
- At 90 days, **3 of 4** simulated CPA effect sizes (5%, 10%, 15%, 20%) reached the 80% power target.
- **CPA:** Paid Search vs Referral remained significant after FDR correction (adjusted p=6.197e-38, Cohen's d=-3.38, large effect).
- **CPA:** LinkedIn Ads vs Referral remained significant after FDR correction (adjusted p=4.037e-37, Cohen's d=-4.79, large effect).
- **CPA:** Outbound Sales vs Referral remained significant after FDR correction (adjusted p=5.517e-35, Cohen's d=-3.94, large effect).
- **Conversion rate:** Outbound Sales vs Referral remained significant after FDR correction (adjusted p=4.355e-44, odds ratio=0.27).
- **Conversion rate:** Partnerships vs Referral remained significant after FDR correction (adjusted p=9.966e-32, odds ratio=0.32).
- **Conversion rate:** LinkedIn Ads vs Referral remained significant after FDR correction (adjusted p=1.13e-31, odds ratio=0.31).

## Recommended $500K Monthly Budget

The allocation uses a simple composite score: 40% CPA rank, 40% ROAS rank, and 20% conversion-rate rank, with each channel constrained to a reasonable 5%-25% range.

| channel | recommended_budget | budget_pct |
|---|---|---|
| Referral | $125,000 | 25.0% |
| SEO | $106,061 | 21.2% |
| Partnerships | $67,172 | 13.4% |
| Content | $63,636 | 12.7% |
| Paid Search | $60,101 | 12.0% |
| Outbound Sales | $53,030 | 10.6% |
| LinkedIn Ads | $25,000 | 5.0% |

## 95% Bootstrap Confidence Intervals for Daily CPA

| channel | mean_daily_cpa | ci_95_lower | ci_95_upper |
|---|---|---|---|
| Referral | 83.925 | 75.255 | 94.665 |
| Content | 791.986 | 723.720 | 855.149 |
| SEO | 795.848 | 726.951 | 874.342 |
| Partnerships | 876.054 | 815.894 | 945.105 |
| Paid Search | 1110.171 | 1018.505 | 1195.880 |
| Outbound Sales | 1171.195 | 1084.342 | 1252.431 |
| LinkedIn Ads | 1293.299 | 1208.569 | 1377.444 |

## Statistical Caveats

- The selected Hugging Face dataset is **100% synthetic**, so the results demonstrate the statistical workflow but should not be used as real e-commerce evidence.
- The analysis pools six synthetic companies and aggregates them into daily channel totals; a real company may have different audiences, attribution rules, prices, and channel mix.
- Daily observations may have time dependence, while the pairwise t-tests treat observations as independent.
- Multiple comparisons were corrected with both Bonferroni and Benjamini-Hochberg; business decisions use the FDR-adjusted results.
- Statistical significance does not automatically imply practical significance, so Cohen's d and the size of CPA/rate differences should be considered together.
- CPA confidence intervals use nonparametric bootstrap resampling and summarize uncertainty in the observed 90-day period.
- The power analysis assumes approximately normal CPA with a standard deviation equal to 15% of baseline CPA; real campaign variance may differ.

## Recommendations

1. Use the allocation table as a **starting hypothesis**, not an automatic budget transfer.
2. Prioritize the top-ranked channels for controlled incremental-budget tests, while retaining minimum spend in every channel.
3. Do not shift budget based only on uncorrected p-values; use the FDR-adjusted findings and effect sizes.
4. For effect sizes that did not reach 80% power at 90 days, collect the additional sample size indicated in `sample_size_recommendations.csv`.
5. Re-run this exact workflow on the company's real e-commerce channel data before implementing the full $500K allocation.

## Next Steps

Run a controlled 30-90 day budget experiment on the highest-priority channels, track the same conversion definition and attribution window across all channels, and update the analysis when new observations arrive.
