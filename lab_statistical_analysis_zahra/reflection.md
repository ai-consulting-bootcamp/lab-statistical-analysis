# Reflection

## What surprised me about the results?

How huge the sample sizes were once I looked at raw clicks and conversions (millions per channel). Because of that, Fisher's exact test found every conversion rate comparison "significant," even though the actual gap was under 1 percentage point. A clean real example of statistical significance without much practical significance.

I also caught an inconsistency in my own work: one notebook computed CPA as total cost divided by total conversions, another used the average of daily CPA values, and these gave different numbers for the same channel ($48.43 vs $57.54 for Google Ads). A good reminder that how you aggregate can quietly change the story.

## How did multiple comparisons correction change my conclusions?

It did not change anything, all 6 comparisons stayed significant after Bonferroni and FDR. That is still a meaningful result though: with only 3 channels, the expected false positives by chance were already low (about 0.3), so there was little for correction to catch. It gave me more confidence the differences are real, not lucky p-values.

## What are the limitations of this analysis?

- The dataset is a real, public Kaggle dataset, but its values are synthetically generated, not the company's real data.
- Only 3 channels, a small comparison.
- No seasonality, competitor behavior, or diminishing returns from spending more on a channel.
- Power analysis relies on simulation assumptions (normal distribution, fixed std).
- Meta Ads has the smallest sample (258 days vs 307 to 308 for the others).

## How would I communicate these findings to non-technical stakeholders?

Lead with the money, not the statistics: "more than half the ad budget goes to the channel with the worst return, here is why I recommend flipping that." Show the allocation table and the CPA/ROAS chart. Keep terms like Cohen's d and FDR correction in an appendix, and just say "this held up even after checking for false positives" instead. Be upfront that this is based on simulated data and 90 days, so it is a strong first signal, not a final answer, real budget changes should be gradual and re-checked.
