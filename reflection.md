# Reflection

## What surprised me

The answer turned out to be "no difference". I expected at least one channel to stand out on CPA, as the dashboards and ranking tables suggested. Website "wins" CPA, Facebook "wins" ROAS and Email "wins" conversion rate. A different winner on each metric turned out to be a clue that all three leads were noise.

The second surprise was Fisher's exact test. With about 18 million clicks per channel, it flagged 9 of 15 conversion-rate pairs as significant for gaps of a few hundredths of a percentage point. The daily t-test on the same metric found nothing. Both are correct; they answer different questions. Fisher asks whether the pooled rates differ at all. The t-test asks whether the gap shows up reliably day to day. For a budget decision the second question is the one that matters.

## How multiple-comparisons correction changed my conclusions

On CPA it changed nothing, because nothing was significant to begin with. It mattered elsewhere:
- **ROAS:** two "significant" pairs (Facebook over Instagram and over Email) disappeared under both corrections. Without correction I might have recommended Facebook on the strength of a p = 0.049 result.
- **Conversion rate:** Bonferroni removed the two borderline pairs. FDR kept all nine, because most of the p-values were tiny.

The main lesson is that correction only answers "is this likely real?". It doesn't answer "is this big enough to matter?". For that I needed effect sizes, confidence intervals and power together.

## Limitations

- The dataset appears synthetic: values are evenly spread within fixed ranges and the channels are nearly identical. Real channel data would almost certainly show bigger differences, and more skewed distributions.
- Revenue and conversions are derived (revenue = cost × (1 + ROI); conversions = clicks × conversion rate), and `Acquisition_Cost` is assumed to be campaign spend.
- Aggregating to channel × day treats days as independent. Seasonality and autocorrelation aren't modelled, so the power analysis is somewhat optimistic.
- The scenario mentions 7 channels; the dataset has 6.
- The composite score uses ranks, which turn a $0.10 difference and a $3 difference into the same one-rank step. That's another reason to cap the allocation tilt.

## Communicating to non-technical stakeholders

I'd lead with the decision rather than the statistics: "the data says the channels perform the same, so don't move the budget; here's a cheap test to find out if one is actually better". Then three supporting points:
- **Spread vs noise:** the gap between best and worst is about $3 per acquisition; normal day-to-day swings are about $24.
- **Confidence:** with a full year of data, any real gap of 5% or more would almost certainly have shown up.
- **Small but "significant":** the conversion-rate differences are real but worth about a dozen conversions a month.

I'd show the confidence-interval chart, where the overlapping bars make the point at a glance, rather than the p-value heatmap. Words like "significant" need care: to an executive it means "important", and that's exactly the misunderstanding this analysis is trying to prevent.
