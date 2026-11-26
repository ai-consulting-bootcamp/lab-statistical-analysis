# Memo: Reallocating the $500K monthly paid-media budget

| | |
|---|---|
| **To** | CMO |
| **From** | Ben Mayer, Marketing Analytics |
| **Date** | 26 November 2026 |
| **Dataset** | *Digital Marketing Performance Dataset* (alinaboulsi, [Kaggle](https://www.kaggle.com/datasets/alinaboulsi/digital-marketing-performance-dataset); loaded from the [Hugging Face mirror](https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset), revision `aaa929a`) |
| **Scope** | 5,453 Sales-objective ad-days on 6 platforms, aggregated to 926 platform-weeks |
| **Period** | 2 Jan 2023 to 28 Dec 2025 (154 to 156 complete weeks per platform; Google Display 148) |

> **Read this first.** The dataset is synthetic: it was generated from industry benchmark ranges, and its own README says not to use it for real budget decisions. The method and the direction of each finding carry over to our own data. The dollar figures don't. Treat this memo as the plan we would run on our ad-platform exports.

---

## Executive summary

1. **Google Search is the clear winner on every metric.** It acquires a customer for $5.31, against $25 to $31 on social and $432 on LinkedIn, and returns $16.73 per $1. Every comparison involving Search survives multiple-comparisons correction with very large effect sizes (Cohen's d 2.7 to 3.2).
2. **LinkedIn loses money.** ROAS is 0.44, so each $1 spent returns $0.44. It takes about 20% of current spend.
3. **Meta is a clear #2.** TikTok's and Snapchat's weekly CPAs run 21% and 28% above Meta's (medium effect, d ≈ 0.5 to 0.6, significant after correction).
4. **TikTok and Snapchat are tied on CPA.** The gap (about 5%) is not significant (FDR-adjusted p = 0.20), and the data cannot rank them.
5. **Recommendation:** move about $74K a month out of LinkedIn and spread it across Search, Meta, Snapchat and TikTok (table below). At historical CPAs that would mean up to +24% conversions. That figure is an upper bound: Search will get more expensive as we scale it.
6. **Warning on the review cadence:** with the noise in our weekly numbers, a quarterly (13-week) review can only reliably detect (80% power) CPA gaps of about 45% or more between channels. The Meta-vs-TikTok gap is real but invisible in one quarter.

---

## Key findings

### 1. Channel performance (Sales campaigns, whole period)

| Channel | CPA | 95% CI, mean weekly CPA* | ROAS | Conversion rate | Profit (3 yrs) |
|---|---:|---:|---:|---:|---:|
| Google Search | **$5.31** | $6.08 to $6.76 | **16.73** | **3.79%** | $7.12M |
| Meta | $25.31 | $28.87 to $32.56 | 2.68 | 1.94% | $0.72M |
| Snapchat | $30.34 | $37.04 to $41.95 | 1.76 | 1.22% | $0.19M |
| TikTok | $30.93 | $35.13 to $39.45 | 1.94 | 1.43% | $0.32M |
| Google Display | $57.54 | $72.36 to $82.85 | 1.21 | 0.89% | $0.04M |
| LinkedIn | $431.56 | $515.87 to $610.86 | **0.44** | 0.71% | **−$0.23M** |

\*Bootstrap, 1,000 resamples of weekly CPA. The mean of weekly CPAs sits above the pooled CPA because weak weeks count equally. Only the Snapchat and TikTok intervals overlap.

### 2. Statistically significant differences (after correction)

I ran 30 primary tests: 15 channel pairs on CPA (Welch t-test on weekly CPA) and 15 on conversion rate (Fisher's exact test). At α = 0.05 with no correction, about 1.5 false positives would be expected by chance, and the chance of at least one is 79%. I applied both Bonferroni and Benjamini-Hochberg (FDR).

| Family | Uncorrected | Bonferroni | FDR (BH) |
|---|---:|---:|---:|
| CPA, 3 years (15 pairs) | 14 | 14 | 14 |
| Conversion rate, Fisher (15 pairs) | 15 | 15 | 15 |
| CPA, **last 13 weeks only** (15 pairs) | 12 | 11 | 12 |

- **Over 3 years, correction removes nothing.** The channels differ by multiples, not percentages: p-values range from 10⁻⁵ to 10⁻⁶⁵. The one pair that is not significant, Snapchat vs TikTok on CPA (p = 0.20), is not significant before correction either.
- **Over one quarter, correction starts to bite.** Bonferroni drops Google Display vs TikTok (p = 0.004 against a threshold of 0.0033). FDR keeps it. Meta vs Snapchat and Meta vs TikTok are **not** significant on 13 weeks, although both are clearly significant on 3 years.
- **Conversion-rate tests are overconfident.** Fisher's exact test treats each of about 5M clicks as an independent coin flip, so even a 0.2-point gap (Snapchat 1.22% vs TikTok 1.43%) gets p ≈ 10⁻²⁷. A t-test on weekly rates gives the same direction with far larger p-values. I use the CPA tests to make decisions and the conversion-rate tests as supporting evidence.
- **Practical significance:** every Search, LinkedIn and Display gap is large (d > 1.4). The Meta advantage over Snapchat and TikTok is medium (d ≈ 0.5 to 0.6), which is worth $6 to $9 per acquisition. Snapchat vs TikTok is negligible (d = 0.14).

### 3. Data adequacy (power analysis)

The lab's simulation assumes weekly CPA varies ±15% around its mean. **In our data it varies about ±40%** (median coefficient of variation 0.40). The 15% assumption underestimates the sample needed by a factor of about 7.

| True CPA gap | Weeks per channel for 80% power (observed noise, simulated ±5%) | 13 weeks (1 quarter) | ~155 weeks (all data) |
|---:|---:|:---:|:---:|
| 5% | ~1,020 | insufficient | insufficient |
| 10% | ~260 | insufficient | insufficient |
| 15% | ~117 | insufficient | sufficient |
| 20% | ~65 | insufficient | sufficient |

- **All data:** every significant pair has ~100% power. The 3-year conclusions are solid.
- **One quarter:** power is 28% for the Meta vs TikTok gap (21%) and 41% for Meta vs Snapchat (28%). Detecting those gaps at 80% power needs about 49 and 35 weeks.
- **Snapchat vs TikTok:** a true gap of about 5% would need over 1,000 weeks per channel. That question can't be answered from observational data. It needs an experiment or a better metric.

---

## Recommendations

### Budget allocation ($500K/month)

Method: I ranked each channel on CPA and ROAS (50/50) and treated Snapchat and TikTok as tied on CPA, as the test says. I allocated budget in proportion to the composite score, with a **5% floor** (keeps every channel measurable) and a **35% cap** (limits concentration and diminishing returns).

| Channel | Current share* | Current $ | Recommended share | Recommended $ | Change |
|---|---:|---:|---:|---:|---:|
| Google Search | 21.9% | $109.6K | 28.5% | **$142.5K** | +$32.9K |
| Meta | 20.9% | $104.4K | 23.8% | **$118.8K** | +$14.4K |
| TikTok | 16.7% | $83.3K | 17.8% | **$89.1K** | +$5.8K |
| Snapchat | 11.7% | $58.7K | 15.4% | **$77.2K** | +$18.5K |
| Google Display | 9.1% | $45.5K | 9.5% | **$47.5K** | +$2.0K |
| LinkedIn | 19.7% | $98.5K | 5.0% | **$25.0K** | −$73.5K |
| **Total** | 100% | $500K | 100% | **$500K** | 0 |

\*Historical spend share on Sales campaigns, scaled to $500K.

### Strategic actions

1. **Cut LinkedIn to the 5% floor now.** This is the only recommendation that needs no further evidence: ROAS has been below 1 in every one of the 12 quarters (best quarter: 0.69). Rebuild the remaining $25K as a monitored test cell (new audiences or offers) with a stop rule: cut to zero if ROAS stays below 1 for 2 quarters.
2. **Scale Google Search in steps of about +$10K a month and watch marginal CPA**, not average CPA. Search demand is finite. If marginal CPA passes about $25 (Meta's level), stop scaling and move the rest of the increase to Meta.
3. **Grow Meta to about 24%.** It has a clear, medium-sized lead over the other social channels.
4. **Stop debating TikTok vs Snapchat on CPA.** They are statistically tied. Keep both at a mid share, and choose on other grounds (audience reach, creative capacity) or run a controlled test.
5. **Hold Google Display flat.** It is profitable, but only just (ROAS 1.21), so it is the first channel to cut if Search saturates.

---

## Statistical caveats

- **Synthetic data.** The data was generated from benchmark ranges, and real channel gaps are usually smaller and noisier. Before any money moves, the whole pipeline must be re-run on our own platform exports.
- **Six channels, not seven.** The dataset covers six platforms. A seventh channel (e.g. email or affiliates) would need its own data and would add 6 more pairs to the correction.
- **Scope.** Only Sales-objective campaigns are included. Reach, Traffic, Engagement, Video Views and Leads campaigns (84% of all spend) are excluded because they don't aim for purchases. Cutting them would affect future demand in ways this analysis can't see.
- **Multiple comparisons.** Results use Benjamini-Hochberg FDR, which controls the expected *share* of false discoveries. Bonferroni gives the same answer on 3 years of data and differs on one pair over 13 weeks. Use Bonferroni for one-way decisions, such as switching a channel off entirely.
- **Confidence intervals.** Over 3 years the CIs are narrow (±5 to 8%). Over the last 13 weeks they are 2 to 3.5 times wider and overlap for Meta, Snapchat and TikTok.
- **External factors.** CPA is about 40% lower in Q4 on every platform (holiday demand), so any short-window comparison depends on the season it covers. Platforms can also change auctions and attribution without notice. Last-click attribution as platforms report it gives Search credit for demand that social may have created.
- **Average vs marginal.** All CPAs are averages. The +24% conversion projection assumes the next dollar performs like the average dollar, which won't hold for Search at scale.
- **Statistical vs practical significance.** With this many clicks, tiny conversion-rate gaps become "significant". I report effect sizes and dollar gaps next to p-values, and the decisions rest on gaps large enough to matter (≥ $6 per acquisition).
- **Power-analysis limits.** The simulation assumes normally distributed weekly CPA with equal variance in both channels and independent weeks. Real CPA is right-skewed and autocorrelated, so the required sample sizes are, if anything, optimistic.

---

## Next steps

| # | Action | Owner | When |
|---|---|---|---|
| 1 | Re-run this pipeline on our own ad-platform exports (same 4 scripts, swap the loader) | Analytics | 2 weeks |
| 2 | Cut LinkedIn Sales budget to $25K/month with the ROAS stop rule | Paid social | Next budget cycle |
| 3 | Step up Search spend by +$10K/month and report marginal CPA weekly | Paid search | Start next month |
| 4 | Design a geo-split holdout test for Meta vs TikTok vs Snapchat, sized for a 15% gap | Analytics | 1 month |
| 5 | Move channel reviews from quarterly to a rolling 52 weeks, with season-adjusted CPA | Analytics + CMO office | Next quarterly review |
