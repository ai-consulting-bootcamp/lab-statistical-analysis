# Reflection

## What surprised me

I expected to be underpowered and to end up with almost nothing surviving correction. The opposite happened. 49 of 55 CPA comparisons survived Bonferroni, and the effect sizes were absurd, Cohen's d between 4 and 7 on the top pairs.

That forced a rethink. An effect size of 7 does not mean the finding is seven times better. It means the two things being compared are not samples from a similar process at all. These campaigns run at stable, widely separated performance levels, so daily variation within a campaign is tiny next to the gaps between campaigns. The t test is answering a question nobody needed to ask.

The second surprise was how much of the answer sat in one row. youtube_blogger produced 11.25M of 12.3M total profit. Every portfolio level number in this analysis is really a statement about one campaign.

## How multiple comparisons correction changed my conclusions

Almost not at all, and that is the interesting part. Bonferroni removed 2 of 49 CPA findings and 6 of 50 ROAS findings. The lab is built on the premise that testing many pairs generates false positives that mislead budget decisions. In this dataset the premise does not bind, because the signal is far too strong relative to the noise.

Where the premise did bind was somewhere the lab did not point. Fisher's exact on pooled clicks returned 46 significant pairs. Running the same comparisons on daily order rates returned 33. Thirteen findings existed only because pooling 28 days of clicks into one contingency table pretends every click is an independent Bernoulli trial and inflates the effective sample size by three orders of magnitude. That is a bigger source of false confidence here than the number of tests, and no correction method would have caught it because the p values were genuinely tiny under the wrong model.

The lesson I take: correcting p values protects against one specific failure. It does nothing about a misspecified test, and nothing at all about the absence of randomisation.

## Limitations

The one that matters most is that this is observational data being used to make a causal recommendation. Nothing was randomised. Last click attribution credits retargeting, branded search and influencer campaigns for demand that prospecting campaigns generated, and those are precisely the campaigns topping my ROAS ranking. I can rank the campaigns honestly. I cannot say what happens if money moves between them, and I said so in the memo rather than burying it.

Beyond that: 28 days in a single month, no seasonal contrast, February 2021 during a pandemic. 19 zero order days dropped from CPA tests, which biases the weak campaigns to look better than they are. Unlabelled currency. And banner_partner reporting 1.07 billion impressions, which is either a different pricing model or an error, and either way makes its CTR meaningless.

The allocation method has its own problem. Ranking discards magnitude, so a campaign returning 0.11 and one returning 0.74 sit next to each other in the ranking, and allocating proportionally to rank assumes returns scale linearly forever. The clearest symptom is that the model wants to grow facebook_retargeting nineteen fold off 108 orders. Retargeting audiences are capped by upstream demand. That number is arithmetic, not strategy.

## Communicating this to non technical stakeholders

I would lead with the money, not the method: 43 percent of spend is going to campaigns that lose money, and one campaign returns eleven cents on the unit. That lands without a single p value.

Then one sentence on confidence: the gaps are large enough that they are not measurement noise, and I would show the confidence interval chart rather than a table of p values, because error bars are intuitive and p values are not.

Then the honest caveat, framed as a decision rather than a disclaimer: this data can tell us which campaigns look good, it cannot tell us what happens when we move money, so the plan is to cut the one obvious loser now and test the rest rather than reshuffle the whole budget on a correlation.

The thing I would not do is present the ranked allocation table as an answer. It looks authoritative, it is arithmetically correct, and treating it as an instruction would be the actual mistake the CMO hired an analyst to prevent.
