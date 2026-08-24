# Step 1: Dataset Selection

## Dataset

- **Name:** Marketing A/B Testing
- **Source:** Kaggle
- **URL:** https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing
- **File used:** `data/marketing_AB.csv` (provided directly for this lab; 588,101 rows, 7 columns)

## Why this dataset

It's a real, publicly documented marketing experiment: users were shown either actual ad
creative (`test group = "ad"`) or a public service announcement (`test group = "psa"`, the
control), and their conversion outcome was tracked along with how many ads they were exposed
to and when. That gives a genuine binary outcome (`converted`) and a genuine continuous
exposure metric (`total ads`) to run statistical tests on — not synthetic data.

## Columns

| Column | Type | Description |
|---|---|---|
| `user id` | int | Unique user identifier |
| `test group` | categorical (2 levels: `ad`, `psa`) | Experiment arm the user was assigned to |
| `converted` | bool | Whether the user converted (e.g., made a purchase) |
| `total ads` | int | Number of ads shown to the user during the study |
| `most ads day` | categorical (7 levels: Monday–Sunday) | Day of week on which the user was shown the most ads |
| `most ads hour` | int (0–23) | Hour of day on which the user was shown the most ads |

## Known limitation vs. the lab's ideal dataset

The lab's instructions describe a dataset with **cost, revenue, impressions, and clicks** per
channel, so that CPA, ROAS, and CTR can be calculated directly. This dataset has **none of
those fields** — it only has ad exposure counts and a conversion flag, at the individual-user
level, with no monetary or per-channel spend/revenue data.

**Decision (confirmed with the analyst before proceeding):** rather than inventing cost/revenue
numbers that don't exist in the source data, the analysis is adapted to use what is genuinely
present:

- **Grouping variable (in place of "channel"):** `most ads day` — 7 distinct groups
  (Monday–Sunday), which satisfies and exceeds the lab's "at least 3–5 groups" requirement.
- **Continuous metric (in place of CPA/ROAS):** `total ads` — ad exposure per user, compared
  across day-of-week groups with t-tests and Cohen's d.
- **Binary outcome (as specified):** `converted` — compared across day-of-week groups with
  Fisher's exact test, exactly as the lab describes for binary outcomes.
- **Primary experimental comparison:** `test group` (`ad` vs. `psa`) — the actual designed
  A/B test in this dataset, used as the headline business finding (does showing ads increase
  conversion vs. a PSA control?).

CPA, ROAS, and CTR are **not** calculated anywhere in this analysis because the underlying
cost/revenue/impression data does not exist in the source file. This is called out again in
`executive_memo.md` under Statistical Caveats.
