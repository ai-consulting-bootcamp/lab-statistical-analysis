# In God we trust, everyone else bring the data

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 5 · **Status:** Required

## My submission: marketing channel statistical analysis (Ben Mayer)

Pairwise channel comparisons (Welch t-tests, Fisher's exact test, Cohen's d), Bonferroni and Benjamini-Hochberg correction, simulation-based power analysis, and a $500K budget recommendation. The findings are in [`executive_memo.md`](./executive_memo.md).

## How to run

```bash
pip install numpy pandas scipy matplotlib seaborn     # SciPy >= 1.11 for false_discovery_control
python data_exploration.py      # Part 1: downloads the raw CSV (~8 MB) into data/ on first run
python statistical_analysis.py  # Parts 2-3
python power_analysis.py        # Part 4
python recommendations.py       # Part 5
```

Run the scripts in this order, because each one reads the CSVs the previous one writes. The full pipeline takes about 15 s. It was tested with Python 3.12, SciPy 1.18 and pandas 3.0. Random seeds are fixed, so the outputs are reproducible.

## File map

| Path | What it is |
|---|---|
| [`executive_memo.md`](./executive_memo.md) | **The deliverable for the CMO**: findings, budget table, caveats, next steps |
| [`reflection.md`](./reflection.md) | What surprised me, what correction changed, limitations, how to communicate the results |
| [`data_exploration.py`](./data_exploration.py) | Part 1: dataset choice and source (docstring), loading, quality checks, cleaning, metrics by channel, distributions, seasonality |
| [`statistical_analysis.py`](./statistical_analysis.py) | Parts 2-3: Welch t-tests on weekly CPA (plus Cohen's d), Fisher's exact test on conversions/clicks, Bonferroni and BH-FDR, a 13-week supplementary family |
| [`power_analysis.py`](./power_analysis.py) | Part 4: `empirical_power_cpa()` simulation, power grid, minimum weeks for 80% power, adequacy check per significant pair |
| [`recommendations.py`](./recommendations.py) | Part 5: FDR-significant findings, `bootstrap_ci()` CPA intervals, composite score, constrained $500K allocation |
| `data/marketing_data.csv` | Cleaned analysis dataset: 926 platform × week rows with derived CTR, CVR, CPA, ROAS and profit |
| `data/raw_*.csv` | Raw download (git-ignored, re-downloaded by `data_exploration.py`) |
| `results/*.csv` | Every table the scripts produce (test results, corrections, power, CIs, allocation) |
| `results/*_output.txt` | Console output of each script, so results are readable without running anything |
| `figures/*.png` | `group_metrics_overview`, `group_distributions`, `metric_comparison_heatmap`, `rate_comparison`, `correction_comparison`, `power_analysis_cpa`, `budget_allocation` |
| [`instructions.md`](./instructions.md), [`rubric.md`](./rubric.md) | Lab brief and grading rubric (unchanged) |

## Assumptions and deviations from the spec

- **Dataset:** [Digital Marketing Performance Dataset](https://www.kaggle.com/datasets/alinaboulsi/digital-marketing-performance-dataset) (Kaggle), loaded from its public [Hugging Face mirror](https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset) at a pinned revision, so no Kaggle API key is needed. It is synthetic. See the caveats in the memo.
- **6 channels, not 7:** the dataset has six platforms.
- **Unit = week, not day:** Sales campaigns are too sparse per platform-day for a stable CPA. "Current data" for the power analysis is therefore ~155 weeks (all data) and 13 weeks (one quarter, roughly the spec's 90 days).
- **Welch t-test** (`ttest_ind(..., equal_var=False)`), because variances differ ~100× between channels.
- **Power noise:** I ran the spec's 15% CPA standard deviation and the observed ~40% side by side.
- **Heatmap colours:** the spec names `RdYlGn_r` but also says "red = significant". Those two conflict, so I used `RdYlGn` to match the stated meaning.
