# Executive Memo

**LAB | In God we trust, everyone else bring the data** &mdash; Step 8
**Author:** Nnanyelugo Ahukannah

---

**TO:** VP Growth
**FROM:** Nnanyelugo Ahukannah
**DATE:** 24 August 2026
**SUBJECT:** Campaign performance comparison &mdash; where the differences are real, and what they are worth

---

## Executive summary

We compared the six highest-volume campaigns in 400,000 impressions of live
ad-serving data. Conversion rates differ by a factor of four &mdash; 2.0% to 8.3%
&mdash; and those gaps survive every statistical check we applied. Cost
differences also test as significant, but most of them are too small to matter.
**The recommendation is to shift budget toward two campaigns and to test rather
than assume the gain transfers**, for a reason set out under Caveats that should
be read before the budget table.

## What we measured

Six campaigns, 68,273 impressions between them, from Criteo's published
attribution dataset. Two families of comparison across all 15 campaign pairs:
conversion rate, tested with Fisher's exact test, and cost per impression, tested
with Welch's t-test. Every p-value was corrected for multiplicity twice, by
Bonferroni and by Benjamini-Hochberg, and every difference carries an effect size
alongside it.

Cost figures are in Criteo's anonymised units, not currency. Ratios between
campaigns are meaningful; the absolute numbers are not money.

## Results

| Campaign | Impressions | Conversion rate | 95% interval | CPA (cost units) |
|---|---:|---:|---|---:|
| B | 14,802 | **8.28%** | 7.85&ndash;8.74% | 0.0031 |
| E | 6,071 | 7.69% | 7.05&ndash;8.39% | 0.0039 |
| F | 5,808 | 4.68% | 4.17&ndash;5.26% | 0.0046 |
| A | 21,680 | 3.76% | 3.52&ndash;4.03% | **0.0018** |
| D | 9,755 | 2.36% | 2.07&ndash;2.68% | 0.0201 |
| C | 10,157 | 2.04% | 1.78&ndash;2.33% | 0.0098 |

**Thirteen of fifteen** conversion comparisons are significant after correction.
The two that are not are worth as much as the ones that are: **B and E are
statistically indistinguishable** (p=0.16), as are **C and D** (p=0.13). We have
two strong campaigns and two weak ones, not a clean ranking of six.

**Cost tells a different story.** Fourteen of fifteen cost comparisons are
significant, but **six of those fourteen have a negligible effect size**. At
6,000&ndash;22,000 impressions per campaign, a difference far too small to act on
still clears p&lt;0.05 comfortably. The largest effect we found is
Campaign A against Campaign D (Cohen's d = 0.73, medium), and that is the one
cost difference the numbers genuinely support.

The eleven-fold CPA spread is driven by conversion rate, not by media price.
Campaign A is the cheapest per acquisition despite a middling conversion rate,
because its cost per impression is the lowest in the set.

## Caveats

**This is observational data, not an experiment.** Campaigns were not randomly
assigned to audiences; they run for different advertisers, products and targeting.
A campaign that converts at 8.3% may do so because of who it reaches, not because
of anything transferable. Nothing here establishes that moving budget into
Campaign B would produce Campaign B's conversion rate on the traffic you moved.

**Correction changed nothing here, and that is not evidence it was unnecessary.**
At this sample size the p-values are effectively zero, so Bonferroni and
Benjamini-Hochberg withdrew no results. Repeating the same tests on a realistic
pilot-sized sample &mdash; 400 impressions per campaign &mdash; Bonferroni
withdrew three of seven apparently significant findings. The correction matters
whenever you are near the threshold, which is where most real decisions sit.

**Scope.** One 30-day window, one ad network, the six largest campaigns only,
and a cost column we cannot convert to currency. ROAS is not computable from this
source at all &mdash; the release carries no revenue field &mdash; so the ROAS
figures in the exploration output come from a separate, clearly-labelled
**synthetic** dataset and support no recommendation.

## Recommendation

**Shift budget toward Campaigns B and E, and treat the shift as a test rather
than a conclusion.** Both convert around four times better than C and D, the gap
is far outside the confidence intervals, and B is only the fourth cheapest per
impression &mdash; so the advantage is conversion quality, not cheap media.

| Campaign | Current share of impressions | Suggested direction | Confidence |
|---|---:|---|---|
| B | 21.7% | increase | high &mdash; best conversion rate, large sample |
| E | 8.9% | increase | moderate &mdash; matches B, but on a third of the volume |
| A | 31.8% | hold | high &mdash; cheapest acquisition in the set |
| F | 8.5% | hold | moderate |
| C | 14.9% | reduce | high &mdash; worst conversion rate |
| D | 14.3% | reduce | high &mdash; worst CPA, 11x Campaign A |

Move a bounded share &mdash; 10 to 15% of C and D's budget &mdash; and measure.
Do not reallocate wholesale on the strength of an observational comparison.

## Sizing the next test

If the reallocation is run as a proper experiment, the planning numbers are
already computed. Against the pooled 4.71% baseline, at 80% power and a
Bonferroni-corrected threshold for a six-arm comparison:

| Lift you want to detect | Impressions per arm |
|---|---:|
| +50% | 2,821 |
| +30% | 7,285 |
| +20% | 15,751 |
| +10% | 60,375 |

Anything under a 20% relative lift needs more volume per arm than four of the six
campaigns currently receive in a month. **If the goal is to detect a 10%
improvement, this is not a two-week test.**
