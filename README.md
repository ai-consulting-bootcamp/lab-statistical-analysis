# In God we trust, everyone else bring the data — Paola Hintze

Completed marketing-channel statistical analysis for a fictional $500K monthly allocation decision. The submission uses a documented public Hugging Face dataset, filters one company to avoid mixing company effects, evaluates seven channels over 90 days, corrects 42 pairwise tests, performs empirical power analysis, and converts the evidence into a guardrailed test budget.

## File map

All student work is in [`lab_statistical_analysis_paola_hintze/`](./lab_statistical_analysis_paola_hintze/):

- [`README.md`](./lab_statistical_analysis_paola_hintze/README.md) — run instructions and detailed file map.
- [`dataset_documentation.md`](./lab_statistical_analysis_paola_hintze/dataset_documentation.md) — source, license, selection rationale, data structure, and transformations.
- [`data_exploration.py`](./lab_statistical_analysis_paola_hintze/data_exploration.py) — validation, cleaning, metrics, summary table, and exploratory charts.
- [`statistical_analysis.py`](./lab_statistical_analysis_paola_hintze/statistical_analysis.py) — Welch t-tests, Cohen's d, Fisher tests, Bonferroni, and BH-FDR.
- [`power_analysis.py`](./lab_statistical_analysis_paola_hintze/power_analysis.py) — empirical power, bootstrap confidence intervals, and constrained budget allocation.
- [`analysis_report.md`](./lab_statistical_analysis_paola_hintze/analysis_report.md) — technical results and interpretation.
- [`executive_memo.md`](./lab_statistical_analysis_paola_hintze/executive_memo.md) — client-facing recommendation with caveats.
- [`reflection.md`](./lab_statistical_analysis_paola_hintze/reflection.md) — lessons and communication approach.
- [`data/`](./lab_statistical_analysis_paola_hintze/data/) — public source files and prepared 630-row analysis dataset.
- [`outputs/`](./lab_statistical_analysis_paola_hintze/outputs/) — all result tables and quality checks.
- [`figures/`](./lab_statistical_analysis_paola_hintze/figures/) — seven analysis visualizations.

The original [`instructions.md`](./instructions.md) and [`rubric.md`](./rubric.md) remain at repository root for traceability.

## Reproduce

```bash
cd lab_statistical_analysis_paola_hintze
python -m venv .venv
source .venv/bin/activate  # Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
python run_all.py
```

The analysis is deterministic: simulations and bootstrap resampling use a fixed seed. No credentials are required.
