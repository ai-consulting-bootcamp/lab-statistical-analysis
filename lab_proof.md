# Lab proof — Marketing channel statistical analysis

## 1. Code / workflow
Everything is in `lab_statistical_analysis.ipynb`, run top to bottom:

1. **Load & clean** `marketing_campaign.csv` → rename columns, convert types, derive `conversions` (clicks × conversion rate) and `revenue` (cost × (1 + ROI)), drop impossible rows (none found), aggregate to **one row per channel per day** → `outputs/marketing_data.csv`.
2. **Metrics** per channel: CTR, conversion rate, CPA, ROAS, profit, margin.
3. **Pairwise tests**: Welch t-tests + Cohen's d on daily CPA and daily conversion rate (15 pairs each); Fisher's exact test on total conversions vs non-conversions (15 pairs).
4. **Multiple comparisons**: Bonferroni and Benjamini-Hochberg on each family of 15 tests (45 tests in total).
5. **Power**: simulation of daily CPA (std = 15% of mean) for 5–20% differences and 30–180 days.
6. **Decision**: bootstrap 95% CIs of daily CPA, composite score (CPA rank + ROAS rank) and budget split, executive memo.

## 2. One run with its input
- **Input:** `marketing_campaign.csv` — 22,029 rows × 16 columns, 6 channels (Email, Facebook, Google Ads, Instagram, Website, YouTube), 1 Jan – 31 Dec 2023.
- **After cleaning:** 2,187 rows (363–365 days per channel), 0 rows removed.
- **Run:** Restart & Run All, ~20 seconds, no errors.

## 3. Evidence
| Check | Result |
|---|---|
| CPA range (total) | $49.08 (Facebook) – $51.76 (Instagram) |
| ROAS range | 1.97 – 2.05 |
| CPA t-tests significant (raw → BH) | 1 → **0** of 15 |
| Conv. rate t-tests significant (raw → BH) | 5 → **0** of 15 |
| Conv. rate Fisher significant (raw → BH) | 8 → **8** of 15, but gaps of only 0.04–0.06 points |
| Expected false positives (45 tests × 0.05) | 2.25 |
| Days needed for 80% power, 5% CPA gap (15% std) | ~156 (we have ~363) |
| Real daily CPA variability (CV) | 0.35 – 0.96 |

Charts: see `outputs/` (6 PNG files).

## 4. Final output
`outputs/executive_memo.md` — **Recommendation: do not move budget on this data.** No channel has a significantly lower CPA after correction, and the significant conversion-rate gaps are too small to matter. Keep an even split (~$83,333 per channel) and run a controlled test sized for a 10% CPA difference. The composite-score model would give Facebook $142,500 and Instagram $25,000, but those ranks rest on differences we can't distinguish from noise.

## 5. Failure / limitation I hit
- **Failure:** my first version of the "days needed for 80% power" function increased the days in steps of 10 up to 10,000. For the tiny observed CPA gaps (0.1–1%) it never reached 80% and the notebook hung for minutes. Fix: increase the days by ~10% per step (up to 20,000) and return "None" if 80% is never reached — the whole notebook now runs in ~20 s.
- **Limitation:** the lab's power simulation assumes a daily CPA std of 15% of the mean, but the real data has a CV of 0.35–0.96. So the simulation says we can detect a 5% gap, while in reality we can only reliably detect ~10–15%. I kept the lab's assumption in the code and explained the gap in the answers and the memo.
- **Limitation:** the dataset has no conversion or revenue columns (both are derived), and it looks simulated (CTR is 4.4% on every channel, costs are uniformly spread between $1,000 and $9,999).
