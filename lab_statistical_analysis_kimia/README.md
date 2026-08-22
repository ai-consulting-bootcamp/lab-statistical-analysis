# Lab: Marketing Channel ROI Comparison

## Status

✅ **Complete.** Run against the real Kaggle dataset (200,000 rows, no missing
values). All scripts, charts, and the executive memo below are generated from
that real data.

## Dataset

- **Name:** Marketing Campaign Performance Dataset
- **Source:** Kaggle
- **Author:** Manisha B
- **URL:** https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset
- **Why chosen:** 200,000 campaign-level rows with a clear grouping variable
  (`Channel_Used`: Email, Google Ads, YouTube, Instagram, Website, Facebook —
  6 channels, ~33K rows each) and performance metrics (Conversion_Rate,
  Acquisition_Cost, ROI, Clicks, Impressions, Engagement_Score). Large,
  balanced groups with no missing data made this a clean fit for pairwise
  testing, multiple-comparisons correction, and power analysis.
- **Correction to my initial guess:** before opening the real file, I assumed
  "Display / Influencer / Search / Email / Social Media" were the channels —
  those are actually values of a separate column, `Campaign_Type`. The real
  grouping variable used throughout this analysis is `Channel_Used`, as above.

## How to run

```
pip install numpy pandas scipy matplotlib   # SciPy 1.11+ required
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
python business_recommendations.py
```

Raw CSV expected at `data/marketing_campaign_dataset.csv` (not included in
this repo — download it from the Kaggle URL above; it's ~27 MB).

## File map

| File | Purpose |
|---|---|
| `data_exploration.py` | Part 1 — loads raw Kaggle CSV, cleans currency/percent strings, computes derived metrics, saves `data/marketing_data_clean.csv`, produces `outputs/group_metrics_overview.png`, `outputs/group_distributions.png`, `outputs/group_boxplot.png` |
| `statistical_analysis.py` | Parts 2–3 — pairwise t-tests (CPA), Fisher's exact tests (conversion), Bonferroni + FDR correction; `outputs/metric_comparison_heatmap.png`, `outputs/rate_comparison.png`, `outputs/correction_comparison.png` |
| `power_analysis.py` | Part 4 — empirical power simulation, power curves (`outputs/power_analysis_cpa.png`), minimum sample size table, data-adequacy assessment |
| `business_recommendations.py` | Part 5 — bootstrap confidence intervals, composite channel ranking, budget allocation table, generates `executive_memo.md` |
| `executive_memo.md` | Generated business memo — findings, recommendations, caveats |
| `reflection.md` | Personal reflection on the exercise |
| `data/` | Raw + intermediate CSVs (raw CSV itself gitignored/excluded — too large, download separately) |
| `outputs/` | All generated charts (7 PNGs) |

## Key results summary

- **Metrics computed:** CPA (Acquisition_Cost), Conversion Rate, CTR (Clicks/Impressions),
  and ROI, all broken out by channel. **ROAS and Profit/Profit Margin are not computed**
  — this dataset has no `Revenue` column, only `Acquisition_Cost` and `ROI` (already a
  ratio). This is stated explicitly in the console output of `data_exploration.py` and
  as a labeled "not available" panel in `outputs/group_metrics_overview.png`, rather
  than silently omitted.
- **CPA (Acquisition_Cost):** no pairwise channel difference was significant
  even before correction (all uncorrected p > 0.08). No budget-allocation
  claim should be made on CPA differences between channels in this dataset.
- **Conversion rate:** 9 of 15 pairwise Fisher's exact comparisons were
  significant after FDR correction — but every one of those differences is
  under 0.5 percentage points, because n ≈ 33K per channel gives enormous
  power to detect even trivial differences. This is flagged explicitly in
  `executive_memo.md` as statistically real but not practically actionable
  on its own.
- **Power:** with 364 days of data, the analysis can reliably (80% power)
  detect CPA differences of 10%+ within ~40 days, and even 5% differences
  within ~150 days — so the "no significant CPA difference" finding above is
  not an artifact of insufficient data.

## Setup assumptions

- `Acquisition_Cost` ships as a currency string (`"$16,174.00"`) and is
  cleaned to float via regex strip of `$` and `,`.
- `conversions_est` (used for Fisher's exact test) is derived as
  `Clicks × Conversion_Rate`, since the dataset does not include a raw
  conversions-count column.
- `Duration` (e.g. `"30 days"`) and `Date` (daily, 2021-01-01 to 2021-12-31)
  are present but not used as grouping/statistical variables in this
  analysis — `Channel_Used` is the primary comparison axis per the lab spec.

