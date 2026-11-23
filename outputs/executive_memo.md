# Executive memo — Marketing budget allocation

**To:** CMO · **From:** Nicolò · **Date:** 23 November 2026 · **Dataset:** Marketing Campaign Performance (22,029 campaigns, 6 channels) · **Period:** 2023-01-01 to 2023-12-31

## Executive summary
The six channels perform almost the same. Cost per acquisition sits between $49.08 (Facebook) and $51.76 (Instagram), and ROAS between 1.97 and 2.05. After correcting for 45 tests, **no channel has a significantly lower CPA than another**. Two channels (Facebook, Website) convert clicks slightly better, but the gap is at most 0.06 percentage points, which is too small to matter. **Recommendation: do not move budget on this evidence. Keep an even split (about $83,333 per channel) and run a controlled test before reallocating.**

## Key findings
- Top performers: Facebook has the lowest CPA ($49.08) and the highest ROAS (2.05); Instagram is the weakest (CPA $51.76, ROAS 1.97). The whole spread is about 5%.
- Statistically significant differences (after correction): CPA: 0 of 15 pairs (only 1 before correction, Instagram vs Website, and it did not survive). Conversion rate, daily t-test: 0 of 15. Conversion rate, Fisher on all clicks: 8 of 15 pairs, all with gaps of 0.04–0.06 points (about 1% relative). These are "real but tiny": they are significant only because each channel has about 8 million clicks.
- Data adequacy (power): with 363–365 days per channel and the lab's 15% day-to-day spread, we could detect a 5% CPA gap. But the real daily CPA spread is much larger (CV 0.35–0.96), so in practice we can only reliably detect gaps of roughly 10–15%. The observed gaps (0.1–7%) are below that, so "not significant" here means "can't tell", not "proven equal".

## Recommendations
1. **Keep the split even for now: about $83,333 per channel.** The composite-score model would give Facebook $142,500 and Instagram $25,000, but those ranks come from differences we cannot tell apart from noise. Moving ~$100K on that basis is exactly the false positive we want to avoid.
2. **If you want a tilt, keep it small and reversible** (e.g. ±10% per channel), and treat it as a test, not a decision.
3. **Set up a proper test**: pick the 2–3 channels where a decision would really change spend, run them with a pre-agreed success metric (CPA or ROAS), and size it for a 10% difference (see Next steps).

## Statistical caveats
- Dataset source and limits: public Kaggle-style dataset (GitHub copy). It has no conversion or revenue columns: conversions were derived as clicks × conversion rate and revenue as cost × (1 + ROI). The data looks simulated (CTR is 4.4% on every channel; costs are spread evenly between $1,000 and $9,999), so channel effects may be near zero by design.
- Multiple comparisons correction: 45 tests at α = 0.05 would give about 2.25 false positives by chance alone. Benjamini-Hochberg removed the only CPA "win" and all five daily conversion-rate "wins".
- Confidence intervals: the 95% bootstrap intervals for mean daily CPA overlap for every channel (e.g. Website $51.18–$55.16), so no channel is clearly cheaper.
- External factors: no data on seasonality, creative, audience overlap, attribution model or channel saturation. A small channel may not keep its CPA if its budget grows.
- Statistical vs practical significance: the Fisher results are significant but worth about 0.05 points of conversion rate — far below anything that would change the budget.
- Power limitations: the power simulation assumes 15% daily spread; the real spread is 35–96%, so detectable effects are 2–3× larger than the simulation suggests.

## Next steps
- Clean the outliers (days with very few conversions push daily CPA up to $937) and re-run.
- Get real revenue and conversion counts from the ad platforms instead of derived ones.
- Design a 90-day test on the 2–3 channels that matter most, sized for a 10% CPA difference; review results before the next budget cycle.
