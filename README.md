# Statistical Marketing Analysis Lab

**Analyst:** Parisa Dehghani

This repository completes the mandatory parts of **LAB | In God we trust, everyone else bring the data**. The optional reflection is intentionally not included.

## Dataset choice

**Dataset:** Solstice SaaS Growth Pack — `channel_performance` subset  
**Source:** Hugging Face  
**URL:** https://huggingface.co/datasets/solsticestudioai/saas-growth-pack

I chose this public dataset because the `channel_performance` table contains 3,780 daily rows across **7 marketing channels** and **90 days**, with the fields needed for the lab: impressions, clicks, conversions, cost, attributed revenue, conversion rate, and click-through rate.

The dataset is explicitly documented by its publisher as **synthetic benchmark data**. That is a limitation, and the executive memo treats the $500K allocation as an analytical recommendation to validate on real company data, not as a production decision.

The analysis pools the six sample companies and aggregates them to daily totals for each channel. This produces 90 daily observations per channel for the t-tests and keeps the lab's 90-day power-analysis framing simple.

## Metrics calculated

- CTR = clicks / impressions
- Conversion rate = conversions / clicks
- CPA = cost / conversions
- ROAS = revenue / cost
- Profit = revenue - cost
- Profit margin = profit / revenue

## Statistical methods

- Independent Welch t-tests for daily CPA
- Cohen's d for CPA effect size
- Fisher's exact tests for conversion-rate differences
- Bonferroni correction
- Benjamini-Hochberg FDR correction
- Empirical CPA power analysis
- Bootstrap 95% confidence intervals for daily CPA
- Composite channel ranking for the $500K monthly budget

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

The Hugging Face dataset is public, so **no API key is required**.

## Run the lab

Run these three commands in order:

```bash
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
```

The final command also generates `executive_memo.md` using the actual statistical results.

## File map

| File/folder | Purpose |
|---|---|
| `README.md` | Dataset choice, setup, methodology, and file map |
| `requirements.txt` | Python dependencies |
| `data_exploration.py` | Downloads, cleans, explores data; calculates marketing metrics and charts |
| `statistical_analysis.py` | t-tests, Cohen's d, Fisher tests, multiple-comparison corrections, confidence intervals, and budget allocation |
| `power_analysis.py` | Power curves, sample-size planning, adequacy assessment, and final executive memo |
| `marketing_data.csv` | Generated cleaned Hugging Face data |
| `daily_channel_metrics.csv` | Generated daily channel-level metrics |
| `channel_summary.csv` | Generated aggregate channel performance table |
| `cpa_pairwise_results.csv` | Generated t-test/effect-size results |
| `fisher_pairwise_results.csv` | Generated Fisher exact-test results |
| `correction_summary.csv` | Generated comparison of uncorrected, Bonferroni, and FDR significance |
| `confidence_intervals.csv` | Generated bootstrap CPA confidence intervals |
| `budget_allocation.csv` | Generated $500K budget recommendation |
| `power_results.csv` | Generated empirical power results |
| `sample_size_recommendations.csv` | Generated minimum sample-size recommendations |
| `observed_difference_power.csv` | Generated power assessment for FDR-significant CPA differences |
| `statistical_findings.md` | Generated compact summary of significant findings |
| `executive_memo.md` | Required business memo, generated after all analyses |
| `outputs/` | Required charts |

## Expected charts

After a successful run, `outputs/` contains:

- `group_metrics_overview.png`
- `group_distributions.png`
- `metric_comparison_heatmap.png`
- `rate_comparison.png`
- `correction_comparison.png`
- `power_analysis_cpa.png`

## Before committing

Confirm all three scripts run without errors:

```bash
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
```

Then check that `executive_memo.md`, the generated CSV files, and all six PNG charts exist before committing.
