# Marketing channel budget allocation – statistical analysis

Ironhack AI Consulting bootcamp lab: *In God we trust, everyone else bring the data*.
Should the $500K monthly marketing budget be shifted between 6 channels? Answered with t-tests, Fisher's exact test, multiple-comparison correction, power analysis and bootstrap confidence intervals.

**Start here:** [`lab_proof.md`](lab_proof.md) · **Findings:** [`outputs/executive_memo.md`](outputs/executive_memo.md)

## How to run

1. Python 3.11 with:
   ```
   pip install -U pandas numpy scipy matplotlib seaborn kagglehub
   ```
   SciPy must be 1.11+ (for `false_discovery_control`).
2. Open `channel_budget_statistical_analysis.ipynb` and choose **Run All**.
   The dataset downloads automatically from Kaggle via `kagglehub` (no login needed for this public dataset; if it fails, download the CSV manually and set `CSV_PATH`).
3. All outputs are written to `outputs/`.

## File map

| File | What it is |
|---|---|
| `lab_proof.md` | Entry point for the reviewer: workflow, one run, evidence, output, limitation |
| `channel_budget_statistical_analysis.ipynb` | The full analysis, Parts 1–5 |
| `outputs/marketing_data.csv` | Cleaned data: one row per channel per day (6 × 365) |
| `outputs/group_metrics_overview.png` | CPA, ROAS, conversion rate, conversions, cost, profit per channel |
| `outputs/group_distributions.png` | Daily CPA and conversion-rate distributions per channel |
| `outputs/metric_comparison_heatmap.png` | Pairwise CPA t-test p-values |
| `outputs/rate_comparison.png` | Conversion rate per channel |
| `outputs/correction_comparison.png` | Significant pairs before/after Bonferroni and BH correction |
| `outputs/power_analysis_cpa.png` | Power curves for 5–20% CPA differences |
| `outputs/executive_memo.md` | Memo to the CMO with findings, recommendation and caveats |
| `reflection.md` | Personal reflection on the lab |
| `instructions.md`, `rubric.md` | Lab instructions and rubric from the original repo |

## Dataset

[Marketing Campaign Performance Dataset](https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset) (Kaggle, manishabhatt22): ~200,000 campaign rows, 6 channels, 2021.
