# Campaign performance and monthly budget recommendation

**To** Chief Marketing Officer  
**From** Sergii Rostovskyi, Marketing Analyst  
**Date** 23 November 2026  
**Dataset** Criteo Attribution Modeling for Bidding Dataset  
**Period** 30 complete relative days, from day 0 through day 29

## Executive summary

Keep $450,000 in the existing monthly allocation and authorize a controlled $50,000 pilot. Campaign 10341182 is the first candidate because it combines the highest conversion volume with the second-lowest aggregate CPA. Campaign 30801593 is the efficiency candidate, and 15184511 is the post-click conversion candidate. The source covers seven campaigns within display advertising and reports transformed costs. A reallocation across seven real channels requires the company's own cost and revenue data and a test of incremental conversion lift.

## Key findings

| Campaign | Credited conversions | Post-click CVR | Aggregate CPA | Mean daily CPA | 95% CI for mean daily CPA |
| --- | ---: | ---: | ---: | ---: | --- |
| 10341182 | 11,157 | 5.92% | 0.01207 | 0.01228 | 0.01156–0.01295 |
| 30801593 | 4,799 | 2.91% | 0.00522 | 0.00512 | 0.00450–0.00578 |
| 15184511 | 8,872 | 9.77% | 0.01683 | 0.01713 | 0.01618–0.01801 |
| 29427842 | 3,147 | 4.09% | 0.04061 | 0.04115 | 0.03814–0.04403 |
| 17686799 | 2,643 | 2.41% | 0.02915 | 0.02943 | 0.02788–0.03115 |
| 15398570 | 3,251 | 2.50% | 0.04615 | 0.04763 | 0.04406–0.05128 |
| 5061834 | 1,265 | 1.51% | 0.10934 | 0.11108 | 0.10406–0.11866 |

