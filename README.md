# Marketing Channel Statistical Analysis Lab

Statistical analysis of e-commerce marketing channel performance: CPA/ROAS/
conversion-rate comparisons across 4 channels, with t-tests, Fisher's exact
tests, multiple-comparisons correction (Bonferroni + Benjamini-Hochberg FDR),
power analysis, and budget-allocation recommendations for a $500K monthly
marketing budget.

## Dataset

- **Source:** [alsayed7/marketing_dataset](https://huggingface.co/datasets/alsayed7/marketing_dataset) (Hugging Face)
- **Why chosen:** 2,000 e-commerce campaign records with the exact fields this
  lab needs — `Marketing_Channel` (4 groups: Email, Influencer Marketing, Paid
  Ads, Social Media), impressions, clicks, conversions, spend, and revenue.
- **Sample used:** the first 400 campaigns (100 rows × 4 pages of the HF
  Dataset Viewer), retrieved via the public Dataset Viewer API since the
  analysis environment has no outbound network access for direct downloads.
  This is a representative subsample of the full 2,000-row dataset,
  ~90-106 campaigns per channel — well within the "hundreds per group" target.

## How to run

```bash
pip install pandas numpy scipy matplotlib seaborn
python data_exploration.py          # Part 1: load, clean, explore, visualize
python statistical_analysis.py      # Part 2-3: t-tests, Fisher's exact, corrections
python power_analysis.py            # Part 4: power curves, sample-size planning
python business_recommendations.py  # Part 5: CIs, composite ranking, allocation
```

Each script reads from the prior script's output and writes to `data/` and
`images/`, so run them in order the first time.

## File map

| File | Purpose |
|---|---|
| `data_exploration.py` | Part 1 — loads raw data, cleans it, engineers CPA/ROAS/conversion-rate/CTR/profit metrics, saves `marketing_data.csv`, produces `group_metrics_overview.png` and `group_distributions.png` |
| `statistical_analysis.py` | Part 2-3 — pairwise t-tests on CPA (with Cohen's d), Fisher's exact tests on conversion rate, Bonferroni + FDR correction; produces the p-value heatmap, rate comparison chart, and correction comparison chart |
| `power_analysis.py` | Part 4 — Monte Carlo power simulation for CPA differences across effect sizes and sample sizes; minimum sample size for 80% power; produces `power_analysis_cpa.png` |
| `business_recommendations.py` | Part 5 — bootstrap 95% CIs for CPA, composite channel ranking, $500K budget allocation table |
| `executive_memo.md` | CMO-facing memo: findings, recommendations, statistical caveats |
| `reflection.md` | Lab reflection questions |
| `data/marketing_data_raw.csv` | As-scraped 400-campaign dataset (pre-cleaning) |
| `data/marketing_data.csv` | Cleaned dataset with engineered metrics (output of Part 1) |
| `data/channel_summary.csv` | Channel-level aggregate metrics table |
| `data/cpa_ttest_results.csv` | All 6 pairwise CPA t-test results incl. Cohen's d, Bonferroni/FDR flags |
| `data/conversion_rate_fisher_results.csv` | All 6 pairwise Fisher's exact test results incl. Bonferroni/FDR flags |
| `data/conversion_binomial_summary.csv` | Channel-level conversions/attempts used for Fisher's exact tests |
| `data/correction_summary.csv` | Uncorrected vs. Bonferroni vs. FDR significant-comparison counts |
| `data/power_analysis_results.csv` | Full power-vs-sample-size grid |
| `data/min_sample_size.csv` | Minimum days needed for 80% power, by effect size |
| `data/cpa_confidence_intervals.csv` | Bootstrap 95% CI for mean CPA per channel |
| `data/budget_allocation.csv` | Composite ranking + recommended $500K allocation |
| `images/*.png` | All chart deliverables (metrics overview, distributions, p-value heatmap, rate comparison, correction comparison, power curves) |

## Setup assumptions

- Python 3.12, pandas/numpy/scipy/matplotlib/seaborn (see `pip install` above).
- `scipy.stats.false_discovery_control` (SciPy ≥1.11) is used for the
  Benjamini-Hochberg correction.
- Fisher's exact test is run on **channel-level pooled totals** (sum of
  conversions/clicks across all campaigns in a channel), not per-campaign —
  see the caveats section in `executive_memo.md` for why this matters when
  interpreting the resulting p-values.
- Random seeds are fixed (`np.random.default_rng(42)` / `(7)`) for
  reproducibility of the bootstrap and power-simulation results.

See `executive_memo.md` for the full narrative write-up and key findings.
