# Marketing channel performance: allocation recommendation

**To:** CMO
**From:** Gordan, Marketing Analytics
**Date:** 25 August 2026
**Dataset:** "Digital Marketing Metrics & KPIs to Measure" (sinderpreet, Kaggle), https://www.kaggle.com/datasets/sinderpreet/analyze-the-marketing-spending
**Period analysed:** 1 to 28 February 2021, 11 campaigns across 4 categories, 308 campaign days

---

## Executive summary

Roughly 43 percent of current spend goes to campaigns that return less than one unit of revenue per unit of cost. Over the 28 day window those campaigns lost about 4.9M in revenue terms, against a portfolio that was profitable overall at a blended ROAS of 1.40.

The performance gaps between campaigns are large and statistically unambiguous. 49 of 55 campaign pairs differ significantly on cost per acquisition even after Bonferroni correction, with effect sizes far beyond conventional thresholds. Statistical significance is not the constraint here.

The constraint is causal. This data is observational. Nothing in it was randomised, so it can rank campaigns but cannot tell us what happens if we move money between them. The recommendation below should be read as a prioritised test plan with a first tranche of budget attached, not as an optimisation result.

---

## Key findings

### 1. Performance is highly dispersed

| Campaign | ROAS | CPA | Profit contribution |
|---|---|---|---|
| youtube_blogger | 3.77 | 2,120 | +11.25M |
| facebook_retargeting | 2.01 | 2,467 | +0.27M |
| google_hot | 1.84 | 4,270 | +1.01M |
| instagram_tier1 | 1.77 | 3,384 | +1.98M |
| instagram_blogger | 1.37 | 3,861 | +1.56M |
| banner_partner | 1.22 | 3,210 | +1.13M |
| facebook_tier1 | 0.93 | 5,411 | -0.17M |
| facebook_tier2 | 0.74 | 6,822 | -1.23M |
| google_wide | 0.66 | 4,132 | -0.76M |
| instagram_tier2 | 0.63 | 3,406 | -0.40M |
| facebook_lal | 0.11 | 8,986 | -2.34M |

One campaign, youtube_blogger, produced 11.25M of the 12.3M total profit. The portfolio result depends almost entirely on it.

### 2. The differences are statistically solid, which is less useful than it sounds

Pairwise Welch t tests on daily CPA gave 49 of 55 pairs significant at the uncorrected 0.05 level, 47 surviving Bonferroni at 0.00091, and 49 surviving Benjamini and Hochberg FDR. Cohen's d for the top comparisons runs between 4 and 7.

An effect size of 7 is not a normal research finding. It tells us these campaigns are structurally different things with stable, separated performance levels, not noisy replicates of one process. When almost every comparison is significant, the hypothesis tests stop discriminating and the decision has to rest on effect magnitude and business logic instead.

Note the consequence for the lab premise: multiple comparisons correction changed almost nothing here. It removed 2 of 49 CPA findings. The false positive risk this exercise was designed to control is not the binding risk in this dataset.

### 3. One statistical result should be discounted

Fisher's exact test on pooled clicks found 46 of 55 pairs significantly different on order rate. That number is inflated. Pooling 28 days of clicks into a single 2 by 2 table assumes every click is an independent draw at a fixed campaign rate, which ignores day to day variation in conversion. Testing the same pairs on 28 daily order rates instead drops the count to 33. Thirteen pairs are called significant by the pooled test and not by the test that respects daily structure. Those 13 should not be treated as findings.

### 4. Data adequacy

Simulation using the measured coefficient of variation of daily CPA (0.144, verified from the data rather than assumed) gives the following:

| True CPA difference | Power at 28 days | Days needed for 80 percent power |
|---|---|---|
| 5 percent | 0.25 | 135 |
| 10 percent | 0.73 | 35 |
| 15 percent | 0.97 | 20 |
| 20 percent | 1.00 | 10 |

The smallest CPA difference reliably detectable with 28 days is about 11 percent. Only one FDR significant pair (google_hot versus instagram_blogger, a 10.1 percent gap) sits below 80 percent power and should be treated as provisional.

This result is sensitive to variability. At a coefficient of variation of 0.30, power to detect a 10 percent difference falls from 0.73 to 0.25. Campaigns with volatile daily performance, particularly facebook_retargeting at 0.365, are measured less precisely than the table above implies.

---

## Recommendation

