# In God We Trust, Everyone Else Bring the Data

I compare five advertising placements, check which differences are supported by the data, and build a cautious monthly budget recommendation.

## How to run

Use Python 3.12. Install the packages with:

```bash
pip install pandas numpy scipy matplotlib seaborn kagglehub jupyter
```

SciPy 1.11 or newer is needed for `false_discovery_control`. Open this folder in VS Code. Run notebooks 01 through 05 in order, top to bottom. The dataset downloads on the first run and is cached after that.

## File map

| File | Purpose |
|---|---|
| [01_data_exploration.ipynb](01_data_exploration.ipynb) | Loads and cleans the Kaggle data, then builds daily metrics. |
| [02_pairwise_comparisons.ipynb](02_pairwise_comparisons.ipynb) | Runs Welch t-tests, Cohen's d, and Fisher's exact tests. |
| [03_multiple_comparisons.ipynb](03_multiple_comparisons.ipynb) | Applies Bonferroni and Benjamini-Hochberg corrections. |
| [04_power_analysis.ipynb](04_power_analysis.ipynb) | Simulates power and estimates required sample sizes. |
| [05_business_recommendations.ipynb](05_business_recommendations.ipynb) | Builds confidence intervals, a composite score, a budget split, and the memo. |
| [outputs/marketing_data.csv](outputs/marketing_data.csv) | Cleaned daily table with one row per date and placement. |
| [outputs/group_metrics_overview.png](outputs/group_metrics_overview.png) | Channel totals for key business metrics. |
| [outputs/group_distributions.png](outputs/group_distributions.png) | Daily CPA and conversion-rate distributions. |
| [outputs/results_cpa_ttest.csv](outputs/results_cpa_ttest.csv) | Pairwise daily CPA tests and correction columns. |
| [outputs/results_conv_rate_ttest.csv](outputs/results_conv_rate_ttest.csv) | Pairwise daily conversion-rate tests and correction columns. |
| [outputs/results_conv_rate_fisher.csv](outputs/results_conv_rate_fisher.csv) | Pooled-click Fisher tests and correction columns. |
| [outputs/metric_comparison_heatmap.png](outputs/metric_comparison_heatmap.png) | Uncorrected pairwise CPA p-values. |
| [outputs/rate_comparison.png](outputs/rate_comparison.png) | Pooled conversion rates by placement. |
| [outputs/correction_comparison.png](outputs/correction_comparison.png) | Significant pair counts before and after correction. |
| [outputs/power_analysis_cpa.csv](outputs/power_analysis_cpa.csv) | Simulated power by effect size and number of days. |
| [outputs/power_min_days.csv](outputs/power_min_days.csv) | Minimum days estimated for 80% power. |
| [outputs/power_analysis_cpa.png](outputs/power_analysis_cpa.png) | Simulated power curves for CPA differences. |
| [outputs/executive_memo.md](outputs/executive_memo.md) | CMO memo with findings, recommendations, and caveats. |
| [lab_proof.md](lab_proof.md) | Reviewer entry point with workflow and evidence. |
| [reflection.md](reflection.md) | My answers to the four reflection questions. |

## Setup assumptions

- I treat `placement` as the marketing channel.
- I aggregate to one row per day per placement, for five placements across 91 days.
- I treat source `revenue` as Company X's cost and `post_click_sales_amount` as Company X's revenue. I drop the source `cost` column.
- I use random seed 42 for simulations and bootstraps.
