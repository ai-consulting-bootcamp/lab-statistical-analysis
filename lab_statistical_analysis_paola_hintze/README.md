# Marketing Channel ROI Comparison

## Run

From this folder:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
python run_all.py
```

`run_all.py` executes the three stages in dependency order and overwrites generated outputs deterministically. Python 3.11+ and SciPy 1.11+ are assumed.

## File map

| Path | Purpose |
|---|---|
| `dataset_documentation.md` | Dataset selection, source, license, schema, quality, transformations |
| `data_exploration.py` | Load, validate, filter, calculate metrics, export prepared data and overview charts |
| `statistical_analysis.py` | Welch t-tests, Cohen's d, Fisher exact tests, Bonferroni and BH-FDR corrections |
| `power_analysis.py` | Monte Carlo power, sample planning, bootstrap CIs, composite ranking and budget constraints |
| `analysis_report.md` | Full technical findings and interpretation |
| `executive_memo.md` | Decision-oriented memo for the CMO |
| `reflection.md` | Reflection on surprises, corrections, limitations, and communication |
| `data/source_channel_performance.csv` | Complete 3,780-row Hugging Face source table |
| `data/source_companies.csv` | Six-company dimension table from the same source |
| `data/marketing_data.csv` | Prepared 630-row VectorFlow analysis table, 90 days × 7 channels |
| `outputs/` | CSV/JSON/TXT result artifacts |
| `figures/` | PNG charts required by the lab |

## Output inventory

The scripts produce group metrics, data-quality checks, 21 CPA comparisons, 21 Fisher comparisons, correction summaries, power results, sample-size recommendations, bootstrap confidence intervals, observed-pair power assessments, and a $500K allocation table. The plots cover performance, distributions, CPA p-values, conversion rates, correction impact, power curves, and budget allocation.

The source is a public **synthetic** dataset. Conclusions are therefore a demonstration of statistical workflow and should not be represented as measured market behavior.

