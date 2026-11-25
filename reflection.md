# Reflection

## 1. What surprised me about the results?

How little difference there was between channels. I expected at least one clear winner, but CPA varied by only ~1.1% and nothing was significant, not even before correction. The bigger surprise was that the same conversion-rate data gave opposite answers depending on the test: Fisher's exact test found 9 of 15 pairs significant, while a t-test on daily rates found none. The gap was entirely about sample size. With ~18 million clicks per channel, a difference of 0.05 percentage points becomes "significant", even though it means one extra conversion per ~1,800 clicks.

## 2. How did multiple-comparison correction change my conclusions?

Less than I expected, but for an instructive reason. The t-tests had nothing to correct. For Fisher, Bonferroni removed 2 of 9 pairs (Email vs Google Ads, Google Ads vs Instagram) and Benjamini-Hochberg kept all 9. The real lesson was that correction protects against false positives, but not against true results that are too small to matter. Effect size and practical significance did more work in the final recommendation than the correction did.

## 3. What are the limits of this analysis?

- The dataset is synthetic, so the near-identical channels may be an artefact of how it was generated.
- Conversions and revenue were derived from rates and ROI, not observed directly.
- Daily observations are treated as independent; seasonality and day-of-week effects aren't modelled.
- Attribution overlap between channels and diminishing returns at higher spend are ignored.
- The power simulation assumes normally distributed CPA with 15% spread; the real spread was 8–9%.
- Channel is the only dimension analysed. Campaign type, audience or location may hide larger differences.

## 4. How would I explain this to a non-technical CMO in one minute?

"We checked a full year of data to see whether any channel gets us customers more cheaply. They all cost about the same, around $284 per conversion, and the small differences we see are the kind you'd get by chance. We had enough data to spot any channel that was 5% cheaper or more, and there isn't one. So I'd keep the budget evenly split for now. If you want to go further, let's run a proper test: move 10% of budget between two channels for a month and measure what actually happens. Ranking channels on these numbers would move about $83,000 a month between channels based on noise."
