# Lab proof — In God we trust, everyone else bring the data

**Evidence status:** Educational scenario — synthetic source data, not observed client outcomes

**Dataset:** [https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset/resolve/main/digital_marketing_dataset_30k.csv](https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset/resolve/main/digital_marketing_dataset_30k.csv) (external source used only in `--source hf` mode). Publisher explicitly describes the source as **synthetic**.

## Reproduction

```bash
python run_lab.py --source hf
python -m unittest discover -s tests -v
```

Demonstration mode: `python run_lab.py --source demo`. It writes only `demo_*` artifacts and is **not evidence of a Hugging Face dataset run**.

## Input → output and evidence

- Input: campaign-day marketing columns date, platform, objective, spend, impressions, clicks, conversions, revenue. Restrict to Sales where available; when six platforms are observed, split one actual platform by observed placement into two non-overlapping segments; otherwise select seven observed platforms. Aggregate to segment/day and use a 90-day window or available history as needed.
- Data quality / transformations: [`results/data_audit.json`](results/data_audit.json)
- Prepared input CSV: [`data/marketing_data.csv](data/marketing_data.csv)
- KPI evidence: [`results/channel_metrics.csv`](results/channel_metrics.csv)
- Daily CPA tests + Cohen d: [`results/daily_cpa_comparisons.csv`](results/daily_cpa_comparisons.csv)
- Daily ROAS comparisons: [`results/daily_roas_comparisons.csv`](results/daily_roas_comparisons.csv)
- Fisher conversion tests: [`results/fisher_conversion_comparisons.csv`](results/fisher_conversion_comparisons.csv)
- Bonferroni + BH: [`results/multiple_comparisons_summary.csv`](results/multiple_comparisons_summary.csv)
- Power curve and sample-size plan: [`results/power_curve.csv`](results/power_curve.csv), [`results/power_sample_size.csv`](results/power_sample_size.csv)
- Intervals: [`results/bootstrap_cpa_confidence_intervals.csv`](results/bootstrap_cpa_confidence_intervals.csv)
- Final $500k allocation: [`results/budget_allocation_500k.csv`](results/budget_allocation_500k.csv)
- Figures: [`figures/`](figures/)
- Executive final output: [`executive_memo.md](executive_memo.md)

## Observed execution

- Source platforms: 6; observed comparison groups: 7; analysis rows: 305; 21 comparisons/family.
- Grouping method: Six actual platforms; one split into two observed, mutually exclusive placement segments (seven allocation groups, NOT seven platforms).
- Corrected discoveries: daily_cpa: 15/21, daily_roas: 18/21, fisher_conversion: 19/21.
- Expected output: reproducible reports, charts, $500k constrained allocation (not actual causal lift).

## Failure / limitation

The first source has an **unknown license** and is explicitly synthetic. It is not measured client performance. Rows are repeated, non-random marketing campaigns, and Fisher's independence assumptions can fail; day-wise Welch p-values ignore serial autocorrelation. Revenue is a proxy; no observational ranking should be interpreted as a causal uplift estimate. A real-client validation dataset and randomized incrementality test are prerequisites for acting on this budget.
