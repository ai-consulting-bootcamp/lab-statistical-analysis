# Executive memo: marketing channel budget allocation

| | |
|---|---|
| **To** | Chief Marketing Officer |
| **From** | Elif Yurdakul, Marketing Analytics |
| **Date** | 27 November 2026 |
| **Dataset** | Marketing Campaign Performance Dataset, Kaggle (manishabhatt22): 200,000 campaigns across 6 channels |
| **Period analysed** | 1 January – 31 December 2021 (365 days per channel) |
| **Decision** | How to allocate the $500K monthly budget |

## Executive summary

**The data does not support moving budget between channels.** Over a full year, Email, Facebook, Google Ads, Instagram, Website and YouTube delivered almost identical cost per acquisition ($282–$285, a 1.2% spread), ROAS (5.99–6.03) and conversion rate (7.98–8.03%).

None of the CPA or ROAS differences is statistically reliable. Some conversion-rate differences are, but they are 0.06 percentage points at most, too small to affect the budget.

With 365 days of data, a real CPA gap of 5% or more would have been detected almost certainly. We would most likely have seen any gap above about 2%.

**Recommendation:** keep the budget close to an even split, tilting at most ±10% toward the composite leaders, Website and Facebook. Run that tilt as a controlled 90-day test rather than treating it as a proven win.

## Key findings

**1. Top performers on paper, but within noise**

| Channel | CPA | ROAS | Conversion rate | Daily CPA, 95% CI |
|---|---|---|---|---|
| Website | **$281.93** | 6.011 | 8.024% | $280.96 – $286.09 |
| Email | $283.34 | 5.999 | **8.032%** | $282.51 – $287.64 |
| Facebook | $283.89 | **6.027** | 8.018% | $283.24 – $287.98 |
| YouTube | $284.75 | 6.001 | 7.976% | $283.90 – $289.20 |
| Instagram | $285.13 | 5.986 | 7.987% | $284.37 – $289.58 |
| Google Ads | $285.22 | 6.008 | 8.008% | $284.26 – $289.29 |

CPA, ROAS and conversion rate are year totals. The confidence intervals are for the mean *daily* CPA, from 1,000 bootstrap resamples. All six intervals overlap: a value between $284.4 and $286.1 falls inside every one of them.

**2. Statistically significant differences (after correcting for 30 tests)**
- **CPA:** none. 15 pairwise t-tests; the smallest raw p-value is 0.075, and 0.57 after FDR correction. All effect sizes are negligible (Cohen's d < 0.14).
- **ROAS:** two pairs looked significant before correction (Facebook vs Instagram, p = 0.006; Facebook vs Email, p = 0.049). Neither survives correction. With 15 tests, about one false positive is expected by chance.
- **Conversion rate (Fisher's exact test, about 18M clicks per channel):** 9 of 15 pairs survive FDR correction and 7 survive Bonferroni. Email, Website and Facebook convert slightly better than YouTube and Instagram. The largest gap, Email 8.03% vs YouTube 7.98%, is 0.056 percentage points, about 0.7% in relative terms. Even if the entire $500K moved from YouTube to Email, that would add about 12 conversions a month (0.7% of roughly 1,750). These differences are statistically real because the samples are huge, but they have no practical significance.

**3. Data adequacy (power analysis)**
- Day-to-day CPA varies by about 8.6% around each channel's mean.
- **With 365 days per channel** we had 80% power to detect a CPA difference of about 1.8%, and near-certain power (≥ 99%) for 5%. A null result here is informative: it isn't caused by too little data.
- **With the 90 days a typical review uses**, the detectable difference is about 3.6% at the observed variability. Under the more conservative 15% variability assumption it's about 6.3%, and confirming a 5% gap would take about 144 days.
- The CPA gaps we actually observed (1.0–1.2%) would need about 850–1,200 days per channel to confirm, which isn't practical.

## Recommendations

**Budget allocation: tilt, don't shift.**

| Channel | Composite score | Monthly budget | Share | vs even split |
|---|---|---|---|---|
| Website | 5.4 | $91,700 | 18.3% | +$8,400 |
| Facebook | 4.8 | $89,000 | 17.8% | +$5,700 |
| Email | 4.0 | $85,500 | 17.1% | +$2,200 |
| YouTube | 2.6 | $79,400 | 15.9% | −$3,900 |
| Google Ads | 2.6 | $79,400 | 15.9% | −$3,900 |
| Instagram | 1.6 | $75,000 | 15.0% | −$8,300 |
| **Total** | | **$500,000** | 100% | |

*How the scores are built:* each channel is ranked 1–6 on CPA (lower is better), ROAS and conversion rate. The ranks are weighted 40% CPA, 40% ROAS and 20% conversion rate.

*How the money follows the scores:* each channel moves away from the even split ($83.3K) in proportion to its score's distance from the average, capped at ±10%.

*Why not the naive version:* allocating purely in proportion to the score would give Website $128.6K and Instagram $38.1K. That's a 3:1 move based on differences the tests can't distinguish from noise.

**Strategic actions**
1. **Treat the tilt as an experiment.** Pre-register CPA as the single success metric and review after 90 days. Keep the tilt only if the favoured channels show a CPA advantage of at least 5%.
2. **Don't cut any channel outright.** No channel is reliably worse. Cutting one would lose reach and diversification without a proven saving.
3. **Look for bigger levers than channel.** Segment the same data by campaign type, audience and region. If channels perform alike, the budget lever may lie elsewhere.
4. **Fix the data before the next decision.** Use the company's own spend and revenue data, with consistent attribution, before acting on any channel ranking.

## Statistical caveats

- **Dataset limitations.** This is a public Kaggle dataset, not our company's data, and it shows signs of being synthetic: values are evenly spread across fixed ranges and channels are nearly identical. Real channel data usually differs much more. The method carries over to our data; the conclusions may not.
- **Derived metrics.** Conversions = clicks × conversion rate. Revenue = cost × (1 + ROI). `Acquisition_Cost` is treated as campaign spend. If the dataset author meant something else, CPA and ROAS would change.
- **Multiple comparisons.** 30 primary tests were run, so about 1.5 false positives were expected by chance. Results are reported with Bonferroni and with Benjamini–Hochberg (FDR) correction. Bonferroni is the right bar for moving real money.
- **Confidence intervals.** Point estimates hide uncertainty. Every channel's CPA interval overlaps the others, so the rankings in the tables could reshuffle with new data.
- **Statistical vs practical significance.** The conversion-rate differences are "significant" only because each channel has about 18M clicks. Their size (≤ 0.06 pp) matters more than their p-values.
- **External factors.** Seasonality, creative quality, audience overlap and attribution rules are not modelled. Each day's channels share the same market conditions, which reduces but doesn't remove this risk.
- **Power analysis limits.** The simulations assume normally distributed daily CPA and independent days. Real data with weekly cycles or autocorrelation would need more days than shown here.

## Next steps

| # | Action | Owner | When |
|---|---|---|---|
| 1 | Approve the tilted allocation for next month | CMO | Next budget cycle |
| 2 | Set up the 90-day CPA test: pre-registered metric, ≥ 5% threshold | Marketing Analytics | Before launch |
| 3 | Rerun this analysis on the company's own channel data | Marketing Analytics | Within 4 weeks |
| 4 | Segment performance by campaign type, audience and region | Marketing Analytics | Within 6 weeks |
| 5 | Review test results and decide whether to keep, extend or reverse the tilt | CMO + Analytics | Day 90 |

*Supporting analysis: `data_exploration.ipynb`, `statistical_analysis.ipynb`, `power_analysis.ipynb`, `business_recommendations.ipynb`.*
