# Lab proof · In God we trust, everyone else bring the data

**Student:** Jaime Garate Marquerie · Ironhack AI Consulting, Week 7 Day 5 · **Start here**, then [`executive_memo.md`](executive_memo.md).

## 1. Workflow (code)

| Script | Lab part | What it does |
|---|---|---|
| [`data_exploration.py`](data_exploration.py) | Part 1, Steps 1–3 | Loads the Kaggle CSV, cleans money and date fields, derives conversions, revenue, CTR, CPA and ROAS, and aggregates by channel and by day |
| [`statistical_analysis.py`](statistical_analysis.py) | Parts 2–3, Steps 4–6 | t-tests and Cohen's d on daily CPA and ROAS, Fisher's exact test on conversions, Bonferroni and Benjamini-Hochberg corrections |
| [`power_analysis.py`](power_analysis.py) | Part 4, Step 7 + Part 5 | Simulated power curves (1,000 runs per cell), minimum days for 80 % power, bootstrap CIs, ranking and bounded allocation |

## 2. One run: input → evidence → output

- **Input:** `marketing_campaign_dataset.csv` from https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset.
  - 200,000 rows, 16 columns.
  - SHA-256 `f06c1b95a8207b4631c35e6b83b4a2a7872892a8bfa133967e1e7ec401c7bb60`.
  - The student downloaded it from Kaggle on 24 Nov 2026.
- **Commands:**
  1. `python data_exploration.py marketing_campaign_dataset.csv`
  2. `python statistical_analysis.py`
  3. `python power_analysis.py`
- **Evidence:**
  - console logs in [`proof/`](proof/): `run_1_exploration.txt`, `run_2_statistics.txt`, `run_3_power.txt`;
  - every result table in [`results/`](results/);
  - every chart in [`figures/`](figures/).
- **Final output:** [`executive_memo.md`](executive_memo.md).
  - CPA: no channel is better (0 of 15 tests).
  - ROAS: 2 false positives that disappear after correction.
  - Conversion rate: 9 differences that are significant but negligible.
  - Recommendation: equal budget split plus an A/B test.

## 3. Failures and limitations hit

1. **A rule broke in the allocation step.** The first version clipped weights to 10–25 % and renormalized once, which left Instagram at **9.8 %**, below the 10 % floor. Fixed with iterative clipping; the final allocation respects 10.0–24.5 %.
2. **The dataset gives rates, not counts.** Conversions had to be reconstructed as rate × clicks. Rates are rounded to 2 decimals per campaign, so the Fisher counts are approximate.
3. **The lab's power simulation assumes a daily CPA spread of 15 %.** The observed spread is 8.6 %. The script keeps the lab's 15 % as instructed and prints the observed value. The memo's minimum detectable effect ($5.10, 1.8 %) uses the observed spread.
4. **The data looks synthetic:** balanced groups, flat CTR of 10 %, no seasonality. That limits what the memo can claim about real channels, and the memo says so.
5. **Kaggle cannot be reached from the tutor's sandbox.** The student downloaded the file; the tutor processed a staged copy.

## 4. How AI tools were used

Claude (Anthropic), acting as tutor, chose the dataset, wrote and ran the three scripts, and drafted the memo. The student downloaded the data and reviewed the conclusions. The scripts were first tested on mock data with the same columns, then run on the real file.
