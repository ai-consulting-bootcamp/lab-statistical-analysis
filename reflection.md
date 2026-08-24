# Reflection

**What surprised me about the results?**
How consistently "flat" the six channels turned out to be on the metrics that actually drive
budget decisions (CPA, ROI). Two CPA pairs looked significant before correction, but neither
survived Bonferroni or FDR — a clean illustration of why the correction step exists. The
conversion-rate test told a different story: with millions of clicks per channel, even a
0.05-percentage-point gap becomes "significant," which is a good reminder that p-values are a
function of sample size as much as of real effect size.

**How did multiple comparisons correction change the conclusions?**
Substantially. Before correction, 10 of 45 comparisons looked significant (2 CPA + 8
conversion-rate). After FDR, only the 8 conversion-rate comparisons survived — and every one of
them has a negligible effect size. If we'd stopped at uncorrected p-values, we might have
reallocated budget away from Website/YouTube based on what turned out to be noise.

**What are the limitations of this analysis?**
- The dataset is synthetic/aggregated Kaggle data, not our own campaigns — useful for practicing
  the method, not for a real budget decision as-is.
- Campaign-level confounds (audience segment, creative, seasonality, competitor activity) aren't
  controlled for — this is observational, not experimental, data.
- The derived metrics (Conversions, Revenue, CPA, ROAS) were back-calculated from
  Conversion_Rate/Cost/ROI, which is a reasonable approximation but not a guarantee of exact
  real-world accuracy.
- The power simulation assumes a specific noise model (normal, 15% CV) that may not match the
  true variability of real CPA data.

**How would I communicate these findings to non-technical stakeholders?**
Lead with the practical takeaway, not the statistics: "the six channels perform similarly on
cost efficiency once we account for the number of tests we ran — small differences we might
have believed by eyeballing the data don't hold up. We recommend a modest tilt toward
Email/Facebook rather than a big bet, and a proper A/B test before making bigger changes."
Save Cohen's d and FDR-corrected p-values for the appendix; the CMO cares about "should I move
the money," not the mechanics of Benjamini-Hochberg.
