# Lab: Statistical Analysis — Marketing A/B Test & Ad-Delivery Timing

Analysis of Kaggle's "Marketing A/B Testing" dataset (`data/marketing_AB.csv`, 588,101 users).
Start with `lab_statistical_analysis_mudit/executive_memo.md` for findings and recommendations,
or `lab_statistical_analysis_mudit/dataset_selection.md` for why the metrics here diverge from
the lab's CPA/ROAS template (this dataset has no cost/revenue fields).

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
| `lab_statistical_analysis_mudit/dataset_selection.md` | Dataset choice, source, and the CPA/ROAS data-gap decision |
| `lab_statistical_analysis_mudit/data_exploration.py` | Load, inspect, clean the raw CSV; saves `data/marketing_data.csv` |
| `lab_statistical_analysis_mudit/key_metrics.py` | Group-level metrics (conversion rate, ad exposure) + overview/distribution plots |
| `lab_statistical_analysis_mudit/ttest_comparisons.py` | Pairwise t-tests + Cohen's d on `total_ads` across day-of-week groups |
| `lab_statistical_analysis_mudit/fisher_exact_tests.py` | Pairwise Fisher's exact tests on `converted`, plus the headline ad-vs-psa test |
| `lab_statistical_analysis_mudit/multiple_comparisons_correction.py` | Bonferroni + Benjamini-Hochberg correction on both test families |
| `lab_statistical_analysis_mudit/power_analysis.py` | Empirical power curves, minimum sample sizes, current-data-adequacy check |
| `lab_statistical_analysis_mudit/business_recommendations.py` | Bootstrap CIs, composite ranking, ad-delivery weighting recommendation |
| `lab_statistical_analysis_mudit/executive_memo.md` | **Findings, recommendations, statistical caveats — start here** |
| `lab_statistical_analysis_mudit/reflection.md` | What surprised us, limitations, how to communicate this to stakeholders |
| `lab_statistical_analysis_mudit/data/marketing_data.csv` | Cleaned dataset (output of `data_exploration.py`) |
| `lab_statistical_analysis_mudit/figures/` | All saved plots (`.png`) |
| `lab_statistical_analysis_mudit/results/` | All saved result tables (`.csv`) and per-script console logs (`.log`) |
| `data/marketing_AB.csv` | Raw source dataset for this lab |

## Setup assumptions

- No cost, revenue, impression, or click data exists in the source file, so CPA, ROAS, and CTR
  are not calculated anywhere in this analysis — see `dataset_selection.md` for the full
  reasoning and the adapted metrics used instead (conversion rate, ad exposure).
- The grouping variable used for pairwise comparisons is `most_ads_day` (7 groups), not a
  marketing "channel" — this dataset's only real 2-group comparison is `test_group` (ad vs. psa),
  used as the headline finding.
- Random seeds are fixed (`np.random.default_rng(42)` / `(7)`) for reproducibility of the
  Monte Carlo power simulations and bootstrap confidence intervals.