CPA is expressed in transformed cost units. One observation in the primary two-sided Welch comparison is one campaign-day ratio (that day's transformed display cost divided by its credited conversions), and each day has equal weight in the daily mean. Aggregate CPA is total transformed cost divided by total credited conversions, so days with more credited conversions carry more weight. Campaign 10341182 also led in CTR at 44.40% within the sampled log.

- **Efficiency.** Campaign 30801593's mean daily CPA was 0.00716 units lower than campaign 10341182's, a 58.3% difference relative to 10341182. The BH-adjusted Welch p-value was 9.85 × 10⁻²¹ and Cohen's d for 30801593 minus 10341182 was −3.80. Campaign 30801593 also had the highest relative day-to-day CPA variability (35.2%), which supports a measured spend increase.
- **Conversion.** Campaign 15184511 had a 3.86 percentage point lead over 10341182 on pooled post-click CVR (Fisher BH-adjusted p ≈ 3.87 × 10⁻²⁸⁶). Against 15398570, campaign 30801593 had a statistically detectable 0.41 percentage point lift, below the pilot's illustrative 0.50 point threshold.
- **Multiplicity.** For daily CPA, 21 of 21 pairs met the raw and BH thresholds, and 20 met Bonferroni. The exception was 29427842 versus 15398570, with 13.6% lower mean daily CPA for 29427842, |d| = 0.70, BH-adjusted p = 0.0090, and Bonferroni-adjusted p = 0.188. All three CVR approaches agreed on the BH decisions. Twenty of 21 pairs remained significant in each approach, with 15398570 versus 17686799 the exception. The CPA exception and small CVR gaps are weak bases for budget shifts.
- **Data adequacy.** The 30 observed campaign-days per arm gave 24.2%, 72.4%, 97.3%, and 100.0% empirical power at CPA gaps of 5%, 10%, 15%, and 20%, respectively. The 80% minimums from the equal-variance noncentral-*t* reference model are 143, 37, 17, and 10 days per arm. Empirical power simulated at those reference sizes was 80.5%, 81.1%, 80.7%, and 79.7%; the 20% result is below 80% as calculated. The 90-day column is a hypothetical planning scenario, not observed data: its empirical powers are 60.8%, 99.5%, 100.0%, and 100.0%. For a 10% gap, the reference-model requirement rises from 37 to 71 days with the Bonferroni threshold and to 253 days with the 40% variability assumption at nominal alpha. This sensitivity matters because observed daily CPA variation ranged from 15.3% to 35.2%.

Across 21 BH-significant CPA pairs, empirical power at the 30 observed days ranged from 98.25% to 100.0% conditional on the observed effect estimates. At the reference-model minimum days per pair (2 to 16), empirical estimates ranged from 72.2% to 100.0%; four pair assessments were below 80% as calculated. These selected-from-the-data effects make the conditional estimates optimistic for replication. Review [pairwise findings](tables/significant_findings.csv), [CPA intervals](tables/cpa_confidence_intervals.csv), [sample-size estimates](tables/power_sample_size.csv), [per-pair power assessments](tables/power_current_pairs.csv), [power curves](tables/power_curves.csv), and the [power figure](figures/power_analysis_cpa.png).

## Recommended monthly budget

| Allocation | Amount | Share of total | Proposed role |
| --- | ---: | ---: | --- |
| 10341182 | $9,638 | 1.93% | First scaling candidate |
| 30801593 | $9,406 | 1.88% | Test whether low CPA persists as spend increases |
| 15184511 | $9,058 | 1.81% | Test whether higher CVR yields incremental value |
| 29427842 | $6,563 | 1.31% | Secondary conversion candidate |
| 17686799 | $6,214 | 1.24% | Secondary efficiency candidate |
| 15398570 | $5,460 | 1.09% | Limited learning allocation |
| 5061834 | $3,661 | 0.73% | Small validation allocation |
| Existing allocation / reserve | $450,000 | 90.00% | Preserve existing spending while the pilot runs |
| **Total** | **$500,000** | **100.00%** | |

The pilot score weights aggregate CPA 60%, post-click CVR 25%, and conversion volume 15%. Larger scores indicate stronger performance on these criteria. Each campaign receives a 5% pilot floor. The remainder follows the scores, with a 25% cap that the allocation does not reach. Dollar allocations are an illustrative decision rule for the assignment. The publisher's transformed costs cannot predict dollar savings or marginal return at a larger budget.

## Statistical caveats

- Historical impressions and clicks were observed under different delivery, targeting, audience, and auction conditions. Attribution identifies credited outcomes in the sampled data. Incremental lift requires a randomized comparison.
- Fisher's test pools clicks, including potential repeat users. Welch and paired daily tests address different questions and can still be affected by autocorrelation, common shocks, and campaign selection. The correction counts show how decisions change under each rule. The actual number of false discoveries is unknown.
- The mean-CPA intervals are individual percentile-bootstrap intervals. The aggregate-CPA intervals also preserve adjacent days through a seven-day moving-block bootstrap. Thirty days provide few independent blocks, so both estimates describe uncertainty within the available window.
- No sales revenue or contribution margin is available. ROAS, profit, and profit margin remain unmeasured. The 10% CPA and 0.50 percentage point CVR thresholds are illustrative until finance has converted the company's unit economics into decision thresholds.
- Power planning assumes independent days, shared SD of 15% of baseline CPA, symmetric clipping around each simulated arm's mean with a shared half-width of 50% of baseline CPA, two-sided Welch tests, and stable delivery. The symmetric clipping rule is the chosen interpretation of the assignment's ambiguous “cap at 50% of base.” The 80% minimum sample sizes are analytical equal-variance noncentral-*t* reference estimates; empirical power at those sample sizes is shown separately and can fall below 80%. Power at observed pairwise effects is conditional on the model and offers limited evidence about replication because effects were selected from the same data.

## Next steps

Run the pilot with randomized, mutually exclusive audiences and a holdout. Log actual spend, deduplicated conversions, revenue, margin, and exposure by experimental arm. Pre-register one primary CPA comparison and calibrate the minimum economically worthwhile effect and sample size from fresh in-market data. Define the conversion lag and contribution margin guardrail before setting the test duration. Review the pilot once the planned sample and conversion window are complete, and release reserve funds only when incremental CPA and margin meet the agreed thresholds.
