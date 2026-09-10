# Executive Memo: Marketing Channel Budget Allocation

**Date:** 2026-09-10
**Analyst:** Vittal Navale
**Dataset used:** Digital Marketing Performance Dataset (Kaggle, alinaboulsi) — 30,000 ad-level records aggregated to a daily-by-channel panel of 6,439 observations
**Period analyzed:** January 2023 – December 2025 (3 years), 6 channels: Google Search, Meta, TikTok, LinkedIn, Snapchat, Google Display

---

## Executive Summary

Across three years of daily performance data, **Google Search is the only channel generating positive ROI** — it returns $3.78 in revenue per $1 spent, versus $0.11–$0.62 for every other channel. The differences in CPA (cost per acquisition) and conversion rate between channels are large, statistically significant after correcting for multiple comparisons, and backed by more than enough historical data to trust them. We recommend shifting the $500K monthly budget away from LinkedIn and Google Display — the two most expensive, lowest-converting channels — and concentrating spend on Google Search, with Meta as a secondary channel.

## Key Findings

**Top performing channels (ranked by composite score: 50% CPA rank + 50% ROAS rank):**

| Rank | Channel | CPA | ROAS | Conv. Rate | Profit (3yr) |
|---|---|---|---|---|---|
| 1 | Google Search | $12.66 | 3.78 | 1.88% | **+$7.62M** |
| 2 | Meta | $62.81 | 0.62 | 0.95% | -$1.00M |
| 3 (tie) | Snapchat | $68.61 | 0.46 | 0.65% | -$0.78M |
| 3 (tie) | TikTok | $73.95 | 0.48 | 0.72% | -$1.10M |
| 5 | Google Display | $127.03 | 0.28 | 0.50% | -$0.83M |
| 6 | LinkedIn | $457.47 | 0.11 | 0.82% | -$2.28M |

**Statistically significant differences (after Benjamini-Hochberg FDR correction, α=0.05):**
- 12 of 15 pairwise CPA comparisons remained significant, with effect sizes ranging from small (Cohen's d≈0.25) to large (d≈1.11). The largest gap: Google Search vs. LinkedIn, an $822.88/day mean CPA difference (d=1.11, large).
- All 15 of 15 conversion-rate comparisons (Fisher's exact test) remained significant. Google Search converts at 1.88% vs. 0.50–0.95% for every other channel.
- 95% bootstrap confidence intervals for CPA do not overlap between Google Search ($80–$102) and any other channel, including the next-cheapest, Meta ($205–$253).

**Data adequacy (power analysis):**
- With our ~760–1,090 days of history per channel, we had essentially 100% power to detect every difference we found — these are not false positives from an underpowered test.
- For *future* tests with a shorter monitoring window: 90 days of data gives ~62–99%+ power to detect CPA differences of 10% or more, but only ~62% power for a 5% difference. A 5% CPA shift would need roughly 140 days of data per channel to detect reliably at 80% power.

## Recommendations

**Resource allocation** (see `data/budget_allocation.csv` for full detail; constrained to a 5%–40% floor/ceiling per channel to avoid abandoning any channel entirely or over-concentrating risk):

| Channel | Allocation % | Monthly Budget |
|---|---|---|
| Google Search | 28.5% | $142,518 |
| Meta | 23.75% | $118,765 |
| Snapchat | 16.6% | $83,135 |
| TikTok | 16.6% | $83,135 |
| Google Display | 9.5% | $47,506 |
| LinkedIn | 5.0% (floor) | $24,941 |

**Strategic actions:**
1. **Increase Google Search spend** toward the proposed 28.5% ($142.5K/mo). It is the only channel with positive ROAS and by far the lowest CPA — the data supports going higher than this if creative/inventory allows, but we capped allocation at 40% of budget as a diversification safeguard.
2. **Cut LinkedIn to the 5% floor.** Its CPA ($457) is 6–36x higher than every other channel with no offsetting conversion-rate advantage. We did not recommend eliminating it entirely because B2B lead quality (not measured in this dataset) may differ by channel — see caveats.
3. **Hold Meta, Snapchat, TikTok at moderate spend** while running a controlled test (see Next Steps) to see if a modest reallocation from these channels toward Search improves blended ROAS without collapsing top-of-funnel reach.
4. **Reduce Google Display** below its current spend share; it has the second-worst CPA and lowest conversion rate.

## Statistical Caveats

- **Dataset limitations and source:** This dataset (Kaggle: alinaboulsi/digital-marketing-performance-dataset) is **synthetically generated** for analytics-education purposes, per its own documentation. Patterns are internally consistent and realistic enough for this exercise, but they are not this company's real spend data — before acting on these numbers with real budget, this analysis must be re-run on actual internal performance data.
- **Multiple comparisons correction applied:** Both Bonferroni and Benjamini-Hochberg (FDR) correction were applied to the 15 CPA comparisons and 15 conversion-rate comparisons. With N this large (millions of clicks/conversions), corrections barely moved the needle (12/15 and 15/15 remained significant either way) — **statistical significance is not the binding constraint here; effect size is.** We leaned on Cohen's d and raw dollar/percentage-point differences to judge practical importance, not just p-values.
- **Confidence intervals:** 95% bootstrap CIs for CPA are reported per channel (`data/cpa_confidence_intervals.csv`). Intervals are tight relative to the between-channel gaps, which is part of why we trust the ranking — but they still reflect day-to-day variance only, not other sources of uncertainty (seasonality shifts, platform algorithm changes, competitive dynamics).
- **External factors:** iOS/Android tracking changes, seasonal demand, competitor bidding, and creative fatigue can all shift channel performance in ways this historical analysis cannot anticipate. Treat this as a strong prior, not a permanent ranking.
- **Statistical vs. practical significance:** A statistically significant CPA gap of a few dollars (e.g., Snapchat vs. TikTok, $8.33/day, d=-0.02, "negligible") is not a basis for reallocating budget — we excluded negligible/small effect-size pairs from the strategic recommendations above and focused on medium/large effects.
- **Power analysis limitations:** The power simulation assumes CPA is approximately normally distributed with a fixed relative standard deviation (15% of the mean) and a symmetric cap at 50% of baseline — a simplification of the messier real distribution. Use the simulated minimum-sample-size figures as planning guidance, not an exact guarantee.

## Next Steps

1. Run a live, randomized budget-shift test (e.g., +10% to Google Search / -10% to LinkedIn for 60–90 days) rather than a full immediate reallocation, and re-measure CPA/ROAS with the same pairwise-testing pipeline.
2. Investigate whether LinkedIn's high CPA is offset by higher-value leads (deal size, sales-cycle conversion) not captured in this dataset — pull CRM data before fully deprioritizing it.
3. Re-run this full analysis on the company's actual internal marketing data (this dataset is a synthetic stand-in) before finalizing next quarter's budget.
4. Extend the power analysis to conversion-rate (Fisher's exact) differences, not just CPA, to plan sample sizes for future A/B tests on creative/targeting changes.
