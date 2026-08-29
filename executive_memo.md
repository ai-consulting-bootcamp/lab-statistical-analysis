# Executive Memo: Shopping Mall Paid Search

| Field | Detail |
|---|---|
| Date | 27 August 2026 |
| Analyst | Gretel Ceballos |
| Dataset | Shopping Mall Paid Search Campaign Dataset, Marcello D. (`marceaxl82`) |
| Period | July–November 2021 |

**To:** Marketing Leadership  
**Subject:** Paid search performance and $500K budget recommendation

## Executive Summary

The campaign is generating significant traffic and conversion volume, but the current economics do not support scaling spend without further optimisation.

Across the five-month period, the campaign generated 95,996 conversions from $635,372 in media spend. Reported revenue was $561,960, resulting in a ROAS of 0.884 and ROI of -11.55%.

One-to-one is the strongest match type on both scale and acquisition efficiency. Exact performs relatively close and is worth optimising. Phrase has the weakest economics and should receive less budget until traffic quality and conversion performance improve.

For a $500,000 planning envelope, I would allocate:

| Match type | Budget | Recommendation |
|---|---:|---|
| One-to-one | $200,000 | Maintain |
| Exact | $200,000 | Optimise and test |
| Phrase | $100,000 | Reduce and review |

I would release this budget progressively rather than commit the full amount upfront. None of the three groups currently demonstrates positive historical ROI.

## Campaign Performance

The campaign generated:

- 2.67M impressions
- 924,503 clicks
- 95,996 conversions
- 34.56% CTR
- 10.38% conversion rate
- $0.69 CPC
- $6.62 CPA

Before analysing performance, I recalculated the main KPIs from the underlying impressions, clicks, conversions, cost and revenue. The conversion-rate field provided in the dataset did not match `Conversions / Clicks` in 160 of 190 records, so the published ratios were not used as analytical inputs.

### Performance by Match Type

| Match type | Conversions | CPA | ROAS | ROI | Recommendation |
|---|---:|---:|---:|---:|---|
| One-to-one | 72,388 | $6.39 | 0.895 | -10.5% | Maintain |
| Exact | 15,038 | $7.00 | 0.886 | -11.4% | Optimise/Test |
| Phrase | 8,570 | $7.86 | 0.812 | -18.8% | Reduce/Pause |

### One-to-one: protect the strongest base

One-to-one generated most of the campaign's conversions while maintaining the lowest CPA and strongest relative ROAS.

The statistical comparison supports the observed CPA advantage. Across monthly ad-group observations, its mean CPA was $1.32 lower than Exact and $2.21 lower than Phrase after FDR correction.

However, its ROI was still negative. I would therefore protect its role in the media mix rather than aggressively scale it.

### Exact: optimise before deciding whether to scale

Exact has a higher CPA than One-to-one, but its ROAS is relatively close.

The CPA difference against One-to-one is statistically detectable, although the effect size is small. This makes Exact a better optimisation candidate than a straightforward budget-cut candidate.

I would investigate search terms, creative, landing-page performance and device differences, then test whether its acquisition economics can be improved before changing its share materially.

### Phrase: reduce exposure while investigating traffic quality

Phrase has the highest CPA and lowest ROAS of the three groups. It also has the most negative historical ROI.

The evidence supports reducing its exposure, but not assuming that match type itself caused the result. Search terms, intent, bids, landing pages and other campaign differences are not available in the dataset.

I would retain a smaller controlled budget while investigating those factors rather than eliminate the group solely from this historical analysis.

## What the Statistical Analysis Changed

The statistical analysis was used to test whether the differences visible in the marketing KPIs were strong enough to support the budget decision.

The CPA analysis confirms that One-to-one has a meaningful advantage over Phrase and a smaller advantage over Exact. Exact and Phrase are not statistically distinguishable on CPA after correction.

Conversion rates also differ statistically, but the effect is very small. With more than 924,000 clicks, small differences can be detected even when their commercial importance is limited. For that reason, conversion-rate significance alone is not enough to justify moving budget.

Bootstrap confidence intervals also keep historical ROI below zero across all three match types. This is why the recommendation prioritises controlled optimisation rather than scaling the apparent winner.

Multiple-comparison corrections were applied to reduce the risk of treating chance differences as meaningful. The CPA power analysis also indicates that a 90-day test is sufficient for differences similar to the larger CPA gaps observed here, but would have only 61.2% power to detect a smaller 5% difference.

## $500K Budget Recommendation

I would start with:

- $200K One-to-one
- $200K Exact
- $100K Phrase

This is a planning allocation, not a prediction that $500K will generate a positive return.

If historical performance remained unchanged, the model estimates approximately $437K in reported revenue from the $500K spend, a loss of approximately $63K.

For that reason, I would release budget in stages and monitor CPA, revenue per conversion, ROAS, ROI and conversion quality before increasing spend.

One-to-one provides the strongest current base. Exact retains enough budget to optimise and test. Phrase is limited while the team investigates why its acquisition economics are weaker.

## Next 90 Days

**Days 1-30**

Audit conversion tracking, search terms, attribution, mobile landing pages and revenue mapping. Reduce weak Phrase exposure and identify optimisation opportunities in Exact.

**Days 31-60**

Run a randomized test on one variable at a time, such as creative or landing page. Define the primary KPI and required sample size before launching the test.

**Days 61-90**

Reallocate incremental budget only where the test demonstrates an improvement that is both statistically supported and commercially meaningful.

Add product margin, new-customer status and better attribution data before setting a true break-even CPA or profitability target.

## Limitations

This is an observational analysis, not a randomized experiment, so the results identify performance patterns rather than causal effects.

The dataset covers five months and does not include product margin, LTV, search-term detail, bids, attribution rules or incremental revenue. Historical performance may also change as spend scales.

ROAS below 1 shows that reported revenue did not cover media spend during the observed period, but a true business break-even CPA cannot be calculated without contribution-margin data.