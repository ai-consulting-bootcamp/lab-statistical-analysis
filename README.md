# LAB | Marketing Channel Performance: EDA and Statistical A/B Testing

**Track:** Module 5 — Evaluation & strategy · **When:** Week 7, Day 5 · **Status:** Required

This repository contains the completed marketing-channel exploratory and statistical analysis for the Global Ads Performance dataset.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against
- [`statistical_analysis.ipynb`](./statistical_analysis.ipynb) — completed notebook covering EDA, metric comparisons, binary conversion outcomes, multiple-comparison correction, power analysis, and recommendations
- [`global_ads_performance_dataset.csv`](./global_ads_performance_dataset.csv) — campaign-day source data
- [`outputs/`](./outputs/) — cleaned data, summary tables, statistical results, charts, allocation plan, and executive memo

## Analysis highlights

- The dataset contains 1,800 campaign-day observations across Google Ads, Meta Ads, and TikTok Ads.
- CTR, CPC, CPA, and ROAS are used directly from the database; only conversion rate, profit, and profit margin are derived in the notebook.
- Fisher's exact tests find statistically significant conversion-rate differences for all channel pairs, but the largest aggregate gap is only about 0.25 percentage points.
- Fisher's test uses millions of clicks, while the campaign-day conversion-rate t-test uses hundreds of observations; the difference in sample size explains why Fisher detects small gaps that the t-test does not.
- The recommendation is provisional because the scenario mentions seven channels while this dataset contains three platforms.

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
