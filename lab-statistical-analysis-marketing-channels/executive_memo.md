# Executive memo · Marketing channel performance (2021 campaign data)

**To:** Head of Marketing · **From:** Jaime Garate Marquerie, analytics consultant · **Date:** 24 November 2026
**Data:** Kaggle "Marketing Campaign Performance Dataset" (200,000 campaigns, 6 channels, 1 Jan–31 Dec 2021)

## Executive summary

**The six channels perform the same on cost per conversion.**

- **Cost per conversion (CPA):** the best (Website, $281.93) and the worst (Google Ads, $285.22) differ by only 1.2 %. None of the 15 pairwise t-tests on daily CPA is significant, before or after correction.
- **Conversion rate:** nine pairs pass the significance test even after FDR correction. That is because each channel has about 18 million clicks, which makes very small differences detectable. The largest difference is 0.06 percentage points (8.03 % vs 7.98 %), so it has **no business value** (Cohen's h = 0.002).

**Recommendation:** do **not** move budget between channels on this evidence. Split the $500K roughly equally and run a proper A/B test if a 2–3 % CPA gain matters.

## Key findings

| Finding | Evidence |
|---|---|
| CPA: no channel is better | 0 of 15 t-tests significant (uncorrected, Bonferroni and FDR). Largest gap: Instagram vs Website, −1.15 %, p = 0.076, Cohen's d = 0.13 (negligible) |
| ROAS: two "wins" were false positives | Email vs Facebook (p = 0.049) and Facebook vs Instagram (p = 0.006) look significant without correction. Both disappear after FDR (adjusted p = 0.36 and 0.09) |
| Conversion rate: significant but negligible | 9 of 15 Fisher tests significant after FDR. Every relative gap is ≤ 0.7 %, odds ratios 0.995–1.008 |
| The data was enough to see real differences | 365 days per channel. Even under the lab's conservative assumption (daily CPA SD = 15 % of the mean), a 5 % CPA difference is detected with 88 % power at only 180 days. With the observed SD (8.6 %), the minimum detectable difference at 80 % power is about **$5.10 (1.8 %)** |
| Daily CPA 95 % confidence intervals overlap | All six intervals sit between $281 and $289 (bootstrap, 1,000 resamples) |

## Statistical confidence

- **Thirty tests were run** (CPA and conversion rate), so about **1.5 false positives** were expected by chance at α = 0.05. The ROAS results show exactly that.
- **All decisions use FDR (Benjamini-Hochberg) corrected results.** Bonferroni is stricter: 7 conversion pairs stay significant instead of 9.
- **Practical significance was checked separately (Cohen's d and h).** No difference reaches even the "small" threshold.

## Budget recommendation ($500K)

**Equal split, about $83K per channel.**

- **Why not rank:** a rank-based model would give Website 24.5 % and Instagram 10 % (`results/allocation.csv`, composite of CPA and ROAS, bounded at 10–25 % per channel). But that ranking **is driven by noise**: the gaps between channels are smaller than their confidence intervals.
- **Validation test:** if a 2–3 % improvement is worth pursuing, run a randomized A/B test between the two channels the business cares about most. Use a fixed duration chosen with the power curve, about 120–180 days for a 5 % effect at this spread.
- **Monitoring:** track daily CPA, ROAS and conversion rate per channel on a dashboard. Re-run this analysis every quarter with FDR correction, and act only on differences that are both significant and above 5 %.

## Caveats

- **The dataset appears synthetic.** It has perfectly balanced channels, identical spend levels, the same 10 % CTR everywhere and no seasonality. Real 2021 data would be messier. Treat these results as a method demonstration, not market evidence.
- **Conversions are estimated** as conversion rate × clicks. The rate is rounded to two decimals per campaign, which adds noise to the counts used in the Fisher tests.
- **Revenue is derived from ROI** (cost × (1 + ROI)), and Acquisition_Cost is treated as campaign spend.
- **The simulated power analysis assumes normal daily CPA** with the spread observed in 2021. External factors (campaign mix, audience, location) were not controlled.
