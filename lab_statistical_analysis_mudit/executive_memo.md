# Executive Memo: Nykaa Campaign Performance — CPA & Conversion Rate by Campaign Type

**Date:** 25.08.2026
**Analyst:** Mudit Airan
**Dataset:** Kaggle "Nykaa Campaign Data" (`nykaa_campaign_data.csv`), 55,555 campaigns
**Period analyzed:** 2024-07-01 to 2025-06-24

---

## Executive Summary

The CMO asked whether marketing spend should be reallocated across channels based on
cost-efficiency. This analysis compared **CPA (cost per acquisition)** and **conversion rate**
across the 5 campaign types in this dataset (Email, Influencer, Paid Ads, SEO, Social Media).

**Headline finding: there is no statistically or practically meaningful difference in CPA
between campaign types**, and while conversion rate differences are technically significant
after correction, every one is under 1% relative — far too small to act on. With ~11,100
campaigns and 50M+ clicks per group, this dataset has more than enough statistical power to
detect a real 5-20% difference had one existed; its absence is a genuine finding, not a data
limitation.

**Recommendation: do not reallocate budget by `Campaign_Type` on the basis of this analysis.**
Any tilt in spend that this analysis' composite ranking implies is cosmetic, not statistically
supported — see Recommendations and Statistical Caveats below.

---

## Key Findings

### Top performing groups

Differences are small enough that "top performing" should be read with caution (see caveats),
but by point estimate:

- **CPA (lower is better):** Social Media ($166.89) < Influencer ($169.15) < SEO ($169.29) <
  Email ($169.70) < Paid Ads ($170.16) — full table in
  `results/group_summary_by_campaign_type.csv`; range across all 5 groups is **$166.89–$170.16**
  (a $3.27 spread, ~2% of the mean).
- **ROAS:** Social Media (2.97x) highest, Email (2.93x) lowest — a 0.04x spread.
- **Conversion rate (conversions/clicks):** all 5 groups sit within 22.0%–22.2%.

### Statistically significant differences found

- **CPA by Campaign_Type:** **0 of 10** pairwise t-tests were significant even before correction
  (all p > 0.32). Every Cohen's d was negligible (|d| < 0.02). This is a genuine null result —
  correction wasn't needed to rule these out; they were never significant to begin with.
  Full table: `results/ttest_results_corrected.csv`.
- **Conversion rate by Campaign_Type:** **10 of 10** pairwise Fisher's exact tests were
  significant, both before and after Bonferroni/FDR correction. But every single difference is
  **under 1% relative** (range: 0.10%–1.03%). With clicks aggregated in the millions per group,
  even a fractional difference clears the p < 0.05 bar — this is a textbook case of statistical
  significance without practical significance. **These results should not drive budget
  decisions.** Full table: `results/fisher_results_corrected.csv`.

### Data adequacy (power analysis)

- 80% power to detect a 5% relative CPA difference needs only ~180 campaigns/group — current
  data has **~11,100/group, ~62x more than needed**. 80% power to detect a 5% relative
  conversion-rate difference needs ~25,000 clicks/group — current data has **51M+/group,
  ~2,000x more than needed**. Full curves: `figures/power_analysis_cpa.png`,
  `figures/power_analysis_conversion.png`; minimum sample sizes:
  `results/power_min_sample_size.csv`. (Sample size here is expressed in campaigns/clicks per
  group, not "days" as in the lab's original template — this dataset has no daily time series
  per channel to sample from; see `power_analysis.py`'s module docstring and
  `dataset_selection.md` for why.)
- This directly supports the headline finding: **the absence of a large, meaningful difference
  is not because we lack the data to see one** — we have far more than enough. If a real,
  actionable CPA or conversion-rate gap existed between these campaign types, this dataset would
  have detected it.
- One caveat within that: of the 10 FDR-significant conversion-rate pairs, 9 are well-powered
  (≥90%) at their observed (sub-1%) effect size, but the smallest and least practically relevant
  one — Influencer vs. SEO, a 0.10% relative difference — sits at only 76% power. That pair would
  need roughly 77M clicks/group (vs. ~52M today) to reach 80% power for an effect this tiny.
  This doesn't change the conclusion (a 0.10% difference isn't actionable regardless of power),
  but it's the one place in this analysis where "significant after correction" is running close
  to the edge of what the data can reliably support. Full table:
  `results/power_current_data_adequacy.csv`.
- Power estimates throughout this section are Monte Carlo simulations (300-500 runs per point),
  so treat them as approximate — see Statistical Caveats.

