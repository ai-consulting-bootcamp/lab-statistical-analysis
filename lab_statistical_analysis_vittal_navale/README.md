# Marketing Channel Budget Allocation — Statistical Analysis

Lab: *In God we trust, everyone else bring the data* — statistical analysis of real marketing channel performance to inform a $500K/month budget allocation across 6 channels.

Full narrative and findings live in [`executive_memo.md`](executive_memo.md); dataset choice/rationale in [`DATASET.md`](DATASET.md). This README is just a file map and run instructions.

## How to run

Requires Python 3.10+ with `numpy`, `pandas`, `matplotlib`, `scipy` (SciPy 1.11+ for `false_discovery_control`). Run the scripts **in order** from this folder, since each one reads the output of the previous:

```bash
pip install numpy pandas matplotlib scipy
python3 data_exploration.py         # Part 1: load, clean, explore -> data/marketing_data.csv
python3 statistical_analysis.py     # Parts 2-3: t-tests, Fisher's exact, corrections
python3 power_analysis.py           # Part 4: power curves, sample size planning
python3 business_recommendations.py # Part 5: CIs, composite ranking, budget allocation
```

Each script prints its results to stdout and writes CSVs to `data/` and charts to `images/`. `executive_memo.md` and `reflection.md` were written by hand, grounded in the numbers these scripts produced.

## File map

| Path | Purpose |
|---|---|
| `DATASET.md` | Dataset choice, source, URL, and why it was selected (Part 1 deliverable) |
| `data_exploration.py` | Part 1: loads raw data, cleans it, aggregates to a daily-by-channel panel, computes CTR/conversion rate/CPA/ROAS/profit, saves summary table + overview/distribution charts |
| `statistical_analysis.py` | Parts 2-3: pairwise t-tests on CPA (+ Cohen's d), pairwise Fisher's exact tests on conversion rate, Bonferroni + Benjamini-Hochberg FDR correction on both families |
| `power_analysis.py` | Part 4: empirical power simulation for CPA differences, power curves, minimum-sample-size table, adequacy check for the FDR-significant pairs found in `statistical_analysis.py` |
| `business_recommendations.py` | Part 5: bootstrap 95% CIs for CPA, composite channel ranking (CPA + ROAS), proposed budget allocation table |
| `executive_memo.md` | **Main deliverable** — findings, recommendations, budget allocation, and statistical caveats for a non-technical (CMO) audience |
| `reflection.md` | Reflection on surprises, how correction changed conclusions, limitations, and how to communicate this to stakeholders |
| `data/raw/` | Original source files: the 30K-row CSV, its data dictionary, and its own README (dataset is synthetic — see caveats) |
| `data/marketing_data.csv` | Cleaned, analysis-ready daily-by-channel panel (this is the "marketing_data.csv" the lab asks for) |
| `data/*.csv` | Every intermediate result table (channel summary, t-test results, Fisher results, correction summary, power tables, CIs, ranking, budget allocation) |
| `images/*.png` | All required charts: group metrics overview, group distributions, p-value heatmap, rate comparison, correction comparison, power curves |

## Setup assumptions

- Ran locally with Python 3.13 / SciPy's native `false_discovery_control` (no manual BH fallback needed).
- The grouping variable used throughout is `channel` (renamed from the source's `platform` column) — 6 groups: Google Search, Meta, TikTok, LinkedIn, Snapchat, Google Display.
- The "daily-by-channel" panel (one row per date x channel, ~6,400 rows total, 760-1,090 days per channel) is the sample used for all t-tests, bootstrap CIs, and distribution plots. Fisher's exact tests instead use full 3-year totals (conversions vs. non-conversions per channel), since that test compares aggregate counts rather than daily samples.
