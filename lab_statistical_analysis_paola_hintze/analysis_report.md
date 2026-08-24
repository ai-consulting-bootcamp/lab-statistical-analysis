# Statistical Analysis Report

## 1. Data and hypotheses

The analysis covers seven VectorFlow channels over 90 days (630 rows). The primary continuous comparison is daily CPA conditional on at least one conversion; pairwise differences use two-sided independent Welch t-tests because variance and usable sample sizes differ. Cohen's d uses the lab-specified average-variance denominator and is reported with every comparison. Click-to-conversion rates use two-sided Fisher exact tests on aggregated conversion/non-conversion counts.

These tests answer association questions, not causal incrementality. Daily channel observations share the same calendar and the source is synthetic; neither test controls for time-varying demand, attribution overlap, or auction response to higher spend.

## 2. Group performance

| Channel | Cost | Revenue | Conversions | Conversion rate | Aggregate CPA | ROAS | Profit |
|---|---:|---:|---:|---:|---:|---:|---:|
| Referral | $9,959.68 | $33,645.23 | 118 | 2.69% | $84.40 | 3.38x | $23,685.55 |
| Content | $12,866.76 | $12,753.46 | 43 | 2.00% | $299.23 | 0.99x | -$113.30 |
| SEO | $12,151.94 | $8,895.13 | 32 | 1.51% | $379.75 | 0.73x | -$3,256.81 |
| Paid Search | $17,035.68 | $11,355.02 | 39 | 1.34% | $436.81 | 0.67x | -$5,680.66 |
| Partnerships | $8,577.86 | $2,689.40 | 9 | 0.57% | $953.10 | 0.31x | -$5,888.46 |
| LinkedIn Ads | $10,410.65 | $1,750.76 | 6 | 0.42% | $1,735.11 | 0.17x | -$8,659.89 |
| Outbound Sales | $11,357.12 | $802.47 | 3 | 0.23% | $3,785.71 | 0.07x | -$10,554.65 |

Referral leads every principal efficiency/outcome metric and is the only materially profitable channel in this attributed snapshot. Content is approximately break-even. The other five channels have ROAS below 1.0, but attribution and marginal returns are unknown, so “loss-making” does not prove their incremental value is zero.

## 3. CPA Welch tests and effect sizes

There are 21 channel pairs. At α=.05, 15 are significant without correction, 11 after Bonferroni, and 14 after Benjamini–Hochberg (BH) FDR correction. The Outbound Sales–Partnerships comparison loses significance after BH (`p=.0397`, adjusted `p=.0555`), illustrating why uncorrected screening would overstate evidence.

Key FDR-retained comparisons:

- Referral's conditional daily CPA is 60.1% lower than Content (`$78.00` vs `$195.45`; adjusted `p=5.74×10⁻²²`; `d=-2.49`, large).
- Referral is 70.6% lower than Paid Search (`$78.00` vs `$265.74`; adjusted `p=4.50×10⁻²⁴`; `d=-3.46`, large).
- Referral is lower than SEO (`$78.00` vs `$199.32`; adjusted `p=4.03×10⁻²⁰`; `d=2.72` in the table's B-minus-A orientation, large).
- Content is 36.0% lower than Paid Search (`$195.45` vs `$265.74`; adjusted `p=2.85×10⁻⁷`; `d=1.32`, large).

The direction and magnitude of Cohen's d depend on table ordering; practical interpretation uses absolute magnitude and the group means. Because CPA excludes zero-conversion days, low-conversion channels can appear artificially inexpensive on the few successful days. Their aggregate CPA correctly exposes the full spend burden.

## 4. Fisher exact tests

The 21 Fisher tests yield 14 significant comparisons before correction, 10 after Bonferroni, and 14 after BH. Key results include:

- Referral converts 2.69% of clicks versus Paid Search's 1.34% (difference 1.35 percentage points; adjusted `p=.000245`).
- Referral converts 2.69% versus SEO's 1.51% (difference 1.19 points; adjusted `p=.00501`).
- Referral versus Content (2.69% vs 2.00%) does **not** survive BH (`adjusted p=.139`), so their rate ordering should not be described as a reliable difference.
- Outbound Sales (0.23%) and LinkedIn Ads (0.42%) are each significantly below several stronger channels, but not significantly different from one another (`adjusted p=.566`).

Fisher's test avoids unreliable normal approximations for sparse conversion counts. Its aggregation nevertheless ignores day-level dependence and changing traffic mix.

## 5. Multiple comparisons

Across both families, 42 hypotheses create **2.10 expected false positives** at an uncorrected 5% threshold if all nulls were true. Corrections are applied within each coherent 21-test family. Bonferroni controls the probability of any false positive but is conservative. BH controls the expected proportion of false discoveries and is the primary screening rule here because the CMO needs to identify several candidates while limiting false discovery. Borderline BH-only results are not used as sole reasons for budget shifts.

| Test family | Uncorrected | Bonferroni | BH-FDR |
|---|---:|---:|---:|
| Daily CPA | 15 | 11 | 14 |
| Conversion rate | 14 | 10 | 14 |

The reduction in discoveries cannot identify a specific result as a “false positive”; it shows which claims are not robust to the selected error-control policy.

## 6. Power and confidence intervals

Under the lab's simulation assumptions (normal CPA, SD = 15% of baseline, two-sided Welch test, 1,000 simulations), 90 days provide estimated power of 62.2% for a 5% CPA difference, 99.3% for 10%, and approximately 100% for 15–20%. Among the tested sample sizes, a 5% difference requires 180 days for ≥80% power; 10% requires 60 days; 15–20% require 30 days.

These power values are scenario-model outputs, not empirical guarantees. The actual daily CPA data are sparse, conditional, skewed, and have unequal usable sample counts. In particular, Outbound Sales has only three conversion-positive days, so its bootstrap interval and effect estimates are fragile even where the lab's simplified power model looks high.

Selected 95% bootstrap CIs for mean conditional daily CPA:

- Referral: $77.997 [67.834, 88.597], 81 positive days.
- Content: $195.452 [182.066, 209.165], 43 days.
- Paid Search: $265.736 [247.486, 284.147], 39 days.
- Outbound Sales: $230.667 [211.300, 254.390], only 3 days.

## 7. $500K budget recommendation

The proposed allocation is a **monthly test budget**, not a permanent optimum. A composite rank uses aggregate CPA (35%), ROAS (35%), conversion rate (20%), and profit margin (10%). Allocation is proportional to points with a 5% floor and 25% cap per channel to preserve learning and limit extrapolation beyond the observed spend range.

| Channel | Budget | Share | Change vs historical share |
|---|---:|---:|---:|
| Referral | $106,250 | 21.25% | +9.16 pp |
| Content | $94,643 | 18.93% | +3.31 pp |
| SEO | $83,036 | 16.61% | +1.85 pp |
| Paid Search | $71,429 | 14.29% | −6.40 pp |
| Partnerships | $59,821 | 11.96% | +1.55 pp |
| LinkedIn Ads | $48,214 | 9.64% | −3.00 pp |
| Outbound Sales | $36,607 | 7.32% | −6.47 pp |
| **Total** | **$500,000** | **100.00%** | — |

The increase for Partnerships despite weak absolute performance comes from the universal learning floor and normalization after larger cuts elsewhere; it is not a claim that Partnerships outperforms Paid Search. Weekly spend ramps should be capped, with holdouts or geo/time experiments where possible. Pause escalation if marginal ROAS deteriorates, lead quality falls, or attribution reconciliation fails.

