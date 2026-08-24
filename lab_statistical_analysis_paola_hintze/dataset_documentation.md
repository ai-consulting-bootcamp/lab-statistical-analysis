# Dataset Documentation

## Selected dataset

**Name:** Solstice SaaS Growth Pack (Sample) — `channel_performance` configuration  
**Publisher:** Solstice AI Studio  
**Platform:** Hugging Face  
**Dataset page:** [huggingface.co/datasets/solsticestudioai/saas-growth-pack](https://huggingface.co/datasets/solsticestudioai/saas-growth-pack)  
**Source file:** [`data/channel_performance/train.csv`](https://huggingface.co/datasets/solsticestudioai/saas-growth-pack/blob/main/data/channel_performance/train.csv)  
**License:** CC BY 4.0  
**Dataset period:** 1 January–31 March 2026 (90 days)

## Why this dataset

The dataset contains 3,780 rows at `date × company × channel` grain: six SaaS companies, seven marketing channels, and 90 days per channel. It includes impressions, clicks, conversions, cost, and attributed revenue, so every required marketing metric can be derived and both continuous and binary comparisons are possible. It is small enough for reproducible local analysis while providing exactly the seven-channel allocation problem in the scenario.

The publisher explicitly describes the data as **100% synthetic**. It is a real, publicly hosted Hugging Face dataset, but it is not observed customer behavior. This analysis therefore demonstrates a statistically rigorous decision workflow; its dollar recommendations are a fictional pilot plan and must not be treated as causal market evidence.

## Candidate evaluation

| Requirement | Assessment |
|---|---|
| At least 3–5 comparable groups | Pass: 7 channels |
| Hundreds of observations | Pass: 3,780 total; 630 in the single-company analysis |
| Time granularity | Pass: 90 daily observations per channel |
| Performance metrics | Pass: impressions, clicks, conversions, cost, attributed revenue |
| Missing values | Pass: 0 missing cells in the required source fields |
| Reasonable processing size | Pass: approximately 271 KB source CSV |
| Public documentation/license | Pass: dataset card, schema notes, CC BY 4.0 |

## Analysis scope

The analysis filters to **VectorFlow (C005, HR Tech, `churn_recovery`)**. Combining all companies would create 540 observations per channel but would also confound channel effects with company growth profile, customer value, and spend strategy. The filtered table contains exactly 630 rows: seven channels × 90 dates.

Channels: Content, LinkedIn Ads, Outbound Sales, Paid Search, Partnerships, Referral, and SEO.

## Transformations and quality checks

1. Parse `date` as a date.
2. Require all count, spend, and revenue fields; reject missing or negative values.
3. Validate `impressions ≥ clicks ≥ conversions` for every row.
4. Reject duplicate `company_name + date + channel` rows.
5. Filter `company_name == "VectorFlow"`.
6. Calculate daily CTR, click-to-conversion rate, CPA, ROAS, profit, and profit margin.
7. Represent divisions by zero as missing rather than infinity. Daily CPA is missing on zero-conversion days.
8. Recalculate aggregate metrics from summed numerators and denominators; do not average daily ratios for the executive ranking.

All checks passed: 3,780 source rows, six companies, seven channels, zero missing required cells, zero duplicate-grain rows, and zero funnel-invariant errors. The prepared date range is complete and every channel has 90 records.

## Important estimand distinction

Aggregate CPA is `total cost / total conversions` and drives the business ranking. The t-test uses daily CPA only on days with at least one conversion because CPA is undefined otherwise. It therefore estimates **mean daily CPA conditional on conversion**, not full-period acquisition efficiency. Conversion-positive sample sizes range from 3 days (Outbound Sales) to 81 (Referral), so CPA inference is supporting evidence only; aggregated Fisher tests and business metrics receive greater decision weight.

