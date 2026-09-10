# Dataset Documentation

**Name:** Digital Marketing Performance Dataset (Synthetic, Benchmark-Based)
**Source:** Kaggle — https://www.kaggle.com/datasets/alinaboulsi/digital-marketing-performance-dataset
(downloaded via its Hugging Face mirror: `jason1966/alinaboulsi_digital-marketing-performance-dataset`, since it provides a direct file URL — see `data/raw/` for the exact file used)
**Size:** 30,000 rows x 35 columns, ~1.83 MB

## Why this dataset

- It has **6 distinct advertising channels** to compare (`platform` column, renamed `channel`): Google Search, Meta, TikTok, LinkedIn, Snapchat, Google Display — comfortably above the lab's 3–5 group minimum.
- It already contains every metric needed for CPA/ROAS/conversion-rate/CTR: `spend`, `impressions`, `clicks`, `conversions`, `revenue`.
- It spans **3 full years of daily data** (2023-01-01 to 2025-12-31), giving each channel 760–1,090 daily observations after aggregation — far more than the "hundreds to thousands" the lab asks for, which lets pairwise t-tests and Fisher's exact tests run with real statistical power instead of toy sample sizes.
- Zero missing values and no invalid rows (`reach <= impressions`, `clicks <= impressions` checked and passed) — minimal cleaning required, more time for analysis.

## Important caveat

Per the dataset's own `README_DATASET.md` (included at `data/raw/`, downloaded alongside the CSV): **this data is synthetically generated** for BI/dashboard practice ("It does NOT represent real client data. It should NOT be used for real budget decisions."). It is used here as a realistic stand-in to practice the statistical workflow (t-tests, Fisher's exact tests, multiple comparisons correction, power analysis) end-to-end. The executive memo explicitly flags this limitation and recommends re-running the same pipeline on real internal data before acting on it.

## Columns used

| Column | Role |
|---|---|
| `date` | Daily granularity, used to build the per-channel daily panel |
| `platform` -> `channel` | Grouping variable (6 channels) |
| `spend` | Cost, used for CPA/ROAS |
| `impressions`, `clicks` | Used for CTR |
| `conversions` | Used for conversion rate, CPA, Fisher's exact test |
| `revenue` | Used for ROAS, profit |

30 other columns (country, campaign metadata, creative theme, etc.) were not used for the core channel comparison but remain in the raw file for any follow-on segmentation analysis.
