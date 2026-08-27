# Executive memo: Shopping Mall Paid Search

**To:** Marketing leadership; **Subject:** Where to maintain, optimise and reduce paid-search spend

## Recommendation

Do not scale the campaign on the strength of the historical conversion numbers alone. Maintain One-to-one, optimise Exact and reduce Phrase while the team fixes measurement and tests changes prospectively.

If a $500,000 planning envelope is required, allocate $200,000 to One-to-one, $200,000 to Exact and $100,000 to Phrase. Release it in stages. All three groups had negative historical ROI, so the allocation is a controlled learning plan, not a forecast of profitable return.

## What the data says

The dataset contains 190 monthly ad-group records from July to November 2021. The campaign generated 2.67 million impressions, 924,503 clicks and 95,996 conversions. Recalculated CTR was 34.56%, conversion rate 10.38%, CPC $0.69 and CPA $6.62.

Reported revenue was $561,960 against $635,372 of media cost. That leaves a $73,412 loss, ROAS of 0.884 and ROI of −11.55%. The published conversion-rate field did not match conversions divided by clicks in 160 rows, so every KPI in the analysis was recalculated from the underlying counts.

One-to-one was the strongest relative group. It delivered 72,388 conversions at a $6.39 CPA, with ROAS of 0.895 and ROI of −10.5%. Exact was close on ROAS but had a $7.00 CPA and −11.4% ROI. Phrase was weakest at a $7.86 CPA, 0.812 ROAS and −18.8% ROI.

The conversion-rate test found a statistically detectable difference across the three groups: One-to-one was 0.41 percentage points above Exact and 0.57 points above Phrase. A p-value below 0.001 means a gap this consistent would be unusual if the rates were truly identical. It does not mean the gap is large. The effect-size measure, Cramér's V, was only 0.0069, which confirms that the overall relationship is very small.

The profitability evidence is more relevant to the budget decision. A bootstrap—repeatedly resampling whole ad groups to measure uncertainty—kept the 95% ROI interval below zero for every match type. In practical terms, none of the groups has convincing evidence of positive historical profitability. One-to-one looks better than Phrase, but the data does not support calling it a profitable winner.

## Budget and guardrails

The allocation rule combines CPA, ROAS and the amount of conversion evidence. A 40% cap prevents the high-volume One-to-one group from absorbing most of the budget, while a 20% floor preserves a controlled learning budget for Phrase.

At unchanged historical CPC, conversion rate and revenue per conversion, the $500,000 scenario estimates approximately $437,000 in revenue and a $63,000 loss. A downside case—CPC up 10%, conversion rate down 10% and revenue per conversion down 10%—widens the modeled loss to about $178,000. The upside case turns positive only when all three drivers improve together. These are sensitivities, not guaranteed forecasts, and they do not account for auction saturation.

Release each tranche only if marginal ROAS and ROI improve. Monitor CPA, revenue per conversion, conversion quality and volume alongside ROAS. Before treating any group as break-even, reconcile the definition of revenue and add product margin; this dataset cannot provide a true business break-even CPA.

## Next 90 days

During the first 30 days, audit conversion tracking, search terms, mobile landing pages, attribution and revenue mapping. Reduce weak Phrase exposure and keep One-to-one within the 40% cap.

By day 60, run a properly randomized creative or landing-page test with one primary outcome and a pre-calculated sample size. Separate device reporting and add negative keywords based on the search-term review.

By day 90, reallocate only where the test shows an incremental improvement large enough to matter commercially. Add margin, new-customer status, attribution lag and auction-level data to the reporting model.

This analysis is observational. It identifies where to look and what to test; it does not prove that changing match type will cause the historical differences to repeat.
