# W7D5_LAB_In_God_we_trust_everyone_else_bring_the_data
- Week 7 / Day 5
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-24
---

# Executive Memo: Campaign Channel Conversion Analysis

**Dataset:** Digital Marketing Campaign Dataset  
**Source:** [\[Digital Marketing Company\] ](https://www.kaggle.com/datasets/arpit2712/digital-marketing-company/data) 

**Records analyzed:** 8,000 customer-level records across five campaign channels

## Executive Summary

This analysis compared customer-level conversion outcomes across Email, PPC, Referral, SEO, and Social Media channels. Conversion rates ranged from 86.83% for Social Media to 88.31% for Referral. However, none of the 10 pairwise channel comparisons showed a statistically significant difference in conversion odds at the 0.05 level.

The conclusion remained unchanged after applying Bonferroni and Benjamini-Hochberg false discovery rate corrections: no channel pair showed a statistically significant conversion-rate difference. Therefore, the available evidence does not support shifting the marketing budget between channels based only on the observed conversion-rate differences.

## Key Findings

- Referral had the highest observed conversion rate at 88.31%.
- PPC had a conversion rate of 88.28%.
- SEO had a conversion rate of 87.68%.
- Email had a conversion rate of 87.03%.
- Social Media had the lowest observed conversion rate at 86.83%.
- The largest observed difference was 1.47 percentage points between Referral and Social Media.
- Fisher's exact tests were used to compare each of the 10 possible channel pairs because `Conversion` is a binary outcome.
- No pairwise comparison was significant at the uncorrected 0.05 level.
- No comparison was significant after Bonferroni correction or Benjamini-Hochberg FDR correction.

## Data Adequacy

A simulation-based power analysis evaluated the ability to detect true differences in CPA under stated assumptions. With 90 customers per channel, the analysis had approximately 60.8% power to detect a 5% true CPA difference, below the 80% target.

The same simulated sample size had approximately 99.3% power to detect a 10% true CPA difference. This suggests that the analysis is better able to detect moderate or large CPA differences than small differences.

The dataset contains no time variable, so the power analysis uses customers per channel rather than days of data. No channel pair was significant after FDR correction; therefore, there were no significant pairs requiring pair-specific post-hoc power assessment.

## Recommendations

1. Do not reallocate the marketing budget based solely on the small observed conversion-rate differences in this dataset.
2. Maintain a balanced allocation across channels while collecting more decision-relevant data, particularly cost, revenue, and time-period information.
3. Before making major budget shifts, run controlled experiments or track channel performance over repeated time periods.
4. Define a minimum practically meaningful difference before testing. For example, determine whether a 5% or 10% CPA improvement would justify the operational cost of moving budget.
5. Track CPA, ROAS, revenue, customer lifetime value, and profit by channel. Conversion rate alone does not indicate which channel creates the greatest business value.

## Statistical Caveats

- A non-significant result does not prove that all channels perform identically; it means the analysis did not find sufficient evidence of a difference.
- The analysis used customer-level records and treated each record as one conversion opportunity because `WebsiteVisits` could not be used as the total-attempt denominator: 119 records had `Conversion` greater than `WebsiteVisits`.
- Ten channel-pair comparisons increase the risk of false positives, so both Bonferroni and Benjamini-Hochberg FDR corrections were applied.
- The dataset does not include a time variable, preventing analysis of daily or seasonal variation.
- The dataset also does not provide a complete basis for true channel-level CPA, ROAS, revenue, profit, or customer lifetime value evaluation.
- Observational channel data can be affected by audience differences, targeting, campaign goals, and attribution rules. The results show association, not proof that channel choice caused the conversion outcome.
- The power analysis is simulation-based and depends on assumptions of a 15% CPA standard deviation and a minimum CPA floor of 50% of the baseline CPA.

## Next Steps

1. Collect daily or weekly performance data by channel, including spend, clicks, conversions, revenue, and profit.
2. Establish a pre-registered testing plan with a practical-effect threshold and target sample size.
3. Use controlled A/B or geo experiments where possible to estimate causal channel effects.
4. Reassess budget allocation after collecting enough data to detect the smallest difference that would matter commercially.