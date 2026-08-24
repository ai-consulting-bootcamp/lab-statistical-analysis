# Executive Memo: Marketing Channel Budget Allocation

**To:** CMO
**From:** Marketing Analytics
**Date:** August 24, 2026
**Dataset:** Marketing Campaign Performance Dataset (Kaggle, 22,029 campaigns, 6 channels, full year 2023)
**Period analyzed:** Jan 1 – Dec 31, 2023 (full calendar year, all 6 channels)

## Executive Summary

We compared six channels — Email, Facebook, Google Ads, Instagram, Website, YouTube — on cost
per acquisition (CPA), return on ad spend (ROAS/ROI), and conversion rate, using t-tests and
Fisher's exact tests with Bonferroni and Benjamini-Hochberg (FDR) correction for multiple
comparisons. **The topline finding is a caution, not a green light**: after correcting for the
45 comparisons we ran, no channel shows a CPA or ROI difference that is both statistically
*and* practically significant. Conversion rate differences are statistically significant for 8
of 15 channel pairs even after correction, but the largest gap is 0.06 percentage points —
not something we'd act on alone. We recommend a **modest, evidence-light reallocation** rather
than a large bet on any single channel, guided primarily by CPA point estimates and their
confidence intervals.

## Key Findings

**Top performing channels (point estimates, not yet proven statistically distinct):**
- **Email** has the lowest mean CPA ($130.55, 95% CI $121.63–$140.40) and a strong ROAS (2.86x).
- **Facebook** has the highest ROAS (2.88x) and second-lowest CPA ($141.07).
- **YouTube** and **Website** are the weakest on CPA ($150.03 and $149.11 respectively).

**Statistically significant differences found (after FDR correction):**
- **CPA and ROI: zero pairs remained significant after either Bonferroni or FDR correction.**
  Two CPA pairs (Email vs. Website, Email vs. YouTube) were significant *before* correction
  (p≈0.015) but did not survive multiple-comparisons correction — these were very likely two
  of the ~2.25 false positives we'd statistically expect from 45 tests at α=0.05.
- **Conversion rate (Fisher's exact test): 8 of 15 pairs remained significant after FDR**,
  e.g., Facebook vs. Instagram (p_fdr < 0.001). However every one of these differences has a
  **negligible effect size** — Cohen's d for the CPA comparisons ranges from 0.00 to 0.06 — and
  the conversion-rate gaps are all under 0.06 percentage points. With ~8 million clicks per
  channel, even a real but tiny business gap can register as statistically "significant." This
  is a textbook case of statistical vs. practical significance.

**Data adequacy (power analysis):**
- With 90 days of campaign data per channel, we have ~99%+ power to detect a CPA difference of
  10% or larger, but only ~60% power to detect a 5% difference — meaning a real 5% CPA gap
  between two channels could easily go undetected with the data we have today.
- To reliably detect a 5% CPA difference at 80% power, we'd need roughly **160 days** of
  campaign data per channel (vs. 90 today).

## Recommendations

### Budget allocation ($500K/month, guided by CPA/ROAS point estimates, not statistical proof)

| Channel | Allocation | Amount | Why |
|---|---|---|---|
| Email | ~31% | ~$154K | Lowest CPA, strong ROAS, well-established channel |
| Facebook | ~20% | ~$100K | Best ROAS, second-best CPA |
| Google Ads | ~17% | ~$83K | Solid mid-pack performer, largest search-intent reach |
| Instagram | ~13% | ~$63K | Reasonable CPA, lowest ROAS — monitor |
| Website (owned) | ~10% | ~$50K | Weakest CPA — floor allocation to keep testing |
| YouTube | ~10% | ~$50K | Weakest CPA — floor allocation to keep testing |

We applied an 8%–30% floor/ceiling per channel deliberately: **because none of the CPA/ROI
differences are statistically robust after correction, we should not fully defund any channel
or over-concentrate spend on the current point-estimate "winner."** This allocation is a
directional tilt, not a statistically proven optimum.

### Strategic actions
- **Do not cut Website or YouTube spend to zero.** Their apparent CPA disadvantage is not
  statistically distinguishable from Email/Facebook/Google Ads/Instagram after correction.
- **Extend the observation window** before making a larger reallocation. At minimum, collect
  ~160 days of comparable data per channel if the goal is to reliably detect a 5% CPA edge.
- **Run a proper A/B/n budget test** (holdout or geo-split) rather than relying solely on
  observational campaign data, since campaign-level confounds (audience, creative, timing)
  aren't controlled for here.
- **Revisit in one quarter** with a fresh pairwise comparison and updated power analysis.

## Statistical Caveats

- **Dataset limitations and source:** Kaggle "Marketing Campaign Performance Dataset"
  (22,029 rows, synthetic/aggregated campaign-level data covering 2023). It does not represent
  our company's actual campaigns; it is used here to demonstrate the statistical method the CMO
  requested. Real budget decisions should rerun this pipeline on our own campaign data.
- **Multiple comparisons correction applied:** Bonferroni (conservative) and Benjamini-Hochberg
  FDR (less conservative) were both applied across all 45 pairwise comparisons (15 CPA + 15 ROI
  + 15 conversion-rate). Only FDR-corrected conversion-rate results survived, and even those
  are of negligible practical size.
- **Confidence intervals:** 95% bootstrap CIs for CPA are reported per channel; several
  channels' CIs overlap substantially, reinforcing that point-estimate rankings alone should
  not drive large budget swings.
- **External factors:** Seasonality, creative quality, competitive bidding, and audience
  saturation are not controlled for in this analysis and could explain observed differences
  better than channel choice itself.
- **Statistical vs. practical significance:** This is the central lesson of this analysis —
  large sample sizes (millions of clicks) can make tiny, business-irrelevant differences
  statistically detectable. Effect size (Cohen's d) and CI width should always be read
  alongside the p-value.
- **Power analysis limitations:** The power simulation assumes normally distributed CPA around
  today's observed mean/variance; real-world CPA distributions may be skewed, which could
  understate or overstate the sample sizes actually required.

## Next Steps
1. Approve the directional budget tilt above for next month as a low-risk starting point.
2. Stand up a formal geo-holdout or budget-split test for Email vs. Website/YouTube to get a
   causal read, not just observational.
3. Re-run this pipeline monthly; flag any pair whose FDR-corrected p-value AND Cohen's d both
   cross significance/medium-effect thresholds simultaneously before making a bigger move.
4. Extend the data window toward 160+ days per channel to reach 80% power for 5% CPA gaps.
