# Statistical Analysis of Facebook Advertising Campaigns

This lab analyzes three Facebook advertising campaigns using exploratory analysis, marketing metrics, pairwise statistical testing, multiple-comparison correction, power analysis, confidence intervals, and a final recommendation for allocating a hypothetical **$500,000 monthly marketing budget**.

## Project Structure

```text
lab-statistical-analysis/
├── data/
│   ├── KAG_conversion_data.csv
│   └── marketing_data.csv
├── results/
│   ├── campaign_summary.csv
│   ├── group_metrics_overview.png
│   ├── group_distributions.png
│   ├── cpa_pairwise_comparisons.csv
│   ├── fisher_pairwise_comparisons.csv
│   ├── correction_summary.csv
│   ├── metric_comparison_heatmap.png
│   ├── rate_comparison.png
│   ├── correction_comparison.png
│   ├── power_analysis_cpa.png
│   ├── power_analysis_results.csv
│   ├── minimum_sample_size.csv
│   ├── current_data_adequacy.csv
│   ├── cpa_confidence_intervals.csv
│   └── budget_allocation.csv
├── data_exploration.py
├── statistical_analysis.py
├── power_analysis.py
├── business_recommendations.py
├── executive_memo.md
└── README.md
```

## File Map

- `data_exploration.py` — loads and inspects the raw data, calculates CTR, purchase rate, and CPA, creates campaign summaries and distribution plots, and saves the prepared dataset.
- `statistical_analysis.py` — performs Welch t-tests, Cohen's d calculations, Fisher's exact tests, Bonferroni correction, Benjamini-Hochberg FDR correction, and statistical visualizations.
- `power_analysis.py` — performs simulation-based power analysis, sample-size assessment, and current-data adequacy checks.
- `business_recommendations.py` — calculates bootstrap CPA confidence intervals and produces the final budget-allocation table.
- `executive_memo.md` — contains the business interpretation, final budget recommendation, statistical caveats, and next steps.
- `results/` — contains generated CSV tables and PNG visualizations.
- `data/marketing_data.csv` — prepared analysis dataset generated from the raw source data.

## Dataset

The source dataset contains **1,143 ad-level observations** across campaigns `916`, `936`, and `1178`.

Main variables used:

- `Impressions`
- `Clicks`
- `Spent`
- `Total_Conversion`
- `Approved_Conversion`

Derived metrics:

- `CTR = Clicks / Impressions`
- `Purchase_Rate = Approved_Conversion / Total_Conversion`
- `CPA = Spent / Approved_Conversion`

## Setup

Install the required packages:

```bash
python -m pip install pandas numpy scipy matplotlib seaborn
```

## How to Run

Run the scripts in this order:

```bash
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
python business_recommendations.py
```

Generated tables and charts are saved in `results/`.

## Analysis Notes

- Welch's t-test is used for CPA because group sizes and variances differ.
- Fisher's exact test is used for purchase-rate comparisons.
- Both Bonferroni and Benjamini-Hochberg corrections are applied.
- CPA is undefined for ads with zero approved conversions, so row-level CPA analysis uses only observations where CPA can be calculated.
- The dataset has no time variable, so no time-series or seasonality analysis is performed.

See `executive_memo.md` for the final findings, budget recommendation, limitations, and business interpretation.
