# Executive memo: provisional channel budget recommendation

## Finding

Across 1,800 campaign-day observations, TikTok Ads had the highest aggregate ROAS (9.54x) and TikTok Ads had the lowest aggregate CPA ($29.20). Pairwise ROAS Welch tests remained significant after both Bonferroni and Benjamini–Hochberg correction: True. The ROAS effects range from medium to large, so the differences are practically meaningful in this dataset.

Aggregate conversion rates were close (4.46% Google, 4.59% Meta, and 4.71% TikTok). The pooled-click Fisher tests are statistically significant, while the row-level conversion-rate t-tests have 0 BH-significant pair(s). This contrast suggests that statistical significance is being driven partly by very large click counts; conversion-rate differences should not be treated as large commercial effects without a controlled experiment.

## Provisional $500,000 plan

The supplied data has three platforms rather than seven channels, so the following is an illustrative starting point only:

- TikTok Ads: 45% ($225,000)
- Meta Ads: 30% ($150,000)
- Google Ads: 15% ($75,000)
- Validation reserve: 10% ($50,000)

The reserve should fund randomized holdouts, creative tests, and measurement. Before reallocating the full budget, obtain comparable data for the four missing channels and validate whether the observed ROAS ranking persists after controlling for campaign type, industry, country, seasonality, and spend level.

## Caveats and next steps

These are observational campaign-day comparisons, not causal estimates. Rows may share campaigns, audiences, or dates, and aggregate Fisher tests treat clicks as independent. ROAS and CPA can also be skewed by attribution and outliers. Use the current results to prioritize tests, not to promise incremental returns. The power analysis indicates adequate row counts for medium effects, but small effects need larger or better-designed experiments.