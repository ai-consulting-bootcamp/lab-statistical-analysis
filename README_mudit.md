# Lab: Statistical Analysis — Nykaa Campaign Performance (CPA & Conversion Rate by Campaign Type)

Analysis of Kaggle's "Nykaa Campaign Data" dataset (`data/nykaa_campaign_data.csv`, 55,555
campaigns). Start with `lab_statistical_analysis_mudit/executive_memo.md` for findings and
recommendations, or `lab_statistical_analysis_mudit/dataset_selection.md` for the dataset choice
and why `Campaign_Type` is used as the channel grouping variable.

All deliverables live in `lab_statistical_analysis_mudit/`.

## How to run

```bash
cd lab_statistical_analysis_mudit
pip install numpy pandas scipy matplotlib seaborn  # scipy>=1.11 required
python data_exploration.py                 # -> data/marketing_data.csv
python key_metrics.py                      # -> figures/group_metrics_overview.png, group_distributions.png
python ttest_comparisons.py                # -> results/ttest_results.csv, figures/metric_comparison_heatmap.png
python fisher_exact_tests.py               # -> results/fisher_results_*.csv, figures/rate_comparison.png
python multiple_comparisons_correction.py  # -> results/*_corrected.csv, figures/correction_comparison.png
python power_analysis.py                   # -> results/power_*.csv, figures/power_analysis_*.png
python business_recommendations.py         # -> results/confidence_intervals.csv, allocation_recommendation.csv
```
Run in this order — each script reads outputs saved by the previous one.

## File map

| File / folder | What it's for |
|---|---|
| `lab_statistical_analysis_mudit/dataset_selection.md` | Dataset choice, source, and why `Campaign_Type` is the grouping variable |
| `lab_statistical_analysis_mudit/data_exploration.py` | Load, inspect, clean the raw CSV; saves `data/marketing_data.csv` |
| `lab_statistical_analysis_mudit/key_metrics.py` | Group-level metrics (CPA, ROAS, CTR, conversion rate, profit) + overview/distribution plots |
| `lab_statistical_analysis_mudit/ttest_comparisons.py` | Pairwise t-tests + Cohen's d on CPA across `Campaign_Type` groups |
| `lab_statistical_analysis_mudit/fisher_exact_tests.py` | Pairwise Fisher's exact tests on conversion rate (conversions/clicks) across `Campaign_Type` groups |
| `lab_statistical_analysis_mudit/multiple_comparisons_correction.py` | Bonferroni + Benjamini-Hochberg correction on both test families |
| `lab_statistical_analysis_mudit/power_analysis.py` | Empirical power curves, minimum sample sizes, current-data-adequacy check |
| `lab_statistical_analysis_mudit/business_recommendations.py` | Bootstrap CIs, composite ranking, budget allocation exercise |
| `lab_statistical_analysis_mudit/executive_memo.md` | **Findings, recommendations, statistical caveats — start here** |
| `lab_statistical_analysis_mudit/reflection.md` | What surprised us, limitations, how to communicate this to stakeholders |
| `lab_statistical_analysis_mudit/data/marketing_data.csv` | Cleaned dataset (output of `data_exploration.py`) |
| `lab_statistical_analysis_mudit/figures/` | All saved plots (`.png`) |
| `lab_statistical_analysis_mudit/results/` | All saved result tables (`.csv`) and per-script console logs (`.log`) |
| `data/nykaa_campaign_data.csv` | Raw source dataset for this lab |

## Setup assumptions

- The grouping variable used for all pairwise comparisons is `Campaign_Type` (5 groups: Email,
  Influencer, Paid Ads, SEO, Social Media) — see `dataset_selection.md` for why this was chosen
  over the more granular but messier `Channel_Used` field.
- `Acquisition_Cost` in the source file is cost-**per-acquisition** (CPA), not total campaign
  spend — `Total_Cost = Acquisition_Cost × Conversions` is derived in `data_exploration.py` and
  used for group-level ROAS/Profit in `key_metrics.py`.
- Conversion rate is defined as `Conversions / Clicks`, per the lab's formula.
- Random seeds are fixed (`np.random.default_rng(42)` / `(7)`) for reproducibility of the
  Monte Carlo power simulations and bootstrap confidence intervals.
