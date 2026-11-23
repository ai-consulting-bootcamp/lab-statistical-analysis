# Statistical Analysis Lab: Marketing Channel Budget Allocation

**Lab:** "In God we trust, everyone else bring the data" · **Author:** Barsha Mishra

The CMO wants to split a **$500K monthly budget** across marketing channels. This lab tests, with statistical rigour, whether any channel is really better, using t-tests, Fisher's exact test, Cohen's d, multiple comparisons correction (Bonferroni, Benjamini-Hochberg), power analysis and bootstrap confidence intervals. The narrative and key findings are in `outputs/executive_memo.md`.

## Dataset
- **Kaggle: Marketing Campaign Performance Dataset** (manishabhatt22): https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset
- 200,000 campaign rows, aggregated to **6 channels × 365 days** (2021)
- Assumptions: `conversions = Conversion_Rate × Clicks`, `revenue = cost × (1 + ROI)`, `cost = Acquisition_Cost`

## How to run
1. Download `marketing_campaign_dataset.csv` from Kaggle and place it in this folder. The raw file is not committed, because of its size and Kaggle's terms; the cleaned version is in `outputs/marketing_data.csv`.
2. Install the packages: `pip install numpy pandas matplotlib seaborn scipy` (SciPy **1.11+** is needed for `false_discovery_control`).
3. Open `marketing_channel_statistical_analysis.ipynb` and run all cells top to bottom (the power analysis takes about 1 minute).

## File map
| File / folder | What it is |
|---|---|
| `lab_proof.md` | **Entry point:** workflow, one run with input, evidence, final output, one limitation |
| `marketing_channel_statistical_analysis.ipynb` | Full analysis: data exploration (Part 1), statistical tests (Part 2), corrections (Part 3), power analysis (Part 4), recommendations (Part 5) |
| `reflection.md` | Answers to the 4 reflection questions |
| `outputs/marketing_data.csv` | Cleaned dataset: one row per channel per day |
| `outputs/executive_memo.md` | Executive memo to the CMO with findings, recommendations and caveats |
| `outputs/budget_allocation.csv` | Composite score and budget allocation table (vs equal split) |
| `outputs/cpa_confidence_intervals.csv` | 95% bootstrap confidence intervals for daily CPA per channel |
| `outputs/group_metrics_overview.png` | CPA, ROAS, conversion rate, conversions, cost and profit per channel |
| `outputs/group_distributions.png` | Histograms and box plots of daily CPA and conversion rate |
| `outputs/metric_comparison_heatmap.png` | Pairwise CPA p-values (colour turns at 0.05) |
| `outputs/rate_comparison.png` | Conversion rate by channel |
| `outputs/correction_comparison.png` | Significant results before and after Bonferroni / BH correction |
| `outputs/power_analysis_cpa.png` | Power curves for 5-20% CPA differences |
