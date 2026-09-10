# Reflection

**What surprised you about the results?**
How lopsided the channel performance was — Google Search wasn't just "better," it was the *only* profitable channel across three full years, with a ROAS of 3.78 versus 0.11–0.62 everywhere else. I expected a statistics exercise to surface subtle, contestable differences; instead the effect sizes were mostly medium-to-large (Cohen's d up to 1.11), which made the multiple-comparisons correction step almost anticlimactic — nothing flipped from significant to non-significant, because the sample sizes (hundreds of days per channel, millions of clicks for Fisher's test) gave the tests enormous power.

**How did multiple comparisons correction change your conclusions?**
It didn't change *which* comparisons were significant (12/15 CPA pairs and 15/15 conversion-rate pairs survived both Bonferroni and FDR), but it changed *how I read the p-values*: once I saw that even the ultra-conservative Bonferroni correction couldn't knock anything out, it became clear that p-values had stopped being the interesting number. The real decision-relevant numbers were Cohen's d and the raw percentage/dollar differences — that's what separated "LinkedIn is significantly worse" (true, large effect, act on it) from "Snapchat is significantly different from TikTok" (true, negligible effect, ignore it).

**What are the limitations of this analysis?**
The dataset is explicitly synthetic (per its own documentation), so while the statistical methodology is sound, the specific numbers shouldn't drive a real $500K/month decision without re-running this pipeline on the company's actual data. It also only measures immediate conversions and revenue — it can't see lead quality, sales-cycle length, or brand-awareness value, all of which matter more for channels like LinkedIn. Finally, the power analysis simulation makes simplifying distributional assumptions (normal CPA, fixed relative variance) that a real deployment should sanity-check against the empirical distribution.

**How would you communicate these findings to non-technical stakeholders?**
Lead with the dollar story, not the statistics: "Google Search returns $3.78 for every $1 spent; every other channel loses money." Then show the budget allocation table as the concrete ask. Keep the statistical rigor (t-tests, Fisher's exact, FDR correction, power analysis) in an appendix/caveats section for anyone who wants to check the work, but don't make the CMO wade through p-values to get to the recommendation — that's what the Statistical Caveats section in the memo is for.
