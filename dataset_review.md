# Dataset discovery and suitability

## Selected source

- **Name:** Digital Marketing Performance Dataset (30k)
- **Platform:** Hugging Face mirror of a Kaggle-origin educational dataset
- **URL:** https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset
- **Direct CSV:** https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset/resolve/main/digital_marketing_dataset_30k.csv
- **Data dictionary:** https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset/blob/main/data_dictionary.csv
- **Publisher's README:** https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset/blob/main/README_DATASET.md

## Why selected

This externally published dataset supplies `date`, `platform`, `objective`, `spend`, `impressions`, `clicks`, `conversions`, and `revenue` in coherent campaign records. Unlike datasets containing only a single aggregated conversion-rate percentage, it allows reproducible computation of **actual count ratios** and dollar-denominated ad metrics. The source CSV contains only **six actual advertising platforms** after the Sales and validation filters. For the exercise's seven-group comparisons, the pipeline splits one platform into **two non-overlapping, observed placement segments** (one actual placement and all its other observed placements), keeping the other five platforms intact. It selects a split with at least 25 active days per group, falling back to full available history if needed. These are **seven delivery segments, not seven independent platforms**; no rows or platforms are fabricated. The choice and exact values are recorded in `results/data_audit.json`. This is a material limitation of the exercise's stated seven-channel scenario.

## Strengths and weaknesses

**Strengths:** downloadable CSV, meaningful metric columns, daily dates, identifiable platforms, enough examples for the requested tests, documentation available. Data calculations can be checked directly from counts.

**CRITICAL LIMITATION:** The publisher explicitly says **synthetically generated, benchmark-based, not real client data**, and warns not to use it for real budget decisions. The Hugging Face page lists **unknown license**. This is a real *public dataset* but **not real-world observed advertising performance**. If the instructor requires genuine historical advertiser measurements, substitute a licensed first-party dataset with the same columns. Until then, conclusions are only educational/demonstrative; do not present modeled ROAS or p-values as evidence of market impact.

**Selection and confounding:** choosing the placement split on observed coverage/spend conditions on past behavior; Sales-only filtering may introduce objective mix differences; campaigns may share audiences, platforms, costs, and attribution, violating independence. Dates represent campaigns, not randomly assigned experiments. Revenue is synthetic modeled proxy and includes lead valuation in other objectives, hence Sales-only filter.

**License:** The code downloads source into a gitignored raw file; the repository publishes transformed 90-day aggregated statistics and source links rather than redistributing the full 8 MB raw original.

## Data dictionary used

- `date`: time grouping key
- `platform` → `channel`: statistical grouping key
- `objective`: analysis restricts to Sales when sufficient rows exist
- `spend`: advertising cost, USD
- `impressions`, `clicks`, `conversions`: counters for CTR, CVR, and Fisher table
- `revenue`: publisher-provided synthetic monetary proxy for ROAS

Cleaning: parse date and all numeric columns, remove missing and invalid rows, enforce `0 <= conversions <= clicks <= impressions`, `spend > 0`, `revenue >= 0`; construct seven observed delivery segments as described above; aggregate daily counts; derive daily CPA/ROAS/CTR/CVR. Full row counts, file checksum and chosen channels are recorded automatically in `results/data_audit.json` on a source run.
