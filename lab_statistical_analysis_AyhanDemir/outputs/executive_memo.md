# Executive memo — Marketing budget allocation

**To:** CMO · **From:** Ayhan Demir, Marketing Analytics · **Date:** 23 Nov 2026 · **Dataset:** Online Advertising Performance Data (Kaggle; Company X, 5 ad placements: abc, def, ghi, jkl, mno) · **Period:** 01 Apr 2020 to 30 Jun 2020 (91 days)

## Executive summary
After correcting for 30 statistical tests, the five placements fall into three groups:
- **def is the clear laggard.** Its cost per conversion is 28% to 38% higher than ghi, jkl and mno, and it has the lowest conversion rate (15.4%).
- **ghi, jkl and mno cannot be told apart on CPA** (gaps of 3 to 9%, p > 0.2). Together they carry 94% of today's spend.
- **abc looks best on every metric** (CPA $0.21, conversion rate 41.8%), **but it is tiny:** $132 of spend in 91 days, with conversions on only 22 days. It is promising, but not proven at scale.

**Recommendation:** move budget away from def, keep ghi, jkl and mno as the core, and give abc a capped test budget before scaling it. The formula-based split below over-weights abc and ranks ghi, jkl and mno on differences the data cannot confirm.

## Key findings
- **Top performers:** abc (lowest CPA $0.21, highest ROAS 268x, small volume). Among the large channels, jkl and mno have the best CPA ($0.42 and $0.43), and ghi has the most conversions (331,992) and the highest conversion rate (26.7%).
- **Statistically significant differences (after BH correction):**
  - **CPA (Welch t-test on daily CPA): 7 of 10 pairs.**
    - abc cheaper than def by $0.25 per conversion (adj. p = 2.1e-06, d = 1.15, large)
    - abc cheaper than ghi by $0.16 per conversion (adj. p = 7.9e-04, d = 0.83, large)
    - abc cheaper than jkl by $0.15 per conversion (adj. p = 2.0e-03, d = 0.71, medium)
    - abc cheaper than mno by $0.12 per conversion (adj. p = 3.7e-03, d = 0.77, medium)
    - ghi cheaper than def by $0.09 per conversion (adj. p = 1.8e-02, d = 0.37, small; not significant under Bonferroni)
    - jkl cheaper than def by $0.11 per conversion (adj. p = 1.3e-02, d = 0.40, small; not significant under Bonferroni)
    - mno cheaper than def by $0.13 per conversion (adj. p = 7.9e-04, d = 0.57, medium)
  - **Conversion rate (Fisher's exact test): 10 of 10 pairs.** The ranking is abc > ghi > jkl > mno > def. Several gaps are tiny (ghi vs jkl: 0.7 points). They count as significant only because N is in the hundreds of thousands of clicks.
- **Data adequacy (power):** with 91 days per channel: 5% gap: 145 days (insufficient); 10% gap: 40 days (sufficient); 15% gap: 20 days (sufficient); 20% gap: 15 days (sufficient). That assumes a day-to-day CPA spread of 15%. The real spread is about 45% to 63%, so in practice the gaps between ghi, jkl and mno (3 to 9%) cannot be resolved with this data.

## Recommendations
**Formula-based split** (composite = 50% CPA rank + 50% ROAS rank, min 5% / max 35% per channel):

| Channel | CPA ($) | ROAS | Composite | Share | Monthly budget | Monthly spend today |
|---|---|---|---|---|---|---|
| abc | 0.21 | 268x | 5.0 | 33.3% | $166,667 | $43 |
| jkl | 0.42 | 124x | 4.0 | 26.7% | $133,333 | $2,675 |
| mno | 0.43 | 122x | 3.0 | 20.0% | $100,000 | $31,949 |
| ghi | 0.46 | 107x | 2.0 | 13.3% | $66,667 | $49,801 |
| def | 0.58 | 92x | 1.0 | 6.7% | $33,333 | $5,136 |

**How to apply it (strategic actions):**
1. **def: keep it at the bottom** (6.7% in the formula, or down to the 5% floor). It is significantly more expensive than mno under both corrections, more expensive than ghi and jkl under BH, and it has the lowest conversion rate.
2. **ghi, jkl, mno: fund as one core tier.** Their CPA gaps are not significant, so the ghi 13% / jkl 27% / mno 20% split comes from ranks rather than evidence. Split the core budget by proven scale (today's spend mix: ghi 59% / jkl 3% / mno 38%), not by rank. Note that jkl would jump from about $2,675 to $133,333 a month.
3. **abc: run a capped scale-up test.** Its formula share ($166,667 a month) is far above anything it has ever spent (about $43 a month). Raise spend in steps and watch CPA weekly. Move more money in only if CPA holds.
4. **Until abc proves it can scale,** place the unused part of its share with the core tier (ghi, jkl, mno), which already runs at scale.

## Statistical caveats
- **Dataset source and limits:** one advertiser, one ad firm, 3 months in 2020, anonymised placements. "Cost" is what Company X paid the ad firm for the clicks. "Revenue" is post-click sales credited to the ads. A ROAS of 92x to 268x points to generous attribution: use ROAS to rank channels, not as a profit forecast. Cleaning removed duplicates, rows with no placement and impossible rows (see notebook 01).
- **Multiple comparisons correction:** 30 tests means about 1.5 false positives by chance alone. I used Benjamini-Hochberg. The stricter Bonferroni correction would drop "def is more expensive than ghi and jkl" on CPA, so treat those two as likely rather than proven.
- **Confidence intervals (95% bootstrap, mean daily CPA):**

| Channel | Days | Mean daily CPA ($) | 95% CI ($) |
|---|---|---|---|
| abc | 22 | 0.26 | 0.20 to 0.32 |
| def | 91 | 0.51 | 0.45 to 0.57 |
| ghi | 91 | 0.42 | 0.37 to 0.46 |
| jkl | 91 | 0.41 | 0.36 to 0.46 |
| mno | 91 | 0.38 | 0.35 to 0.42 |

  The ranges for ghi, jkl and mno overlap. abc's range rests on only 22 days.
- **External factors:** April to June 2020 (the early COVID-19 months), the campaign and banner mix differs by placement, and attribution (sales after a click are not proof that the ad caused them). Scale is a factor too: $500K a month is about 5.6x today's total spend ($89,605 a month), and CPAs seen at today's spend may not hold at higher spend.
- **Statistical vs practical significance:** all 10 conversion-rate pairs are significant with Fisher, but the gaps of 0.7 to 3.2 points between ghi, jkl and mno are too small to move budget on their own.
- **Power limitations:** the power simulation assumes a 15% day-to-day spread in CPA. The real spread is 45% to 63% (3 to 4 times larger), so the true power is lower and "not significant" here means **not enough data**, not "no difference".

## Next steps
1. Agree on the smallest CPA gap worth acting on (for example 10%) **before** the next test.
2. Launch the abc scale-up test with a fixed budget cap and a fixed duration. Review it weekly.
3. To separate ghi, jkl and mno, run a planned test: shift a fixed share of budget between them for a set period and compare against a control.
4. Re-run this analysis monthly with fresh data and re-allocate based on BH-corrected results and confidence intervals.
