# Marketing Channel Statistical Analysis Lab

## How to run

```bash
pip install numpy pandas matplotlib scipy   # scipy>=1.11 required for false_discovery_control
python3 data_exploration.py        # Part 1: load, clean, explore, save marketing_data.csv
python3 statistical_analysis.py    # Parts 2-3: t-tests, Fisher's exact, multiple comparisons correction
python3 power_analysis.py          # Part 4: power curves, min sample size
python3 business_recommendations.py # Part 5: bootstrap CIs, composite ranking, budget allocation
```

Run in this order — later scripts read outputs written by earlier ones
(`data/marketing_data.csv`, `outputs/fisher_exact_results.csv`).

## File map

| File | What it's for |
|---|---|
| `data_exploration.py` | Part 1: dataset loading, cleaning, metric derivation, group summary, exploratory charts |
| `statistical_analysis.py` | Parts 2-3: pairwise t-tests (CPA, ROI) + Cohen's d, Fisher's exact tests on conversion rate, Bonferroni + FDR correction |
| `power_analysis.py` | Part 4: empirical power simulation, power curves, minimum sample size table |
| `business_recommendations.py` | Part 5: bootstrap confidence intervals, composite channel ranking, budget allocation |
| `executive_memo.md` | Findings, budget recommendation, and statistical caveats for the CMO |
| `reflection.md` | Reflection on surprises, correction impact, limitations, and communication approach |
| `data/marketing_campaign_raw.csv` | Raw dataset as downloaded |
| `data/marketing_data.csv` | Cleaned dataset with derived metrics (CPA, ROAS, CTR, Profit, etc.) |
| `outputs/` | All generated tables (CSV) and charts (PNG) |

## Dataset

**Marketing Campaign Performance Dataset** — Kaggle, 22,029 individual campaign records,
6 channels (Facebook, Google Ads, Instagram, Website, Email, YouTube), full calendar year 2023.
- Kaggle: https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset
- Chosen because it has a real grouping variable (channel) with 6 groups, thousands of
  observations per group, and cost/conversion/ROI fields that map directly onto the CPA/ROAS
  metrics the CMO scenario requires.

## Setup assumptions
- Conversions, Revenue, CPA, ROAS, CTR, Profit, and Profit Margin are all derived from the raw
  Conversion_Rate / Acquisition_Cost / ROI / Clicks / Impressions columns (see comments in
  `data_exploration.py` for the exact formulas).
- "Attempts" for the Fisher's exact test = Clicks; "successes" = estimated Conversions.
- Power analysis simulates CPA as normally distributed (15% coefficient of variation) — see
  `power_analysis.py` docstring.
