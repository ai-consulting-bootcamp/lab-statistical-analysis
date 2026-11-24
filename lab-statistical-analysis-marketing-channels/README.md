# In God we trust, everyone else bring the data · Marketing channel analysis

**Student:** Jaime Garate Marquerie · Ironhack AI Consulting, Week 7 Day 5

**Start here:** [`lab_proof.md`](lab_proof.md) · **Decision document:** [`executive_memo.md`](executive_memo.md)

## Dataset (Step 1)

[Marketing Campaign Performance Dataset](https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset) (Kaggle):
- 200,000 campaigns;
- 6 channels: Email, Facebook, Google Ads, Instagram, Website, YouTube;
- daily dates from 1 Jan to 31 Dec 2021;
- clicks, impressions, conversion rate, acquisition cost, ROI.

**Why this dataset:**
- It has a clear group variable (channel).
- It has cost, outcome and click metrics.
- It covers 365 days, more than the 90 days the lab requires.
- It has enough data per group (about 33,000 campaigns).

**Limitation:** it appears synthetic (see memo caveats).

**Derived metrics** (assumptions):
- Cost = Acquisition_Cost.
- Conversions = Conversion_Rate × Clicks.
- Revenue = Cost × (1 + ROI).
- CTR = Clicks / Impressions; CPA = Cost / Conversions; ROAS = Revenue / Cost.

**Unit of analysis for the t-tests:** one value per channel per day (365 × 6).

## File map

| File | Content |
|---|---|
| `data_exploration.py`, `statistical_analysis.py`, `power_analysis.py` | Analysis code (Parts 1–5) |
| `marketing_data.csv` | Cleaned dataset with derived metrics (one row per campaign) |
| `daily_channel_metrics.csv` | Day × channel aggregates used in the tests |
| `group_metrics_summary.csv` | Channel totals and ratios (Step 3) |
| `results/ttest_cpa.csv`, `results/ttest_roas.csv` | t-tests with Cohen's d, Bonferroni and FDR (Steps 4, 6) |
| `results/fisher_conversion.csv` | Fisher's exact tests with odds ratios, Bonferroni and FDR (Steps 5, 6) |
| `results/correction_summary.csv` | Significant counts before and after correction |
| `results/power_table.csv`, `results/min_days.csv`, `results/adequacy.csv` | Power analysis (Step 7) |
| `results/bootstrap_ci_cpa.csv`, `results/allocation.csv` | Confidence intervals and bounded allocation (Steps 8–9) |
| `figures/*.png` | Overview, distributions, p-value heatmap, conversion rates, correction comparison, power curves |
| `executive_memo.md` | Executive memo (Step 10) |
| `proof/` | Console logs of the real run and the dataset hash |

## Results in one table

| Metric | Test | Uncorrected | Bonferroni | FDR | Practical size |
|---|---|---|---|---|---|
| Daily CPA | t-test (15 pairs) | 0 | 0 | 0 | max 1.2 %, d ≤ 0.13 |
| Daily ROAS | t-test (15 pairs) | 2 | 0 | 0 | false positives |
| Conversion rate | Fisher (15 pairs) | 9 | 7 | 9 | ≤ 0.06 pp, h = 0.002 |

## How to run

```
pip install pandas numpy scipy matplotlib seaborn
python data_exploration.py <path-to>/marketing_campaign_dataset.csv
python statistical_analysis.py
python power_analysis.py
```

SciPy ≥ 1.11 is needed for `scipy.stats.false_discovery_control`.

**Reflection questions (optional):** answered implicitly in the memo. A non-significant result after correction is a good outcome: it stops a budget move based on noise.
