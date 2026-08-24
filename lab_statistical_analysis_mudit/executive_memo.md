# Executive Memo: Marketing A/B Test & Ad-Delivery Timing Analysis

**Date:** 25.08.2026
**Analyst:** Mudit Airan
**Dataset:** Kaggle "Marketing A/B Testing" (`marketing_AB.csv`), 588,101 users
**Period analyzed:** Not date-stamped in source data; day-of-week and hour-of-day only

---

## Executive Summary

This analysis had two goals: (1) confirm whether showing ads (vs. a public-service-announcement
control) actually increases conversion, and (2) test whether conversion performance and ad
exposure vary meaningfully by day of week, in order to inform ad-delivery scheduling.

**Headline finding:** users shown real ad creative converted at **2.55%**, vs. **1.79%** for
users shown the PSA control — a statistically significant **30% relative lift**
(p = 1.05 × 10⁻¹⁴, odds ratio = 1.44). This is the single most defensible, decision-ready result
in this dataset.

**Secondary finding:** conversion rate varies meaningfully by the day of week a user received
most of their ads — Monday (3.28%) is the strongest day and Saturday (2.11%) the weakest, and
most of these day-pair differences survive correction for multiple comparisons. Ad *exposure*
(`total_ads`) also differs by day in a statistically significant way, but every one of those
differences has a negligible effect size (Cohen's d) — a textbook case of statistical
significance without practical significance, discussed further below.

**Important scope note:** this dataset has no cost, revenue, impressions, or click data, so
**CPA, ROAS, and CTR could not be calculated**, and no literal per-channel budget allocation is
possible. See Statistical Caveats.

---

## Key Findings

### Top performing groups

- **Experiment arm:** `ad` beats `psa` on conversion rate — 2.55% vs. 1.79% (+30.1% relative,
  p = 1.05e-14, survives at any reasonable correction threshold since it is the single planned
  comparison).
- **Day of week (by conversion rate):** Monday (3.28%) > Tuesday (2.98%) > Wednesday (2.49%) >
  Sunday (2.45%) > Friday (2.22%) > Thursday (2.16%) > Saturday (2.11%).

### Statistically significant differences found

- **Conversion rate by day of week:** 17 of 21 pairwise comparisons remained significant after
  Benjamini-Hochberg (FDR) correction (full table: `results/fisher_results_corrected.csv`).
  Monday and Tuesday are reliably higher-converting than every other day.
- **Ad exposure (`total_ads`) by day of week:** 19 of 21 pairwise comparisons were "significant"
  both before and after correction, **but every single one had a negligible Cohen's d (|d| < 0.1)**
  (`results/ttest_results_corrected.csv`). With ~80,000 users per day-of-week group, even a
  practically trivial difference in mean ad exposure clears the p < 0.05 bar. **These results
  should not drive any action** — correction alone did not filter them out; effect size did.

### Data adequacy (power analysis)

- At current sample sizes (77,479–92,608 users per day-of-week group), we have **≥80% power**
  to detect 13 of the 17 FDR-significant conversion-rate differences and 16 of the 19
  FDR-significant `total_ads` differences we actually observed.
- Four pairs are under-powered at current n (58–77% power): Tuesday–Wednesday, Tuesday–Thursday,
  and Tuesday–Sunday for `total_ads`, and Monday–Tuesday for conversion rate. Treat these four as
  provisional pending more data. Full table: `results/power_current_data_adequacy.csv`.
- For future, smaller-scale tests: detecting a 15–20% relative difference in conversion rate
  reliably (80% power) needs roughly 20,000–50,000 users per group; a 10% relative difference
  needs on the order of 100,000 per group at this base rate (~2.5%). Full curves:
  `figures/power_analysis_conversion.png`, `results/power_min_sample_size.csv`.

---

## Recommendations

1. **Keep running ad creative over the PSA control.** This is the best-supported, most powerful
   finding in the data (p = 1.05e-14, well-powered, single planned comparison — no correction
   concerns). If any campaigns are currently defaulting to PSA-style placeholder creative, that
   is the highest-value fix available from this analysis.

2. **Weight ad delivery toward Monday and Tuesday**, where conversion rates are reliably higher
   even after FDR correction. `results/allocation_recommendation.csv` translates the day-of-week
   composite ranking into a bounded delivery-schedule weighting (8%–25% per day):

   | Day | Conversion rate | Recommended delivery weight |
   |---|---|---|
   | Monday | 3.28% | 25.0% |
   | Tuesday | 2.98% | 25.0% |
   | Wednesday | 2.49% | 13.6% |
   | Sunday | 2.45% | 12.4% |
   | Friday | 2.22% | 8.0% |
   | Thursday | 2.16% | 8.0% |
   | Saturday | 2.11% | 8.0% |

   The $500K figure from the lab scenario is applied only illustratively (Monday/Tuesday ≈
   $125,000/month each) to show what this weighting means in dollar terms — it is **not** a
   validated real budget allocation, since this dataset has no real per-channel spend data.

3. **Do not use the `total_ads`-by-day results to change exposure/frequency strategy.** They are
   statistically significant purely due to sample size; the effect sizes are all negligible.

4. **Collect cost and revenue data going forward.** The single biggest gap limiting this
   analysis is the absence of spend and revenue fields — without them, CPA and ROAS (the metrics
   this kind of decision should really be based on) cannot be computed at all.

---

## Statistical Caveats

- **Dataset limitations and source:** Kaggle "Marketing A/B Testing" dataset, 588,101 rows,
  user-level, no cost/revenue/impression/click fields, no date stamps (only day-of-week/hour-of-day).
  See `dataset_selection.md` for full discussion.
- **No CPA/ROAS/CTR:** these could not be calculated; all recommendations here are based on
  conversion rate and ad-exposure counts only, not cost efficiency.
- **Multiple comparisons correction applied:** Benjamini-Hochberg FDR (primary) and Bonferroni
  (reported alongside) across the 21 day-of-week pairwise comparisons in each metric family.
  See `multiple_comparisons_correction.py` output for full detail.
- **Confidence intervals:** bootstrap 95% CIs (1,000 resamples) reported for mean `total_ads`
  and conversion rate by day in `results/confidence_intervals.csv`; several day-pairs have
  overlapping CIs even where the point-estimate difference is statistically significant —
  read the CI table alongside the p-values, not instead of them.
- **Statistical vs. practical significance:** the `total_ads` findings are the clearest
  illustration in this analysis — large sample sizes make even negligible effects statistically
  significant. Cohen's d was checked for every continuous comparison for exactly this reason.
- **Power analysis limitations:** power curves are Monte Carlo estimates (500–1,000 simulations)
  under a normal (continuous) or binomial (binary) data-generating assumption; real-world
  seasonality, day-of-week user-mix differences, and non-stationarity are not modeled.
- **External factors:** day-of-week effects here are correlational (which day a user happened to
  see the most ads), not from a randomized day-of-week experiment — confounding by campaign
  timing, promotions, or audience mix cannot be ruled out. The `ad` vs. `psa` finding, by
  contrast, is a randomized comparison and is the more causally trustworthy result.

---

## Next Steps

- [ ] Instrument cost and revenue by channel/campaign so CPA/ROAS can be computed directly.
- [ ] Run a proper randomized day-of-week or dayparting experiment to test the scheduling
      recommendation causally, rather than relying on the correlational `most_ads_day` grouping.
- [ ] Re-test the four under-powered pairs once more data accumulates.
- [ ] Confirm the ad-vs-psa lift holds when segmented by day of week and any other available
      user attributes, to check the finding isn't concentrated in one subgroup.
