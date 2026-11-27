# Lab: Marketing channel ROI comparison — Elif Yurdakul

Statistical comparison of 6 marketing channels to guide a $500K monthly budget. Data: Kaggle's Marketing Campaign Performance Dataset.

**Start here:** [`lab_proof.md`](./lab_proof.md) (reviewer entry point) · findings and recommendation: [`executive_memo.md`](./executive_memo.md)

## File map

| Path | What it is |
|---|---|
| `lab_proof.md` | Reviewer entry point: workflow, an example run, evidence, final output, a failure hit |
| `executive_memo.md` | Executive memo: findings, $500K allocation, caveats, next steps (Step 8) |
| `reflection.md` | Reflection (optional deliverable) |
| `data_exploration.ipynb` | Part 1: dataset choice, loading, quality checks, cleaning, channel metrics (Steps 1–3) |
| `statistical_analysis.ipynb` | Parts 2–3: t-tests + Cohen's d, Fisher's exact test, Bonferroni and FDR corrections (Steps 4–6) |
| `power_analysis.ipynb` | Part 4: simulated power curves, minimum sample sizes, data adequacy (Step 7) |
| `business_recommendations.ipynb` | Part 5: FDR-corrected findings, bootstrap CIs, composite score, budget allocation (Step 8) |
| `scripts/download_dataset.py` | Downloads the Kaggle dataset into `data/raw/` (token read from `.env`) |
| `data/marketing_data.csv` | Cleaned dataset: channel × day (2,190 rows), with CTR, conversion rate, CPA and ROAS |
| `data/raw/` | Raw Kaggle CSV (not committed: 27 MB; recreate with the download script) |
| `outputs/` | Result tables: channel summary, pairwise tests, corrections, power, CIs, allocation |
| `figures/` | All charts the lab asks for, plus CI and allocation charts |
| `requirements.txt` | Python packages |

## How to run

```bash
pip install -r requirements.txt
# put KAGGLE_API_TOKEN=... in a .env file at the repository root (it is git-ignored)
python scripts/download_dataset.py          # from this folder
jupyter nbconvert --to notebook --execute --inplace data_exploration.ipynb statistical_analysis.ipynb power_analysis.ipynb business_recommendations.ipynb
```

Run the notebooks in that order from this folder. Each one reads files written by the one before. Simulations and bootstraps use fixed seeds, so results reproduce exactly.

## Setup assumptions

- Python 3.10+ and SciPy ≥ 1.11 (for `false_discovery_control`).
- A Kaggle API token for the download step only. All later steps run offline from `data/`.
- Derived metrics: conversions = clicks × conversion rate; revenue = cost × (1 + ROI); `Acquisition_Cost` = campaign spend.
