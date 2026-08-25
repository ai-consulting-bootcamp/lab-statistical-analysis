# Lab: Marketing channel ROI comparison

Statistical comparison of marketing campaign performance, with multiple comparisons
correction, power analysis and a budget allocation recommendation.

**Dataset:** "Digital Marketing Metrics & KPIs to Measure" (sinderpreet, Kaggle)
https://www.kaggle.com/datasets/sinderpreet/analyze-the-marketing-spending

Chosen because it is a real daily panel with every column the analysis needs
(impressions, clicks, leads, orders, spend, revenue), 11 campaigns grouped into
4 categories, and a genuine date axis. Campaigns are the primary unit of analysis
(11 groups, 55 pairs); categories are a secondary check, since they are unbalanced
(social contains 6 campaigns, media contains 1).

## How to run

`marketing_roi_analysis.ipynb` is the deliverable. It is one notebook covering all five
parts and is committed **with outputs already executed**, so the results can be read
without running anything.

```bash
pip install pandas numpy scipy matplotlib seaborn   # scipy 1.11+ for false_discovery_control
jupyter lab marketing_roi_analysis.ipynb            # then run top to bottom
```

The same code is also available as four command line scripts, for anyone who wants to
re-run a single stage without executing the whole notebook. They pass state through the
CSVs in `outputs/`, so run them in order:

```bash
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
python business_recommendations.py
```

Paths resolve relative to the file, not the working directory, so both forms run from
anywhere on Windows, macOS or Linux.

## File map

| Path | What it is |
|---|---|
| `marketing_roi_analysis.ipynb` | **Main deliverable.** All five parts, executed, with figures and tables inline |
| `executive_memo.md` | Findings, recommendation and caveats for the CMO |
| `reflection.md` | What surprised me, what the corrections changed, limitations |
| `data_exploration.py` | Part 1: load, clean, derive metrics, aggregate by campaign and category |
| `statistical_analysis.py` | Parts 2 and 3: pairwise t tests, Cohen's d, Fisher's exact, Bonferroni and FDR |
| `power_analysis.py` | Part 4: simulated power using measured variability, sample size requirements |
| `business_recommendations.py` | Part 5: bootstrap confidence intervals, composite ranking, budget allocation |
| `data/marketing_raw.csv` | Source file as downloaded |
| `data/marketing_data.csv` | Cleaned daily panel with derived metrics |
| `outputs/` | Result tables as CSV |
| `figures/` | Charts, also embedded in the notebook |

## Setup assumptions

- `false_discovery_control` requires SciPy 1.11 or later.
- Simulations are seeded, so power figures reproduce exactly.
- The notebook and the `.py` scripts run identical logic and produce identical numbers.
- Two deliberate departures from the lab template are flagged in code comments where
  they occur: Welch t tests instead of Student's, and a coefficient of variation
  measured from the data instead of a hardcoded 0.15 in the power simulation.
- The source file does not label its currency; values are treated as generic units.