---

## Recommendations

1. **Do not reallocate the $500K monthly budget by `Campaign_Type` based on CPA or conversion
   rate.** There is no statistically defensible basis to prefer one campaign type over another
   on these metrics — see `results/allocation_recommendation.csv` for the composite-ranking
   exercise the lab template calls for, but treat it as illustrative only (see caveat below),
   **not** an actionable reallocation.

2. **Investigate other dimensions the data does support**, which this analysis did not test but
   which are available in the source file: `Channel_Used` (specific platforms, e.g. Instagram,
   WhatsApp, YouTube — 156 raw combinations, would need cleanup), `Target_Audience`,
   `Customer_Segment`, and `Duration`. If budget reallocation is the goal, these are more
   promising places to look for a real signal than `Campaign_Type`.

3. **Treat the current allocation (or an even split) as the safe default** until a dimension
   with a real, practically meaningful effect is found. Continuing to split spend roughly evenly
   across Email, Influencer, Paid Ads, SEO, and Social Media is not a mistake here — it's what
   the evidence supports.

4. **Re-run this comparison periodically as new campaigns accumulate**, in case channel
   performance genuinely shifts over time — this snapshot (Jul 2024–Jun 2025) shows no
   difference *now*, which is not a permanent guarantee.

---

## Statistical Caveats

- **Dataset limitations and source:** Kaggle "Nykaa Campaign Data", 55,555 campaign-level rows.
  See `dataset_selection.md` for full discussion, including why `Campaign_Type` (not the more
  granular `Channel_Used`) was used as the grouping variable.
- **Multiple comparisons correction applied:** Benjamini-Hochberg FDR (primary) and Bonferroni
  (reported alongside) across the 10 `Campaign_Type` pairwise comparisons in each metric family
  (CPA, conversion rate). See `multiple_comparisons_correction.py` output for full detail.
- **Confidence intervals:** bootstrap 95% CIs (1,000 resamples) for mean CPA and conversion rate
  by group are in `results/confidence_intervals.csv` — they overlap heavily across all 5 groups,
  consistent with the null/near-null findings above.
- **Statistical vs. practical significance:** the conversion-rate family is the clearest
  illustration in this analysis — with 50M+ clicks per group, even a 0.1% relative difference is
  "significant." Every comparison's percentage difference was checked against a 10%
  practical-meaningfulness screen for exactly this reason, and none passed.
- **The composite ranking / allocation table is a required lab deliverable, not a
  recommendation.** It ranks groups by CPA and ROAS point estimates (50/50 weighting, per the
  lab's suggested formula) even though neither metric showed a statistically or practically
  meaningful difference. Reading it as "Social Media should get 30% of budget" would be
  overstating what the data supports — see Recommendation 1.
- **Power analysis limitations:** power curves are Monte Carlo estimates (300–500 simulations
  per point) under a normal (CPA) or binomial (conversion rate) data-generating assumption —
  treat every power/n figure in this memo as approximate, not exact. The real CPA distribution
  is right-skewed (a small number of very high-cost campaigns), and real-world seasonality or
  campaign-mix shifts over the year analyzed are not modeled. Sample size is also expressed in
  **campaigns/clicks per group**, not the "days" unit the lab's original template specifies —
  this dataset is campaign-level with no daily time series per channel to sample from (see
  `power_analysis.py`'s module docstring), so campaigns/clicks are used as the closest available
  analog to one day's worth of observations in the lab's original design.
- **External factors:** `Campaign_Type` groups are observational, not from a randomized
  experiment — campaigns of each type may have been run against different audiences, budgets, or
  time periods, so this is a correlational comparison. That said, the finding here is a **null**
  result (no difference), which is generally more robust to this kind of confounding than a
  positive finding would be — confounding would more plausibly *create* a spurious difference
  than hide a real one across 55,555 campaigns.

---

## Next Steps

- [ ] Repeat this comparison using `Channel_Used` (after resolving multi-channel campaigns,
      e.g. by exploding to one row per platform) to check whether individual platforms
      (Instagram, YouTube, WhatsApp, etc.) show a real CPA or conversion-rate gap that
      `Campaign_Type` averages over.
- [ ] Repeat using `Target_Audience` and `Customer_Segment` as grouping variables.
- [ ] Test whether `Duration` (campaign length) correlates with CPA or conversion rate.
- [ ] Re-test this exact comparison in 6-12 months as more campaigns accumulate, in case channel
      performance diverges over time.
