# LAB Proof — Statistical Analysis & Marketing Budget Allocation

**LAB:** In God We Trust, Everyone Else Bring the Data  
**Date:** November 24, 2026  
**Status:** Completed — Notebook executed successfully from top to bottom  
**Main deliverable:** `lab_statistical_analysis.ipynb`

## 1. Project Overview

This project applies statistical hypothesis testing to real-world advertising performance data to support a hypothetical monthly marketing budget decision of $500,000.

The analysis covers:

1. Dataset discovery, exploration, and cleaning.
2. Marketing performance metrics and visualization.
3. Pairwise statistical comparisons using Welch's t-test and Fisher's exact test.
4. Effect size analysis using Cohen's d.
5. Multiple-comparison correction using Bonferroni and Benjamini-Hochberg (BH-FDR).
6. Statistical power analysis and sample-size planning.
7. Bootstrap confidence intervals.
8. Illustrative marketing budget allocation and executive recommendations.

**Key distinction:** The dataset contains three advertising campaigns, not seven independent marketing channels. The final budget allocation is therefore an illustrative planning scenario, not a validated production recommendation.

## 2. Dataset and Input Evidence

**Dataset:** Sales Conversion Optimization  
**Source:** [Kaggle — Sales Conversion Optimization](https://www.kaggle.com/datasets/loveall/clicks-conversion-tracking)  
**Local source file:** `KAG_conversion_data.csv`  
**Cleaned output:** `outputs/marketing_data.csv`

The original download used an `.xls` filename, although the underlying file was comma-separated text. It was renamed to `.csv` and loaded using pandas.

### Dataset characteristics

| Property | Result |
|---|---|
| Advertising records | 1,143 |
| Original columns | 11 |
| Campaigns | 3 |
| Campaign IDs | 916, 936, 1178 |
| Missing values | None detected |
| Duplicate records | None detected |
| Revenue information | Unavailable |
| Date information | Unavailable |

The dataset includes advertising identifiers, campaign IDs, audience characteristics, impressions, clicks, advertising expenditure, and conversion counts.

Each row represents an advertising record rather than a daily or weekly observation.

### Data-quality limitations

During exploration, 72 records were identified in which approved conversions exceeded recorded clicks. Of these, 71 contained approved conversions despite having zero recorded clicks.

These observations were retained rather than silently removed because the underlying attribution definitions could not be verified.

Consequently, click-to-purchase conversion rates cannot be treated as conventional binomial probabilities.

For Fisher's exact test, the analysis instead uses a binary ad-level outcome: whether a record contains at least one approved purchase.

## 3. Code and Workflow Evidence

**Primary notebook:** [`lab_statistical_analysis.ipynb`](lab_statistical_analysis.ipynb)

The notebook follows the five LAB parts.

### Part 1 — Data Exploration

- Loaded and validated the source dataset.
- Standardized relevant column names.
- Checked missing values, duplicates, and invalid values.
- Calculated aggregate impressions, clicks, cost, and conversions.
- Derived CTR, CPA, and conversion-to-click ratios.
- Examined distributions, outliers, and variability.
- Saved the cleaned dataset and exploratory charts.

### Part 2 — Statistical Testing

- Conducted pairwise Welch's t-tests on advertisement-level CPA.
- Calculated Cohen's d effect sizes.
- Conducted additional t-tests on per-advertisement conversion-to-click ratios.
- Applied Fisher's exact test to ad-level purchase success.
- Compared significance results and documented test limitations.

### Part 3 — Multiple Comparisons

- Evaluated nine pairwise comparisons across three metric families.
- Applied Bonferroni correction.
- Applied BH-FDR correction.
- Compared corrections both within individual metric families and globally across all nine tests.

### Part 4 — Statistical Power

- Simulated CPA differences of 5%, 10%, 15%, and 20%.
- Evaluated hypothetical sample sizes of 30, 60, 90, 120, and 180 observations per campaign.
- Used 1,000 simulations per combination.
- Evaluated an 80% target power.
- Compared simulation assumptions with actual CPA variability.
- Estimated prospective sample-size requirements.

### Part 5 — Business Recommendations

- Summarized corrected statistical findings.
- Calculated bootstrap confidence intervals for aggregate CPA.
- Checked budget allocation constraints.
- Developed an illustrative seven-position allocation.
- Generated the executive memo.

## 4. Execution Proof — One Complete Run

**Execution environment:**

- Windows
- Visual Studio Code
- Jupyter Notebook
- Python 3.11 (bootcamp environment)

**Input:** `KAG_conversion_data.csv`

**Workflow:** Restart Jupyter kernel → Run All Cells → Review outputs.

**Execution result:** The completed notebook was executed from top to bottom without errors on November 24, 2026.

### Representative output: Aggregate CPA

Aggregate CPA is calculated using total advertising cost divided by total approved conversions, including advertising records without purchases.

| Campaign | Aggregate CPA | 95% Bootstrap CI |
|---|---:|---:|
| 916 | 6.238 | 3.919–9.728 |
| 936 | 15.811 | 12.048–20.938 |
| 1178 | 63.833 | 57.972–70.627 |

The CPA figures use the dataset's cost units; the original currency has not been independently verified.

**Evidence:** [`outputs/cpa_bootstrap_ci.csv`](outputs/cpa_bootstrap_ci.csv)

### Representative output: Welch's t-test

The following comparisons remained statistically significant after BH-FDR correction.

| Comparison | Lower mean ad-level CPA | Absolute difference | Cohen's d | BH-adjusted p-value |
|---|---|---:|---:|---:|
| 916 vs. 1178 | 916 | 54.150 | 1.316 | 5.49e-46 |
| 936 vs. 1178 | 936 | 50.422 | 1.164 | 1.96e-39 |

The comparison between campaigns 916 and 936 was not statistically significant under the original Welch test (p = 0.0928).

**Important:** These t-tests use advertisement-level CPA calculated only for records with approved purchases. They do not test the aggregate CPA measure in the preceding table.

**Evidence:** [`outputs/significant_cpa_findings.csv`](outputs/significant_cpa_findings.csv)

### Representative output: Fisher's exact test

The statistically significant BH-FDR comparisons showed:

| Comparison | Higher ad-level purchase success | Difference | BH-adjusted p-value |
|---|---|---:|---:|
| 916 vs. 1178 | 1178 | 17.64 percentage points | 0.0200 |
| 936 vs. 1178 | 1178 | 25.01 percentage points | 8.02e-16 |

Campaign 1178 had a higher proportion of advertising records with at least one approved purchase, despite its higher aggregate CPA.

This metric is not a conventional click-to-purchase conversion rate and is affected by differences in advertising spend and exposure.

**Evidence:** [`outputs/significant_ad_success_findings.csv`](outputs/significant_ad_success_findings.csv)

### Representative output: Multiple-Comparison Correction

| Correction method | Significant results |
|---|---:|
| Uncorrected | 6 of 9 |
| Global Bonferroni | 5 of 9 |
| Global BH-FDR | 6 of 9 |

The ad-level purchase success comparison between campaigns 916 and 1178 lost statistical significance under global Bonferroni correction.

- Uncorrected p-value: 0.01332.
- Global Bonferroni-adjusted p-value: 0.11988.
- Global BH-FDR-adjusted p-value: 0.01998.

This illustrates why correction methods matter when multiple comparisons are performed.

**Evidence:** [`outputs/correction_comparison.png`](outputs/correction_comparison.png)

### Representative output: Power Analysis

The hypothetical simulation produced:

| CPA difference | Power at 90 observations |
|---|---:|
| 5% | 58.5% |
| 10% | 99.2% |
| 15% | 100.0% |
| 20% | 100.0% |

The simulation assumed normally distributed CPA observations with a relative standard deviation of 15%.

Actual CPA values displayed substantially higher variability. An additional prospective calculation estimated that detecting a 5% CPA difference could require thousands of independent observations per group under the observed variability assumptions.

Because the dataset does not contain dates, simulated observations cannot be directly interpreted as real campaign days.

**Evidence:** [`outputs/power_analysis_cpa.png`](outputs/power_analysis_cpa.png)

## 5. Final Output — Budget Allocation Scenario

The LAB requires a hypothetical allocation of $500,000 per month, subject to minimum and maximum allocation constraints.

However, the available dataset contains only three campaigns and no revenue information.

A CPA/ROAS composite score could therefore not be calculated.

Instead, an illustrative allocation was generated using aggregate CPA rankings for the three observed campaigns, with four additional positions reserved for unassessed channels.

| Budget position | Share | Amount | Status |
|---|---:|---:|---|
| Campaign 916 | 15.0% | $75,000 | Conditional pilot planning |
| Campaign 936 | 10.0% | $50,000 | Conditional pilot planning |
| Campaign 1178 | 5.0% | $25,000 | Conditional pilot planning |
| Unassessed channel 1 | 17.5% | $87,500 | Uncommitted reserve |
| Unassessed channel 2 | 17.5% | $87,500 | Uncommitted reserve |
| Unassessed channel 3 | 17.5% | $87,500 | Uncommitted reserve |
| Unassessed channel 4 | 17.5% | $87,500 | Uncommitted reserve |
| **Total** | **100%** | **$500,000** | |

### Budget validation

- Total allocation: 100%.
- Total planned budget: $500,000.
- Minimum position share: 5%.
- Maximum position share: 17.5%.
- All positions satisfy the LAB's 5%–35% constraints.

The observed campaigns receive a combined **conditional pilot planning envelope of $150,000**.

The remaining **$350,000 stays uncommitted**.

These values are illustrative rather than statistically optimized. The available historical data does not establish that the campaigns can absorb the proposed spending while maintaining their observed CPA.

**Budget evidence:** [`outputs/budget_allocation.csv`](outputs/budget_allocation.csv)

**Final business deliverable:** [`outputs/executive_memo.md`](outputs/executive_memo.md)

## 6. Failure Encountered and Resolution

### Issue: Floating-point precision in budget validation

During the budget allocation step, the validation initially failed with:

```text
AssertionError

assert budget_allocation["allocation_share"].between(
    0.05, 0.35
).all()
```

**Root cause:** Floating-point arithmetic caused an allocation intended to equal exactly 5% to be represented internally as a value marginally below `0.05`.

The strict boundary comparison therefore failed.

**Resolution:** The validation was updated to use a small numerical tolerance:

```python
tolerance = 1e-10

assert (
    (budget_allocation["allocation_share"] >= MIN_SHARE - tolerance)
    &
    (budget_allocation["allocation_share"] <= MAX_SHARE + tolerance)
).all()
```

After the correction, the allocation validation succeeded.

A subsequent complete notebook execution finished without errors.

### Additional analytical challenge: Missing and inconsistent data

The source dataset did not match all assumptions of the original LAB template.

Specifically:

- Revenue and ROAS could not be calculated.
- Daily or weekly time-based metrics were unavailable.
- Only three campaigns were available.
- Some conversion counts exceeded recorded clicks.
- Individual-ad CPA was undefined for ads without approved purchases.

**Resolution:** The analysis explicitly documented these limitations, adapted Fisher's exact test to ad-level purchase success, used aggregate CPA for the business assessment, and separated hypothetical simulations from observed results.

No revenue figures, campaign dates, or additional observed marketing channels were fabricated.

## 7. Evidence Files and Reviewer Navigation

The following files provide the main reproducibility and output evidence.

| File | Purpose |
|---|---|
| [`lab_statistical_analysis.ipynb`](lab_statistical_analysis.ipynb) | Complete analysis, statistical tests, simulations, and generated outputs |
| [`outputs/marketing_data.csv`](outputs/marketing_data.csv) | Cleaned dataset |
| [`outputs/group_metrics_overview.png`](outputs/group_metrics_overview.png) | Marketing performance overview |
| [`outputs/group_distributions.png`](outputs/group_distributions.png) | Distributions and variability |
| [`outputs/metric_comparison_heatmap.png`](outputs/metric_comparison_heatmap.png) | Pairwise CPA p-value heatmap |
| [`outputs/rate_comparison.png`](outputs/rate_comparison.png) | Ad-level purchase success comparison |
| [`outputs/correction_comparison.png`](outputs/correction_comparison.png) | Multiple-comparison correction results |
| [`outputs/power_analysis_cpa.png`](outputs/power_analysis_cpa.png) | Statistical power curves |
| [`outputs/cpa_bootstrap_ci.csv`](outputs/cpa_bootstrap_ci.csv) | Aggregate CPA confidence intervals |
| [`outputs/budget_allocation.csv`](outputs/budget_allocation.csv) | Illustrative budget allocation |
| [`outputs/executive_memo.md`](outputs/executive_memo.md) | Final CMO decision memo |

### Suggested review order

1. Read this `lab_proof.md` for the workflow, results, and limitations.
2. Open `lab_statistical_analysis.ipynb` to inspect the calculations and notebook outputs.
3. Review the charts in `outputs/` for visual evidence.
4. Read `outputs/executive_memo.md` for the business conclusions.
5. Consult `README.md` for environment setup and execution instructions.

## 8. Reproducibility

To reproduce the analysis:

1. Clone or download the repository.
2. Set up a Python environment with the required scientific Python packages, including NumPy, pandas, SciPy, Matplotlib, Seaborn, and Jupyter.
3. Ensure `KAG_conversion_data.csv` is available in the expected project location.
4. Open `lab_statistical_analysis.ipynb` in VS Code or Jupyter.
5. Select the correct Python kernel.
6. Restart the kernel and run all cells in order.
7. Inspect the generated files in `outputs/`.

The statistical simulations use fixed random seeds for reproducibility.

No external API keys or paid services are required for the analysis.

## 9. Final Conclusions

The analysis identifies substantial observed performance differences among three advertising campaigns.

Campaign 916 has the lowest aggregate CPA, while campaign 1178 shows higher ad-level purchase success but substantially higher acquisition cost.

Multiple-comparison corrections demonstrate that some findings depend on the chosen statistical error-control method.

Bootstrap confidence intervals and power analysis illustrate why statistical uncertainty and data variability must be considered alongside observed performance.

**Final recommendation:** Do not immediately commit the full $500,000 monthly budget based on these data alone.

Instead, validate promising campaigns through controlled, limited-budget experiments, obtain attributable revenue and time-series data, and evaluate all intended marketing channels before making a production allocation decision.

**LAB outcome:** The statistical workflow, corrected hypothesis tests, power analysis, confidence intervals, illustrative budget model, and executive memo were completed and executed successfully.