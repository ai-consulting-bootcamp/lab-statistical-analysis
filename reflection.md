# Reflection

**What surprised me about the results?**
None of the six pairwise CPA comparisons survived correction — even though the
raw channel averages looked meaningfully different (Email at $0.31 vs. Social
Media at $0.50, a ~230% relative gap). Cohen's d for every CPA pair was
negligible-to-small, which is a good reminder that eyeballing a bar chart of
group means is a bad way to make budget decisions: campaign-to-campaign
variance within each channel was large enough to swallow the between-channel
signal.

**How did multiple comparisons correction change my conclusions?**
For CPA, correction didn't change anything — none of the 6 comparisons were
significant even before correcting, so Bonferroni/FDR were moot there. For
conversion rate, all 6 comparisons stayed significant even under the strict
Bonferroni correction, but only because the test pools clicks across every
campaign in a channel, producing enormous effective sample sizes. That
inflated the CPA-vs-conversion-rate asymmetry: it made me separate "passed
correction" from "is commercially meaningful" as two different questions
rather than treating a low p-value as the end of the analysis.

**What are the limitations of this analysis?**
- The dataset is a 400-campaign sample of a public/synthetic Hugging Face
  dataset, not real company spend data — good for practicing the statistical
  workflow, not for making live decisions.
- Fisher's exact test was run on channel-level pooled totals rather than
  campaign-level binary outcomes, which inflates N and makes trivial rate
  differences look highly significant. A more rigorous version would run the
  test (or a logistic regression / mixed model) at the campaign or even
  user level.
- The power simulation assumes normally distributed CPA with a fixed 15% SD;
  real campaign data is likely to be right-skewed, so the sample-size
  recommendations are a reasonable first estimate, not a guarantee.

**How would I communicate these findings to non-technical stakeholders?**
Lead with the one-line takeaway: "channels perform similarly on cost per
acquisition — we can't statistically tell them apart on that metric yet — but
Social Media edges out on return and Email converts noticeably better." Skip
p-values and Cohen's d in the room; show the bar chart with error bars (the
confidence intervals) so people can see the overlap visually, and frame the
budget table as a modest rebalancing with the reasoning attached, not a
verdict on any channel being "bad."
