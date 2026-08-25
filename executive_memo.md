# Executive Memo: Marketing Channel Performance & Budget Allocation

**To:** CMO
**From:** Marketing Analytics
**Date:** 2026-08-24
**Dataset:** alsayed7/marketing_dataset (Hugging Face), 400-campaign sample across
4 channels (Email, Influencer Marketing, Paid Ads, Social Media)
**Period analyzed:** campaigns spanning May 2022 – Nov 2024 (dataset-relative dates)

## Executive Summary

Across 400 campaigns, all four channels post similar ROAS (2.58x–2.66x) and similar
profit margins (~61–62%). CPA differences between channels are **not statistically
significant** once tested rigorously — the apparent CPA gaps in the raw averages
are within the range of random variation. Conversion-rate differences **are**
statistically significant, but the largest gap is only ~6.5 percentage points and
several "significant" gaps are under 1 percentage point — a reminder that with a
large denominator (millions of clicks), even trivial differences clear the p<0.05
bar. **We recommend a modest rebalancing toward Social Media and away from Paid
Ads, not a dramatic reallocation** — the data does not support a bold bet on any
single channel at this time.

## Key Findings

**Channel performance (aggregate, 400 campaigns):**

| Channel | Campaigns | CTR | Conv. Rate | CPA | ROAS | Profit Margin |
|---|---|---|---|---|---|---|
| Email | 102 | 56.3% | 53.8% | $0.31 | 2.58x | 61.2% |
| Influencer Marketing | 104 | 50.1% | 47.3% | $0.44 | 2.62x | 61.8% |
| Paid Ads | 106 | 45.5% | 48.1% | $0.53 | 2.64x | 62.1% |
| Social Media | 88 | 49.3% | 48.5% | $0.50 | 2.66x | 62.4% |

*(CPA/ROAS units follow the dataset's own spend/revenue scale, not literal
dollars — see Caveats.)*

**Statistically significant differences (after Benjamini-Hochberg FDR correction, α=0.05):**

- **CPA:** 0 of 6 pairwise comparisons remained significant. The raw CPA gaps
  (Email $0.31 vs. Social Media $0.50, a ~230% relative difference) look large but
  Cohen's d for every CPA comparison was "negligible" to "small" (d ≤ 0.26), and
  none survived correction for multiple testing. **We do not have statistical
  evidence that any channel has a genuinely lower CPA than another.**
- **Conversion rate:** All 6 of 6 pairwise comparisons were significant, including
  after Bonferroni (the strictest correction). Email converts at 53.8% vs. 47.3%
  for Influencer Marketing — a real, replicable gap. However, three of the six
  "significant" pairs (Influencer Marketing vs. Paid Ads, vs. Social Media, and
  Paid Ads vs. Social Media) differ by 1–3 percentage points; because the test
  pools clicks across all campaigns (millions of observations), even
  differences with little practical import register as p<0.001. Treat only the
  larger gaps (Email vs. everything else, ~6–9 points) as commercially meaningful.

**Data adequacy (power analysis):** With ~90 observations per channel, we have
80%+ power to detect CPA differences of 10% or larger, but only ~60% power to
detect a 5% difference. This is consistent with the CPA results: the observed
gaps were noisy enough, and the true underlying differences (if any) are small
enough, that we could not confirm them statistically.

## Recommendations

**1. Monthly budget allocation ($500K total)** — based on a composite score
(50% CPA rank + 50% ROAS rank), with guardrails of 10%–40% per channel so no
channel is starved or over-concentrated given the CPA result was not
statistically significant:

| Channel | Recommended Allocation | % of Budget |
|---|---|---|
| Social Media | $153,061 | 30.6% |
| Email | $122,449 | 24.5% |
| Influencer Marketing | $122,449 | 24.5% |
| Paid Ads | $102,041 | 20.4% |

This is a **rebalancing, not a reallocation** — Paid Ads (currently likely the
largest or a large share of spend) moves down modestly in favor of Social Media,
which posts the best ROAS (2.66x) and best profit margin (62.4%) despite CPA
differences being statistically inconclusive.

**2. Do not defund any channel based on CPA alone.** Since no CPA difference
survived correction, cutting a channel's budget on the premise that it has a
"worse CPA" would be exactly the kind of costly, false-positive-driven mistake
this analysis was designed to prevent.

**3. Prioritize Email's conversion-rate advantage operationally**, not just
budget: the Email vs. others gap is the one conversion-rate finding large enough
(6–9 points) to be commercially actionable — worth testing whether Email's send
cadence, list segmentation, or offer structure can be adapted to other channels.

**4. Re-test CPA in 60–90 more days.** Per the power analysis, detecting a
true 10% CPA difference reliably needs ~60 days of channel-level data; we
likely have that on aggregate but campaign-level noise (SD ≈ 15% of mean CPA)
means smaller (5%) differences need closer to 180 days. Re-run this analysis
after another quarter of data before making a larger reallocation.

## Statistical Caveats

- **Dataset**: sample of 400 campaigns pulled from a 2,000-row public Hugging
  Face dataset (synthetic/aggregated demo data representative of real
  e-commerce campaign structures, not this company's live spend). Treat this as
  a methodology validation exercise; **before acting on real budget, this
  analysis should be re-run on the company's actual platform data.**
- **Multiple comparisons**: 12 pairwise tests were run (6 CPA + 6 conversion
  rate). At uncorrected α=0.05 we'd expect ~0.6 false positives by chance alone;
  Benjamini-Hochberg FDR correction was applied to control this.
- **Statistical vs. practical significance**: several conversion-rate
  comparisons were "significant" purely because of enormous pooled sample
  sizes (millions of clicks), while representing sub-1-point rate differences.
  We weighted commercial meaningfulness (Cohen's d, absolute point gap)
  alongside p-values in every recommendation above.
- **Confidence intervals are wide**: bootstrap 95% CIs for mean CPA per channel
  span roughly 2x–7x (e.g., Influencer Marketing: $2.29–$14.68), reflecting
  real campaign-to-campaign variability. Point estimates should not be treated
  as precise.
- **Power limitations**: our simulation assumes CPA is roughly normally
  distributed with SD = 15% of the mean; if real variance is higher, more days
  of data will be needed than shown here.
- **External factors** not modeled: seasonality, one-off promotions, audience
  overlap/cannibalization between channels, and attribution-window effects
  (last-click vs. multi-touch) could all shift true channel performance.

## Next Steps

1. Re-run this pipeline on the company's actual platform-level campaign data
   (Google Ads, Meta, ESP, affiliate/influencer platform exports).
2. Extend the observation window to ≥180 days before making CPA-based budget
   cuts, per the power analysis.
3. Set up a lightweight quarterly cadence for this analysis so allocation
   decisions are re-validated rather than made once and left static.
4. Run a controlled test isolating Email's conversion-rate driver (offer,
   segmentation, or cadence) to see if it transfers to other channels.
