# Lab: Marketing Channel ROI Comparison

This submission analyzes 200,000 campaign records across six marketing channels.

## File map

- `data_exploration.py` - loads, cleans, aggregates, and plots the source data
- `statistical_analysis.py` - runs Welch t-tests, Fisher exact tests, FDR/Bonferroni corrections, bootstraps CPA confidence intervals, and creates the allocation
- `power_analysis.py` - performs empirical CPA power analysis and sample-size calculations
- `marketing_campaign_source.csv` - original downloaded dataset
- `marketing_data.csv` - cleaned, prepared campaign-level data
- `daily_channel_metrics.csv` - channel metrics aggregated by date
- `channel_summary.csv` - aggregate channel metrics
- `cpa_comparisons.csv` - pairwise CPA Welch t-test results
- `conversion_rate_comparisons.csv` - pairwise Fisher exact-test results
- `cpa_confidence_intervals.csv` - 95% bootstrap CPA confidence intervals
- `correction_summary.csv` - comparison of significance after correction
- `power_analysis_results.csv` - power estimates by effect size and number of days
- `minimum_sample_sizes.csv` - minimum days for 80% power
- `current_data_adequacy.csv` - adequacy assessment for FDR-significant CPA pairs
- `budget_allocation.csv` - proposed $500K monthly allocation
- `executive_memo.md` - concise findings, recommendations, and caveats
- `DATASET.md` - dataset provenance and preparation notes
- `reflection.md` - interpretation and communication reflection
- PNG files - figures referenced in the memo and scripts

## Setup and run

Python 3.11+ is recommended. Install dependencies and run the scripts from this folder:

```powershell
python -m pip install pandas numpy scipy matplotlib seaborn
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
```

The scripts generate CSV tables and PNG visualizations in this folder.

## Secret and credential hygiene

Do not put API keys, passwords, access tokens, private keys, certificates, or local `.env`
files in this repository. Keep credentials in an environment-specific secret manager or
local `.env` file; both `.env` patterns and common key/certificate formats are ignored by
the repository `.gitignore`.

## Dataset source

The source is a Hugging Face mirror of the Kaggle “Marketing Campaign Performance Dataset” by manishabhatt22:

- Dataset page: https://huggingface.co/datasets/federicomoreno/marketing-campaign-performance-200k
- Original Kaggle mirror referenced by the dataset page: https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset

The source contains 200,000 rows and 16 columns. It spans 2021-01-01 through 2021-12-31 and includes six channels: Email, Facebook, Google Ads, Instagram, Website, and YouTube.
