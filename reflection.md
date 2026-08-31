# Reflection

## What statistics added to my marketing analysis

The marketing KPIs already gave me a first view of performance.

One-to-one had the highest conversion volume and lowest CPA. Exact was less efficient but remained relatively close. Phrase had the highest CPA and weakest ROAS and ROI.

The statistical analysis helped me go one step further: **were these differences consistent enough to support the initial performance analysis, or could they simply be variation in the data?**

## A significant result is not always an important result

This was one of the most useful lessons from the analysis.

The campaign had more than 924,000 clicks. With that amount of data, even small differences in conversion rate can be statistically significant.

That does not necessarily mean they are important enough to change a marketing decision.

In this case, the differences in conversion rate were statistically significant, but their size was very small. I would therefore not move budget based on the p value alone.

I would also consider CPA, ROAS, ROI, conversion volume and the commercial impact of the difference.

## CPA gave stronger evidence

The CPA analysis supported what I could already see in the campaign performance.

One-to-one had a lower CPA than both Exact and Phrase. After FDR correction, both differences remained statistically significant. The stricter Bonferroni correction retained only the difference against Phrase.

But the size of those differences also mattered.

The advantage over Exact was relatively small, while the advantage over Phrase was larger.

That gave me a more useful conclusion than simply saying that One-to-one performed better. **The data also showed where that advantage was stronger and where the difference was less clear.**

## Checking the data came first

Before running the statistical analysis, I checked whether the marketing metrics provided in the dataset were consistent.

The published conversion rate did not match `Conversions / Clicks` in 160 of 190 records.

I therefore recalculated the KPIs from impressions, clicks, conversions, cost and revenue before using them in the analysis.

This reinforced something simple but important: **a sophisticated analysis does not help if the metrics behind it are wrong.**

## Statistics supported the decision, they did not make it

My final recommendation was:

| Match type | Action | Why |
|---|---|---|
| One-to-one | Maintain | Strongest volume and acquisition efficiency |
| Exact | Optimise and test | Performance remains relatively close and there is room to improve |
| Phrase | Reduce | Highest CPA and weakest return |

I would not automatically move more budget to One-to-one just because it was the strongest group.

All three match types still had negative historical ROI. The better decision is to protect the strongest area, improve the areas with potential and reduce exposure where the economics are weakest.

The statistics gave me stronger evidence for that recommendation, but the decision still required marketing and commercial judgement.

## What I would test next

The analysis uses historical campaign data. It can show differences in performance, but it cannot prove what caused them.

The next step would be a controlled A/B test.

I would test one variable at a time, such as the creative or landing page. I would randomly divide eligible traffic between a control and a new version, choose the main KPI before starting and calculate how much data the test needs.

I would then let the test reach the planned sample before making a decision.

I would only recommend moving additional budget if the new version produced an improvement that was both statistically supported and large enough to matter commercially.

## Main takeaway

**Marketing KPIs show me what is happening. Statistical analysis helps me understand how much confidence I can place in the differences I see.**

For me, that is the practical value of adding statistics to marketing analysis.
