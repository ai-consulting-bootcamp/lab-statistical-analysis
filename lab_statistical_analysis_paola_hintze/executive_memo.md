# Executive Memo — Marketing Channel Budget Allocation

**Date:** 24 August 2026  
**Analyst:** Paola Hintze  
**Decision:** Allocation of a fictional $500K monthly marketing test budget  
**Dataset:** Solstice SaaS Growth Pack, VectorFlow channel performance  
**Period:** 1 January–31 March 2026 (90 days)

## Executive summary

Under this synthetic 90-day scenario, Referral is the strongest channel: 2.69% click-to-conversion, $84 aggregate CPA, 3.38x ROAS, and $23.7K attributed profit. Content is effectively break-even at 0.99x ROAS; the remaining channels are below 1.0x. After controlling the false discovery rate, Referral's advantage over Paid Search and SEO remains statistically supported. I recommend a guardrailed reallocation toward Referral and Content while retaining minimum budgets in every channel to test whether performance holds at higher spend.

## Key findings

The dataset contains 630 daily channel records, 90 per channel. Across 21 CPA comparisons, 15 were significant without correction, 11 under Bonferroni, and 14 under BH-FDR. Across 21 Fisher conversion-rate comparisons, the counts were 14, 10, and 14. Referral's conditional daily CPA was 70.6% below Paid Search (BH-adjusted `p=4.50×10⁻²⁴`, large `|d|=3.46`), while its conversion rate was 2.69% versus 1.34% (adjusted `p=.000245`). Referral versus Content conversion rate was not statistically distinguishable after BH (`p=.139`), so Content remains a credible scale-test candidate.

The power model indicates that 90 days are sufficient for differences of 10% or larger under the lab's normal/15%-SD assumptions, but power is only 62.2% for a 5% difference. A 5% effect needs 180 tested days to exceed 80% power in the prescribed grid. Actual CPA inference is weaker for sparse channels: Outbound Sales has only three conversion-positive days.

## Recommended monthly test allocation

| Channel | Amount | Share |
|---|---:|---:|
| Referral | $106,250 | 21.25% |
| Content | $94,643 | 18.93% |
| SEO | $83,036 | 16.61% |
| Paid Search | $71,429 | 14.29% |
| Partnerships | $59,821 | 11.96% |
| LinkedIn Ads | $48,214 | 9.64% |
| Outbound Sales | $36,607 | 7.32% |
| **Total** | **$500,000** | **100.00%** |

This allocation weights aggregate CPA and ROAS at 35% each, conversion rate at 20%, and profit margin at 10%, then applies a 5% floor and 25% cap. Treat it as a staged experiment: increase weekly, monitor marginal rather than average returns, and require attribution and lead-quality checks before releasing the next tranche.

## Statistical caveats

The public Hugging Face source is explicitly synthetic, so results validate the method—not a real market opportunity. Attributed revenue is not incremental revenue, and pairwise tests do not establish causality. Daily CPA is undefined on zero-conversion days; its t-tests and bootstrap intervals describe conversion-positive days and can flatter sparse channels. Fisher tests aggregate across dates and do not model seasonality or repeated-day dependence. BH controls expected false-discovery proportion, not the truth of each retained claim. Finally, scaling budget may change auction prices, audience mix, saturation, and conversion quality.

## Next steps

1. Run a four-week controlled ramp with weekly guardrails and channel-level holdouts where feasible.
2. Reconcile attributed revenue to CRM-qualified pipeline and contribution margin.
3. Review marginal CPA/ROAS and lead quality weekly; stop increases that breach pre-agreed thresholds.
4. Collect 90 additional days before making decisions on differences near 5%.
5. Re-estimate the allocation using observed incremental lift rather than attributed averages.

