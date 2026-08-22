# Reflection

**What surprised me about the results?**
How stark the split was between CPA and conversion rate. Not a single pairwise
CPA comparison came close to significance (all uncorrected p > 0.08), while 9
of 15 conversion-rate comparisons survived FDR correction. That's not because
conversion rate "matters more" — it's because n ≈ 33K per channel gives Fisher's
exact test enormous power to detect even a 0.02–0.06 percentage-point gap. It's
a clean, real-world illustration of statistical significance without practical
significance.

**How did multiple comparisons correction change my conclusions?**
For CPA, correction changed nothing — there was nothing significant to lose.
For conversion rate, Bonferroni dropped 9 significant results to 7 (two
borderline pairs, e.g. Google Ads vs Instagram at p≈0.019, didn't survive the
stricter α=0.0033 threshold), while FDR kept all 9. If I'd only looked at
uncorrected p-values, I'd have reported 9 "wins" with false confidence; FDR
still reports 9 here, but with adjusted p-values that make the margin visible,
and Bonferroni shows how fragile 2 of those 9 really are.

**What are the limitations of this analysis?**
- Public Kaggle dataset, not proprietary company spend data — the exact
  numeric magnitudes (CPA around $12,500, ROI 2-8x) won't transfer to a real
  $500K/month budget without validation against actual spend data.
- "Conversions" for the Fisher's exact test is estimated as
  Clicks x Conversion_Rate, not a raw logged conversions count, since the
  dataset doesn't provide one.
- Power analysis relies on simulation assumptions (normally distributed CPA,
  fixed 15%-of-mean standard deviation) that may not hold for real spend data.
- The composite budget-allocation score (50% CPA rank / 50% ROI rank) is a
  reasonable default, not a validated business rule — a real allocation
  decision should weight metrics based on the CMO's actual priorities.

**How would I communicate these findings to non-technical stakeholders?**
Lead with the CPA finding in plain language: "we don't see real evidence that
any one channel is cheaper per acquisition than another - the differences we
see look like noise." Then flag the conversion-rate finding carefully: "some
channels do convert at a statistically real but very small rate - a fraction
of a percentage point - so I wouldn't move budget on this alone." Show the
confidence-interval table rather than just point estimates, since overlapping
CIs make the "these channels are basically tied" story visually obvious even
without explaining p-values.
