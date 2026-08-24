# Marketing Channel ROI Comparison

Statistical analysis of marketing channel performance using real Kaggle data. Compares CPA, ROI, and conversion rate across six channels, applies multiple comparisons correction, runs power analysis, and produces a budget recommendation.

## How to run

Activate the conda environment first.

```bash
conda activate My_class_repo_conda
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
```

Run in that order. Each script reads the CSV output from the one before it.

## File map

- `data/marketing_campaign_dataset.csv` — raw dataset downloaded from Kaggle
- `data/marketing_data_cleaned.csv` — cleaned dataset, output of `data_exploration.py`
- `data_exploration.py` — Part 1: loads, cleans, and explores the dataset. Produces group summary stats and two charts.
- `statistical_analysis.py` — Parts 2-3: t-tests and Fisher's exact tests across channel pairs, plus Bonferroni and FDR correction.
- `power_analysis.py` — Part 4-5: power simulation, minimum sample size, bootstrap confidence intervals, composite channel ranking.
- `executive_memo.md` — Part 5: findings, budget recommendation, and statistical caveats.
- `group_metrics_overview.png` — bar charts of CPA, ROI, conversion rate, clicks, campaign count, engagement by channel
- `group_distributions.png` — box plots of conversion rate and ROI by channel
- `metric_comparison_heatmap.png` — p-value heatmap for conversion rate t-tests
- `rate_comparison.png` — conversion rate bar chart by channel
- `correction_comparison.png` — significant results before and after correction
- `power_analysis_cpa.png` — power curves by effect size and sample size

## Dataset

Marketing Campaign Performance Dataset, Kaggle, author Manisha B.
https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset

200,000 campaigns, 6 channels (Email, Facebook, Google Ads, Instagram, Website, YouTube), full year 2021.

## Setup assumptions

- `Acquisition_Cost` is cleaned from a string with `$` and commas into a float.
- No raw conversion counts in the source data. Conversions are derived as `Clicks × Conversion_Rate` for the Fisher's exact test.
- No revenue column, so ROAS is not calculated directly. ROI is used as provided in the dataset.