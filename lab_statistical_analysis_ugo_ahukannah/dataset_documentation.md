# Dataset Documentation

**LAB | In God we trust, everyone else bring the data** &mdash; Step 1
**Author:** Nnanyelugo Ahukannah

## Candidates evaluated

The brief asks for a real marketing dataset from Kaggle or Hugging Face with
multiple comparable groups and enough volume per group. Kaggle needs an API
credential that is not on this machine, so the search ran on Hugging Face. Three
candidates were assessed against what the analysis actually needs &mdash; group
structure, conversion outcomes, and a **cost** column, because CPA is impossible
without one.

| Candidate | Rows | Real or simulated | Has cost? | Has revenue? | Verdict |
|---|---|---|---|---|---|
| **`criteo/criteo-attribution-dataset`** | 16.5M | **Real** &mdash; Criteo production ad-serving logs, 30 days | yes | no | **Selected** |
| `jason1966/alinaboulsi_digital-marketing-performance-dataset` | 30k | Simulated, by its own README | yes | yes | Secondary, ROAS only |
| `datametrik/b2b-digital-marketing-performance-benchmarks` | small | Benchmark aggregates | partial | partial | Rejected &mdash; aggregates, no per-observation rows to test |

## Selected: Criteo Attribution Dataset

| | |
|---|---|
| **Source** | Hugging Face &mdash; https://huggingface.co/datasets/criteo/criteo-attribution-dataset |
| **Origin** | Criteo's live ad-serving systems, released for attribution-modelling research |
| **Size** | 16,468,027 impressions over 30 days; **400,000 streamed** for this analysis |
| **Groups** | 661 campaigns in the slice; the **6 largest** (5,808&ndash;21,680 impressions each) are compared |
| **Licence** | Public, ungated |

**Why this one.** It is genuinely observational &mdash; real auctions, real
impressions, real conversions &mdash; which is what the brief asks for and what
makes the statistics worth doing. It carries `campaign` (the groups), `click` and
`conversion` (binary outcomes for Fisher's exact test), and `cost` (a continuous
per-impression measurement for t-tests). Volume is far beyond the "hundreds to
thousands per group" the brief wants.

**Why it was streamed, not downloaded.** The full release is roughly 800MB. The
analysis needs a slice, and `datasets` can stream one in a few seconds, so
`fetch_dataset.py` takes the first 400,000 impressions rather than pulling the
lot.

## The three limitations that shape every conclusion

**1. Cost is anonymised.** Criteo scales the cost column by an undisclosed
constant, so the figures are not currency. Because the scaling is uniform,
*ratios* between campaigns are meaningful and absolute values are not. Every CPA
in this analysis is quoted in "Criteo cost units" and never in money.

**2. There is no revenue column, so ROAS cannot be computed from this data.**
That is not an oversight in the release; ad revenue is commercially sensitive and
essentially never published alongside real spend. Rather than skip a metric the
brief asks for, or invent a revenue column on real data, ROAS is computed from a
clearly-labelled **synthetic** secondary set and kept in its own section. It is
never mixed with the Criteo results and never drives a recommendation.

**3. This is observational, not an experiment.** Campaigns were not randomly
assigned to audiences. They serve different advertisers, products and targeting,
so a difference in conversion rate between two campaigns is a *description* of
what happened, not evidence that moving budget would reproduce it. This is the
single most important caveat in the whole lab and it is repeated in the memo.

## Secondary set (ROAS only)

`jason1966/alinaboulsi_digital-marketing-performance-dataset`, 30,000 rows across
six platforms. Its own `README_DATASET.md` states plainly: *"This dataset is
synthetically generated for educational dashboards and analytics practice... It
does not represent real client data."* It is used for exactly one figure &mdash;
ROAS by platform &mdash; and is labelled SYNTHETIC everywhere it appears.

## What each field is used for

| Field | Type | Used for |
|---|---|---|
| `campaign` | categorical | the comparison groups |
| `conversion` | binary | conversion rate; Fisher's exact test |
| `click` | binary | click-through rate |
| `cost` | continuous | cost per impression; Welch's t-test; CPA numerator |
| `cpo` | continuous | **deliberately unused** &mdash; only 8&ndash;510 distinct values per campaign, so it is a campaign-period attribute repeated down the rows, not an independent measurement |
| `attribution`, `click_pos`, `click_nb` | mixed | retained in the extract for reproducibility; not analysed |
