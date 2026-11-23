# Executive memo — Marketing budget allocation

**To:** CMO · **From:** Barsha Mishra, Marketing Analyst · **Date:** 23 November 2026
**Dataset:** Kaggle "Marketing Campaign Performance Dataset" (manishabhatt22), 200,000 campaigns aggregated to 6 channels × 365 days
**Period:** 1 January – 31 December 2021

## Executive summary
We tested whether any of our 6 channels (Email, Facebook, Google Ads, Instagram, Website, YouTube) is genuinely cheaper or more effective, before moving any of the $500K monthly budget. **No channel has a statistically significant CPA advantage.** All channels cost about $282–$285 per acquisition and return about 6× ad spend. The data was large enough to detect any real CPA difference of 5% or more, so we can say with confidence that **no channel is meaningfully better on cost**. We recommend **keeping the budget roughly equal** and running a controlled experiment before any major shift.

## Key findings
- **Top performers (point estimates only):** Website has the lowest CPA ($281.93) and Facebook the highest ROAS (6.03). The gap between best and worst CPA is only about **1%**.
- **Statistically significant differences (after correction):**
  - **CPA:** 0 of 15 channel pairs differ (Welch t-test on daily CPA; BH and Bonferroni corrected). Every effect size is negligible (|Cohen's d| ≤ 0.13).
  - **Conversion rate:** 9 of 15 pairs differ with Fisher's exact test (7 with Bonferroni), because each channel has about 18 million clicks. But all rates are **7.98–8.03%**, so the biggest gap is **0.056 percentage points**: real, but **too small to matter**. The t-test on daily conversion rates finds 0 differences.
- **Data adequacy (power):** with 365 days per channel we have about **99% power to detect a 5% CPA difference** (150 days would suffice). The gaps we observed (1.0–1.2%) would need about **850–2,600 days** (2.5–7 years) to prove, and are too small to justify that effort.

## Recommendations
1. **Do not reallocate budget based on these results.** A formula that ranks channels by CPA and ROAS would give Website $131K and Instagram $36K, a **3.7× difference built on noise**. Keep about **$83K per channel** (equal split) for now.
2. **If a small tilt is wanted**, move at most **5–10%** of budget towards Website and Facebook as a **test**, not a decision, and measure the result.
3. **Run a controlled experiment** (e.g. a geo or holdout test) to measure **incremental** conversions per channel. That answers what the historical data cannot: which channel causes extra sales.
4. **Shift the focus from channel choice to other levers** (creative, targeting, landing pages, customer segments), where differences are more likely to be large.

## Statistical caveats
- **Dataset source and limits:** a public Kaggle dataset, very likely **synthetic**. Conversions (rate × clicks) and revenue (cost × (1 + ROI)) were **derived**, not observed. Results show the method, not our real market.
- **Multiple comparisons correction:** 45 tests were run (about 2.25 false positives expected by chance). We used **Benjamini-Hochberg** and, for budget decisions, the stricter **Bonferroni** correction.
- **Confidence intervals:** the 95% bootstrap CIs for daily CPA all overlap (about $281–$290), e.g. Website $281.15–$286.11.
- **External factors:** seasonality, promotions, attribution rules and campaign mix (company, audience, location) were not controlled. Historical correlations are not causal effects.
- **Statistical vs practical significance:** with 18 million clicks per channel, tiny differences become "significant". We judge the **size** of a difference, not just its p-value.
- **Power limitations:** the simulation assumed normal daily CPA with 15% noise (our real noise is about 8.6%, so the estimates are conservative). It also assumes stable conditions over time.
- **Scalability:** a channel's CPA may rise if it receives much more budget (diminishing returns), which this data cannot show.

## Next steps
1. Keep the current, roughly equal allocation for the next month.
2. Design a 6–8 week **geo or holdout experiment** for the 2–3 largest channels, with a pre-defined success metric (incremental CPA) and a sample size based on this power analysis.
3. Repeat this analysis on **our own first-party data**, with real conversions and revenue, before any major reallocation.
4. Review creative and audience performance within channels, where larger gains are more likely.