Two allocations of the 500K monthly budget are in `outputs/budget_allocation.csv`. I recommend option B, which applies a break even screen before ranking.

| Campaign | Current share | Recommended share | Monthly budget | Change |
|---|---|---|---|---|
| youtube_blogger | 13.3% | 18.9% | 94,444 | +5.6 pp |
| facebook_retargeting | 0.9% | 17.2% | 85,859 | +16.3 pp |
| instagram_tier1 | 8.4% | 13.7% | 68,687 | +5.4 pp |
| banner_partner | 16.4% | 12.9% | 64,394 | -3.6 pp |
| google_hot | 3.9% | 11.2% | 55,808 | +7.2 pp |
| instagram_blogger | 13.9% | 11.2% | 55,808 | -2.7 pp |
| facebook_tier1 | 8.4% | 3.0% | 15,000 | -5.4 pp |
| facebook_tier2 | 15.3% | 3.0% | 15,000 | -12.3 pp |
| google_wide | 7.4% | 3.0% | 15,000 | -4.4 pp |
| instagram_tier2 | 3.5% | 3.0% | 15,000 | -0.5 pp |
| facebook_lal | 8.6% | 3.0% | 15,000 | -5.6 pp |

The 3 percent floor is deliberate. Cutting a campaign to zero destroys the measurement that would tell us whether the cut was right.

**The single most defensible action** is reducing facebook_lal. At a ROAS of 0.11 it returns eleven cents per unit spent and accounts for 2.34M of losses in 28 days. No plausible attribution correction rescues that number.

**The least defensible line in the table** is facebook_retargeting. The model wants to raise it from 0.9 percent of spend to 17.2 percent, a nineteen fold increase, on the basis of 29,954 clicks and 108 orders. Retargeting pools are capped by the size of the audience upstream campaigns generate. Scaling it that far almost certainly cannot happen, and if it did the marginal ROAS would not resemble the current one. Treat this as a signal to test incremental increases, not as a budget instruction.

---

## Statistical caveats

**Observational data, causal recommendation.** Spend was not randomly assigned. Last click attribution systematically credits harvesting channels (retargeting, branded search, influencer) for demand that prospecting channels created. The two influencer campaigns and the retargeting campaign are the top three on ROAS, which is exactly the pattern attribution bias produces. Moving budget out of prospecting into harvesting can shrink the pool that makes harvesting profitable.

**Short window.** 28 days in February 2021, a single month with no seasonal contrast, during a pandemic period with atypical e commerce behaviour. There is no way to separate campaign effects from month specific effects.

**Excluded observations.** 19 of 308 campaign days had zero orders and therefore undefined CPA. They are excluded from CPA tests. Because those days are disproportionately from the weaker campaigns, this biases their measured CPA downward, making the gaps in this memo conservative rather than exaggerated.

**Confidence intervals.** Bootstrap 95 percent intervals on daily CPA are 8 to 15 percent wide relative to the mean for most campaigns. Only 7 of 55 pairs have overlapping CPA intervals. Full table in `outputs/bootstrap_ci_cpa.csv`.

**Ranking method limits.** The composite score converts CPA and ROAS to ranks, which discards magnitude. facebook_lal and facebook_tier2 rank adjacently, but one returns 0.11 and the other 0.74. The allocation is also proportional to score, which implicitly assumes constant returns to scale. No channel behaves that way past a point.

**Measurement anomaly.** banner_partner reports 1.07 billion impressions in 28 days, roughly fifteen times the next highest campaign. Its CTR is therefore not comparable to the others and should not be read as poor creative performance.

**Currency.** The source file does not label its currency. Figures are treated as generic units and mapped to the 500K brief as proportions.

---

## Next steps

1. Cut facebook_lal to the 3 percent floor immediately. This is the one move with a large enough margin to survive any reasonable attribution correction.
2. Run a geo holdout or a spend down test on facebook_tier2 and google_wide before reallocating their combined 22.7 percent of budget. Their negative return may be an attribution artefact.
3. Raise facebook_retargeting in steps of roughly 50 percent per month with ROAS measured at each step, rather than executing the full increase the model proposes.
4. Extend the measurement window to at least 90 days. That takes the detectable CPA difference from about 11 percent down to under 6 percent and allows day of week and seasonal controls.
5. Instrument incrementality properly. Everything in this memo is correlational, and a single incrementality test on the top spending campaign would be worth more than another month of this analysis.
