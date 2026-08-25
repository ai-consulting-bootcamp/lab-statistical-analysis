# Step 1: Dataset Selection

## Dataset

- **Name:** Nykaa Campaign Data
- **Source:** Kaggle
- **URL:** https://www.kaggle.com/datasets/ishitabahamnia/nykaa-campaign-data-csv
- **File used:** `data/nykaa_campaign_data.csv` (provided directly for this lab; 55,555 rows, 16 columns)

## Why this dataset

Unlike the previous dataset used for this lab (Marketing A/B Testing — see git history), this one
is campaign-level and includes real cost, revenue, and funnel data (impressions, clicks, leads,
conversions, acquisition cost, revenue, ROI) across 5 campaign types. That means CPA, ROAS, CTR,
and conversion rate — the actual metrics this lab is built around — can all be calculated directly
from the source data, with no adaptation needed.

## Columns

| Column | Type | Description |
|---|---|---|
| `Campaign_ID` | string | Unique campaign identifier |
| `Campaign_Type` | categorical (5 levels: Email, Influencer, Paid Ads, SEO, Social Media) | **Grouping variable used throughout this analysis** |
| `Target_Audience` | categorical (5 levels) | Audience segment targeted |
| `Duration` | int (5–30) | Campaign length in days |
| `Channel_Used` | string | Platform(s) used (single or comma-separated combinations; 156 distinct raw values — see note below) |
| `Impressions` | int | Ad impressions served |
| `Clicks` | int | Ad clicks |
| `Leads` | int | Leads generated |
| `Conversions` | int | Conversions (sales) |
| `Revenue` | int | Revenue generated ($) |
| `Acquisition_Cost` | float | **Cost per acquisition (CPA)** — confirmed against the `ROI` column (see `data_exploration.py`); not a total campaign spend figure |
| `ROI` | float | Return on investment, `(Revenue - Total_Cost) / Total_Cost` |
| `Language` | categorical (4 levels) | Campaign language |
| `Engagement_Score` | float | Engagement score (not used in this analysis) |
| `Customer_Segment` | categorical (5 levels) | Customer segment (not used in this analysis) |
| `Date` | date | Campaign date, `2024-07-01` to `2025-06-24` |

## Design decisions

- **Grouping variable ("channel"):** `Campaign_Type` — 5 clean, evenly-sized groups
  (~11,100 campaigns each, no missing values). `Channel_Used` was considered instead, since it's
  the more literal "channel" field, but it has 156 distinct raw values (many multi-channel
  combinations like `"WhatsApp, Google"`) and would need non-trivial explosion/cleanup to use as a
  grouping variable — `Campaign_Type` is the clean, lab-ready grouping variable and is used as the
  channel-equivalent throughout.
- **Continuous metric (t-tests, Step 4):** CPA (`Acquisition_Cost`), compared per-campaign across
  `Campaign_Type` groups — this is a genuine per-row continuous metric, unlike the previous
  dataset where a substitute had to be found.
- **Binary outcome (Fisher's exact, Step 5):** conversion rate, aggregated as
  `Conversions / Clicks` per group per the lab's formula.
- **Derived metrics:** `Total_Cost = Acquisition_Cost × Conversions`, from which ROAS
  (`Revenue / Total_Cost`), Profit (`Revenue - Total_Cost`), and Profit Margin are computed in
  `key_metrics.py`. CTR (`Clicks / Impressions`) is also computed there.
- **Not used:** `Channel_Used` (too granular/messy — noted above), `Target_Audience`,
  `Language`, `Customer_Segment`, `Engagement_Score`, `Duration` — available for a follow-up
  breakdown but out of scope for the primary channel comparison this lab asks for.
- **Power analysis sample-size unit (Step 7):** the lab's template specifies power/sample-size
  curves in **days** (`empirical_power_cpa(..., n_days, ...)`), because it assumes a daily CPA
  time series per channel. This dataset has no such series: each row is a single campaign that
  already spans 5–30 days (`Duration`), aggregated to totals/rates — there is no way to recover a
  per-day CPA value from it without fabricating one. `power_analysis.py` therefore substitutes
  **campaigns per group** for CPA power (one CPA observation per campaign is the direct analog of
  one CPA observation per day) and **clicks per group** for conversion-rate power (the natural
  Fisher's-exact denominator). This is a deliberate, documented adaptation — see the module
  docstring in `power_analysis.py` and the caveat repeated in `executive_memo.md`.

## A note on what the analysis found

The values across `Campaign_Type` groups turned out to be extremely close (CPA within ~$7 of each
other, ROAS within 0.04x) — the statistical tests in Steps 4-6 confirm this is not just an
impression: CPA shows **no** significant differences at all (0 of 10 pairs), and while conversion
rate differences are technically significant after correction, every one is under 1% relative and
is only detectable because clicks are aggregated in the millions per group. This is a real,
reportable finding in its own right (see `executive_memo.md`), not a failure of the analysis.
