# LAB | In God we trust, everyone else bring the data

Week 7 of the Ironhack AI Consulting Bootcamp &mdash; comparing marketing
campaign performance with statistics that survive scrutiny.
**Author:** Nnanyelugo Ahukannah

Fork of [`ai-consulting-bootcamp/lab-statistical-analysis`](https://github.com/ai-consulting-bootcamp/lab-statistical-analysis).
`instructions.md` and `rubric.md` are unchanged; the original lab README is
preserved in full below this section.

## Start here

**[`executive_memo.md`](lab_statistical_analysis_ugo_ahukannah/executive_memo.md)** &mdash; the findings, the budget table and the sizing for the next test.

## The dataset

**`criteo/criteo-attribution-dataset`** &mdash; real ad-serving logs from Criteo's
production systems, 16.5M impressions over 30 days, ungated on Hugging Face.
400,000 impressions were streamed; the six largest campaigns (5,808&ndash;21,680
impressions each) are compared.

It was chosen over two alternatives because it is genuinely observational **and**
carries a cost column, without which CPA cannot be computed. ROAS cannot be
computed from it at all &mdash; the release has no revenue field, and real ad
revenue is essentially never published &mdash; so that one metric comes from a
clearly-labelled **synthetic** secondary set and drives no recommendation. Full
reasoning in [`dataset_documentation.md`](lab_statistical_analysis_ugo_ahukannah/dataset_documentation.md).

## What it found

**Conversion rates differ four-fold and the gaps are real; most cost differences
are not worth acting on.**

- Conversion rate ranges 2.04% to 8.28% across the six campaigns. Thirteen of
  fifteen pairwise comparisons are significant after correction.
- Fourteen of fifteen cost comparisons are significant too &mdash; but **six of
  those have a negligible effect size.** At this sample size significance is
  cheap; the effect size is what decides.
- **Two pairs are statistically indistinguishable** (B/E, C/D), which turns a
  ranking of six into two strong campaigns and two weak ones.
- **CPA is compared by bootstrap** (2,000 resamples), because it is a ratio of
  totals with no per-impression value to test. Fourteen of fifteen pairs are
  unambiguous; on the fifteenth, **Bonferroni and Benjamini-Hochberg disagree**
  &mdash; E vs F is significant under BH and not under Bonferroni, and the
  intervals overlap.
- Correction withdrew nothing on the other two families, because their p-values
  sit at machine zero. Repeated at a realistic pilot size of 400 impressions per
  campaign, Bonferroni withdrew **three of seven** findings.
- The data is **observational, not an experiment**, so nothing here shows that
  moving budget reproduces the gap. Every recommendation is framed as a bounded
  test.

## Running it

```bash
cd lab_statistical_analysis_ugo_ahukannah
pip install -r requirements.txt

python fetch_dataset.py          # streams both datasets from Hugging Face (network)
python data_exploration.py       # Part 1  - metrics, summary table, figures
python statistical_analysis.py   # Parts 2-3 - t-tests, Fisher, effect sizes, corrections
python power_analysis.py         # Part 4  - power curves and sample-size planning
```

`fetch_dataset.py` needs network access; everything after it runs offline against
the committed CSVs. No API keys are required and none are stored here.
Double-clickable launchers (`run_*.command` / `.bat`) are provided for each.

## File map

| Path | What it is |
|---|---|
| [`executive_memo.md`](lab_statistical_analysis_ugo_ahukannah/executive_memo.md) | Step 8 &mdash; findings, caveats, budget table, test sizing |
| [`dataset_documentation.md`](lab_statistical_analysis_ugo_ahukannah/dataset_documentation.md) | Step 1 &mdash; candidates evaluated, choice, and the three limitations |
| [`reflection.md`](lab_statistical_analysis_ugo_ahukannah/reflection.md) | What surprised me, what correction changed, limitations, how to explain it |
| `marketing_statistical_analysis.ipynb` | The whole analysis as an executed notebook |
| `marketing_data.py` | Shared loading, cleaning, metrics, Wilson intervals, Cohen's d |
| `fetch_dataset.py` | Streams the Criteo slice and downloads the secondary set |
| `data_exploration.py` | Part 1 |
| `statistical_analysis.py` | Parts 2&ndash;3, including the pilot-size correction demonstration |
| `power_analysis.py` | Part 4 |
| `data/criteo_attribution_sample.csv` | The cleaned 400k-impression extract |
| `data/synthetic_platform_performance.csv` | Secondary set, synthetic, ROAS only |
| `group_performance_summary.csv` | Per-campaign metrics with confidence intervals |
| `results_ttest_cost.csv`, `results_fisher_conversion.csv` | Full pairwise results |
| `results_cpa_by_campaign.csv`, `results_cpa_pairs.csv` | CPA with bootstrap intervals, and all 15 CPA pairs |
| `results_correction_subsample_demo.csv` | The pilot-size correction demonstration |
| `power_*.csv` | Achieved power and required sample sizes |
| `figures/` | Overview, cost distributions, effect-size heatmap, correction effect, power curves |

## Rubric coverage

| Rubric rows | Where |
|---|---|
| 1, 16 &mdash; find and evaluate a real dataset | [`dataset_documentation.md`](lab_statistical_analysis_ugo_ahukannah/dataset_documentation.md) &mdash; three candidates assessed against group structure, cost and revenue |
| 2, 9, 17 &mdash; load and explore | `data_exploration.py`, `marketing_data.py` |
| 3, 18 &mdash; CPA, ROAS, conversion rates | `data_exploration.py`; ROAS from the labelled synthetic set |
| 3, 18 &mdash; pairwise CPA | `statistical_analysis.py` &mdash; bootstrap CPA per campaign and across all 15 pairs |
| 4, 10, 19, 20 &mdash; t-tests and Fisher's exact | `statistical_analysis.py` &mdash; Welch's on cost, Fisher on conversion, all 15 pairs |
| 5 &mdash; Cohen's d | `statistical_analysis.py`; heatmap in `figures/` |
| 6, 11, 21 &mdash; Bonferroni and Benjamini-Hochberg | `statistical_analysis.py`, applied within each family, plus the pilot-size demonstration |
| 7, 12, 22 &mdash; power analysis | `power_analysis.py` &mdash; achieved power, required n, adequacy verdict, curves |
| 8, 13, 14, 23 &mdash; recommendations and memo | [`executive_memo.md`](lab_statistical_analysis_ugo_ahukannah/executive_memo.md) |
| 15 &mdash; all code runs without errors | Four scripts and the notebook all exit 0; the notebook has zero error cells |

---
---

# Original lab README

*Everything below is unmodified from the upstream lab repository.*

# In God we trust, everyone else bring the data

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 5 · **Status:** Required

This repository contains everything you need for this lab.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
