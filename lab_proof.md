# Lab proof: Is any marketing channel really better?

## 1. Code / workflow
Everything is in `marketing_channel_statistical_analysis.ipynb`:

```
Kaggle CSV (200,000 campaigns)
  → clean + derive conversions/revenue → aggregate to 6 channels × 365 days (outputs/marketing_data.csv)
  → metrics per channel (CPA, ROAS, conversion rate, CTR, profit)
  → Welch t-tests + Cohen's d on daily CPA and conversion rate (15 pairs each)
  → Fisher's exact test on total conversions/clicks (15 pairs)
  → Bonferroni + Benjamini-Hochberg correction (45 tests)
  → power simulation (5-20% CPA differences, 30-365 days)
  → bootstrap 95% CIs, composite score, budget allocation → executive memo
```

## 2. One run with its input
- **Input:** `marketing_campaign_dataset.csv` (Kaggle, 200,000 rows, 16 columns). After cleaning: 0 rows removed; **2,190 rows = 6 channels × 365 days** (2021-01-01 to 2021-12-31).
- **Example comparison:** Website vs Instagram, daily CPA $283.62 vs $286.93 (gap $3.31, 1.2%).

## 3. Evidence it produced
- `outputs/metric_comparison_heatmap.png`: all 15 CPA pairs non-significant (lowest p = 0.075)
- `outputs/correction_comparison.png`: Fisher 9 → 7 (Bonferroni) → 9 (BH); t-tests 0 → 0
- `outputs/power_analysis_cpa.png`: 5% CPA difference detectable with 150 days; we have 365
- `outputs/cpa_confidence_intervals.csv`: all CPA confidence intervals overlap ($281-$290)

## 4. Final output
- **CPA:** 0 of 15 pairs significant (before and after correction); every Cohen's d negligible (|d| ≤ 0.13).
- **Conversion rate:** Fisher 9/15 significant (7 after Bonferroni), but all rates are 7.98-8.03% (largest gap 0.056 percentage points); t-test 0/15.
- **Power:** about 99% power for a 5% CPA gap, so a meaningful difference would have been found.
- **Recommendation** (`outputs/executive_memo.md`): **do not reallocate**; keep about $83K per channel and run a controlled geo/holdout experiment. A rank-based formula would give Website $131K vs Instagram $36K, a 3.7× gap built on noise.

## 5. One failure / limitation I hit
- **Misleading heatmap:** the suggested colour map `RdYlGn_r` coloured *high* p-values red, the opposite of "red = significant". Switching to `RdYlGn` then made p = 0.075 look red. The fix was `TwoSlopeNorm(vcenter=0.05)`, so the colour turns exactly at the significance threshold.
- **Limitation:** the dataset is very likely synthetic, and conversions and revenue were derived from rates, so the results demonstrate the method rather than real channel performance.
