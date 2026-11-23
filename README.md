# Lab — In God we trust, everyone else bring the data

Statistical analysis of 6 marketing channels to decide how to split a $500K monthly budget: t-tests, Cohen's d, Fisher's exact test, multiple-comparison correction (Bonferroni / Benjamini-Hochberg), power analysis, bootstrap confidence intervals and an executive memo.

**Start here:** [`lab_proof.md`](lab_proof.md)

## How to run
1. Install the libraries (Python 3.10+, SciPy 1.11+ is needed for `false_discovery_control`):
   ```
   pip install numpy pandas matplotlib seaborn scipy jupyter
   ```
2. Keep `marketing_campaign.csv` in the same folder as the notebook.
3. Open `lab_statistical_analysis.ipynb` and run all cells top to bottom (Kernel → Restart & Run All). It takes about 20 seconds.
4. All charts, the cleaned data and the memo are written to `outputs/`.

## File map
| File | What it is |
|---|---|
| `lab_statistical_analysis.ipynb` | The completed lab notebook (all TODOs and written answers) |
| `marketing_campaign.csv` | Input data: 22,029 campaigns, 6 channels, 2023 ([source](https://github.com/AnithaInsights/marketing-campaign-performance-analysis), a copy of the [Kaggle Marketing Campaign Performance dataset](https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset)) |
| `lab_proof.md` | Entry point: workflow, one run, evidence, final output, a limitation |
| `reflection.md` | Reflection questions |
| `outputs/marketing_data.csv` | Cleaned data: one row per channel per day |
| `outputs/group_metrics_overview.png` | CPA, ROAS, conversion rate, conversions, cost, profit per channel |
| `outputs/group_distributions.png` | Histograms and box plots of daily CPA and conversion rate |
| `outputs/metric_comparison_heatmap.png` | p-values of the pairwise CPA t-tests |
| `outputs/rate_comparison.png` | Conversion rate per channel |
| `outputs/correction_comparison.png` | Significant results before/after Bonferroni and BH |
| `outputs/power_analysis_cpa.png` | Power curves for 5–20% CPA differences |
| `outputs/executive_memo.md` | Final recommendation for the CMO |
