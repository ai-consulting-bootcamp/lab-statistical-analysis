# Executive memo — Marketing budget allocation

**To:** CMO · **From:** Pieter Albrecht · **Date:** 24 November 2026
**Dataset:** Marketing Campaign Performance Dataset (Kaggle, manishabhatt22) · **Period:** 01 Jan 2021 – 31 Dec 2021 (365 days, 6 channels)

## Executive summary
I tested whether any of our six marketing channels is reliably cheaper or more effective than the others. **None is.** CPA differs by at most ~1.1% between channels, and no difference is statistically significant, even before correcting for multiple tests. I recommend **keeping an even split of the $500K monthly budget** (~$83K per channel) and running a controlled test before moving money.

## Key findings
- **Top performers on paper:** Website has the lowest CPA ($281.93) and Facebook the highest ROAS (6.027), but the gaps to the weakest channels are ~1.1% (CPA) and ~0.7% (ROAS).
- **CPA:** 0 of 15 channel pairs differ significantly (Welch t-test on daily CPA; smallest BH-adjusted p = 0.57). All Cohen's d values are negligible (|d| < 0.2).
- **Conversion rate:** 9 of 15 pairs differ significantly after Benjamini-Hochberg correction (7 after Bonferroni); YouTube and Instagram convert slightly less. The largest gap is only 0.056 percentage points: detectable only because each channel has ~18M clicks, and not significant in daily data (0 of 15 t-tests).
- **Data adequacy (power):** with 365 days per channel we have ≥80% power to detect any CPA gap of 5% or more (5% needs ~145 days). So **no channel differs from another by 5% or more**. The ~1% gaps we observe would need ~2,630 days (~7 years) to confirm.

## Recommendations
| Channel | CPA | ROAS | Rank-based split | Recommended split |
|---|---|---|---|---|
| Website | $281.93 | 6.011 | $131,000 (26.2%) | $83,300 (16.7%) |
| Facebook | $283.89 | 6.027 | $119,000 (23.8%) | $83,300 (16.7%) |
| Email | $283.34 | 5.999 | $83,300 (16.7%) | $83,300 (16.7%) |
| YouTube | $284.75 | 6.001 | $71,400 (14.3%) | $83,300 (16.7%) |
| Google Ads | $285.22 | 6.008 | $59,500 (11.9%) | $83,300 (16.7%) |
| Instagram | $285.13 | 5.986 | $35,700 (7.1%) | $83,300 (16.7%) |

- **Use the recommended (even) split.** The rank-based split would give Website 3.7× the budget of Instagram based on differences that are statistically indistinguishable from noise.
- **Run a controlled test** before reallocating: e.g. shift 10% of budget between two channels for a fixed period and measure the CPA change.
- **Look for gains within channels**, not between them: campaign type, audience and location may show larger, actionable differences.

## Statistical caveats
- **Dataset source and limits:** public Kaggle dataset that appears synthetic. Conversions were derived (conversion rate × clicks) and revenue from ROI. Absolute spend (~$417M per channel per year) doesn't match our $500K/month scale, so only relative differences are used.
- **Multiple comparisons:** 45 pairwise tests in three families, corrected with Bonferroni and Benjamini-Hochberg per family. ~2.25 false positives would be expected by chance without correction.
- **Confidence intervals:** 95% bootstrap CIs for mean daily CPA all overlap (each about ±$2.50):

| Channel | Mean daily CPA | 95% CI |
|---|---|---|
| Website | $283.62 | $281.05 – $286.04 |
| Email | $285.07 | $282.74 – $287.59 |
| Facebook | $285.57 | $283.07 – $287.85 |
| YouTube | $286.44 | $283.88 – $289.09 |
| Google Ads | $286.80 | $284.34 – $289.27 |
| Instagram | $286.93 | $284.45 – $289.48 |

- **External factors:** seasonality, attribution overlap between channels, creative changes and diminishing returns at higher spend are not modelled.
- **Statistical vs practical significance:** the conversion-rate gaps are statistically significant but tiny (≤0.056 pp); with ~18M clicks almost any gap becomes significant. None is large enough to justify moving budget.
- **Power limitations:** the power simulation assumes normally distributed daily CPA with 15% spread; our actual spread is 8–9%, so true power is somewhat higher. Conclusions are unchanged.

## Next steps
- Keep the even split for the next month.
- Design and run a 4–6 week budget-shift test between the top and bottom channels.
- Re-run this analysis on our own (non-synthetic) channel data, broken down by campaign type and audience.
