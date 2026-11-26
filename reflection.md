# Reflection

## What surprised me

The lab is framed around the danger of false positives. In this data that danger barely showed up: 14 of 15 CPA pairs were significant before correction and stayed significant after it. Google Search and LinkedIn don't differ by 10%. Their CPAs differ by a factor of 80. With three years of weekly data, no correction method changes that.

The real risk turned out to be **false negatives**. When I re-ran the same tests on the last 13 weeks, which is what a quarterly review would look at, Meta's 21 to 28% CPA lead over TikTok and Snapchat disappeared (p = 0.08 and 0.30). Someone reading that quarterly table would conclude "the social channels are equivalent". That reading is wrong: the test had 28 to 41% power.

The second surprise was the noise assumption. The spec simulates weekly CPA with a 15% standard deviation. The observed figure is about 40%. Because the required sample size scales with variance, that one assumption understated the data we need by about 7 times.

## How multiple-comparisons correction changed my conclusions

On the full data, it didn't. On the 13-week window, Bonferroni removed one pair (Google Display vs TikTok, p = 0.004 against a cutoff of 0.0033) and FDR kept it. I learned that correction matters at the margin, where p-values sit near the threshold, which is also where small samples put them. The method choice depends on what a false positive would cost. For "shift some budget", FDR is right: a wrong call is cheap and reversible. For "switch a channel off", I'd use Bonferroni.

Correction also made me think about how to define a "family" of tests. I treated CPA and conversion rate as separate families of 15, as the spec does. Pooling them into one family of 30 would halve the Bonferroni threshold and change nothing here, but in a closer race it could.

## Limitations

- The data is synthetic, so channel gaps are cleaner than in real accounts.
- I restricted the scope to Sales campaigns and aggregated to weeks. Both choices are defensible, and both affect the results: daily data would give more samples but noisier, often undefined CPAs.
- Fisher's exact test assumes each click is independent. It isn't (same ads, same week, same audience), so the conversion-rate p-values are far too small. A weekly t-test or a mixed model is more honest.
- CPA is a ratio, so the mean of weekly CPAs and the pooled CPA differ. I used weekly values for the tests and pooled totals for budget figures, and said so.
- Strong Q4 seasonality (about −40% CPA) adds noise to every weekly comparison. Season-adjusting CPA before testing would raise power.
- The allocation rule uses ranks, so it ignores how big each gap is. Search is 5 times better than Meta but gets only 1.2 times its budget. A better model would use marginal-return curves per channel.

## Communicating to non-technical stakeholders

- Lead with the decision and the dollar amount ("move about $74K a month from LinkedIn"), not with p-values.
- Replace "statistically significant" with "a gap we can trust" and "not significant" with "too close to call with this data". Never say "no difference".
- Show confidence intervals as ranges on a chart. Overlapping bars explain a tie better than a p-value does.
- Turn power into a calendar: "to see a 10% gap we'd need about 5 years of weekly data, so we should run a test instead of waiting."
- State the strongest caveat first. In this lab that is "synthetic data, re-run on ours before acting".
