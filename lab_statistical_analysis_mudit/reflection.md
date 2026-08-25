# Reflection

**What surprised you about the results?**
That there was essentially nothing there. Going in, I expected at least one campaign type to
show a real CPA or conversion-rate edge — that's usually how these datasets go. Instead, CPA
came back with 0 of 10 pairwise comparisons significant (not even before correction), and every
Cohen's d was under 0.02. The conversion-rate family did show 10 of 10 "significant" comparisons,
but every one was under 1% relative — a clean illustration of how large samples make even trivial
differences statistically detectable, made especially stark here because clicks are aggregated in
the tens of millions per group.

**How did multiple comparisons correction change your conclusions?**
Barely at all, but for a different reason than usual. For CPA, correction was moot — nothing was
significant to begin with. For conversion rate, Bonferroni dropped exactly one pair (Influencer
vs. SEO, p=0.0076) and FDR dropped none. The real filter here wasn't the correction step, it was
checking practical significance (the 10% relative-difference screen) against the p-values —
correction alone would have left a reader thinking "10 of 10 channel pairs differ," which is
technically true and practically misleading.

**What are the limitations of this analysis?**
`Campaign_Type` groups are observational, not from a randomized experiment, so a real difference
elsewhere in how campaigns were run (budget, audience, timing) could in principle be masking a
genuine effect rather than confirming its absence — though a confound is more likely to *create*
a spurious difference than hide one across 55,555 campaigns, so I read this null result as fairly
trustworthy. The bigger limitation is scope: this dataset supports several other groupings
(`Channel_Used`, `Target_Audience`, `Customer_Segment`, `Duration`) that weren't tested here and
might show a real signal `Campaign_Type` averages over. Power analysis also relied on a normal
(CPA) / binomial (conversion rate) simulation model rather than the real, right-skewed CPA
distribution.

**How would you communicate these findings to non-technical stakeholders?**
Lead with the finding, not an apology for it: "we checked, and there's no meaningful cost or
conversion-rate difference between your five campaign types — so there's no statistical reason
to shift budget between them." Frame the power analysis result concretely — "we have 37x more
data than we'd need to catch even a small (5%) real difference, so this isn't a case of
'not enough data to tell'; there genuinely isn't a gap to find here." Then point stakeholders at
the next place to look (channel/platform, audience segment) rather than leaving them with a dead
end. A null result is still an actionable answer — it says "stop looking here, look there."
