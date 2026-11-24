# Marketing Campaign Statistical Analysis

Analysis of five anonymised marketing campaigns to assess CPA and conversion performance, test whether observed differences are statistically reliable, and develop a cautious, illustrative **$500,000 monthly budget allocation**.
This repository contains only the materials for the Ironhack Statistical Analysis Lab, including the notebook, documentation, processed data, visualisations, and executive memo.

## How to run

**Main notebook:** `lab_statistical_analysis_STUDENT.ipynb`

**Generated outputs:** `outputs/` — processed CSV, six visualisations, and executive memo.

**Reviewer evidence:** `lab_proof.md` — workflow, findings, limitations, and reproduction check.

1. Open `lab_statistical_analysis_STUDENT.ipynb` in VS Code or Jupyter with a Python kernel.
2. Download the [Criteo Attribution Dataset](https://huggingface.co/datasets/criteo/criteo-attribution-dataset) from Hugging Face and place `criteo_attribution_dataset.tsv.gz` in the project root. The source archive is excluded from GitHub because of its size. The processed data is available in `outputs/marketing_data.csv`.
3. Install any missing Python dependencies used by the notebook (`numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, and `tabulate`). The `tabulate` package is required to generate the Markdown confidence-interval table.
4. **Restart Kernel → Run All**. Check that the notebook completes without errors and regenerates the files in `outputs/`.

## Data preparation and sampling

The Criteo Attribution Dataset was initially explored using the full dataset. A 2% sample was subsequently used to reduce processing time. The final statistical analysis and visualisations are based on the sampled data.

The analysis covers five anonymised campaigns, with 155 campaign-day observations. Each campaign has 31 daily observations covering day indices 0–30, with no missing days within that range.
One campaign has 30 valid CPA observations because CPA is undefined when conversions are zero.
Data preparation included checking missing values and data types. The sampled dataset contained 22 numeric columns (`int64` and `float64`) with zero missing values, so no missing-value imputation was required. Timestamps were stored as integers and used to derive day indices. Impressions, clicks, conversions and costs were then aggregated by campaign and day. The processed dataset is saved in `outputs/marketing_data.csv`.


## Method and results
The notebook builds daily campaign metrics, visualises CPA and conversion-rate distributions, runs pairwise Welch t-tests with Cohen's d and Fisher's exact tests, applies Bonferroni and BH-FDR corrections, estimates simulated statistical power, and calculates bootstrap confidence intervals.
Conversion rate is consistently calculated as conversions divided by clicks. Click-through rate (CTR) is calculated as clicks divided by impressions. The executive memo includes bootstrap 95% confidence intervals for mean daily CPA and conversion rate across all five campaigns.

The power analysis estimates the additional days needed to reach 80% statistical power using a simulation-based search up to 365 days. All nine statistically significant CPA comparisons achieved at least 80% simulated power with 31 days, requiring zero additional days under the model assumptions.

**Key results:** 9/10 CPA comparisons and 9/10 conversion-rate comparisons were significant; all 9 remained significant after both multiple-comparison corrections. Campaign `30801593` had the lowest observed mean daily CPA, while `10341182` had the highest conversion rate (23.64%). See `lab_proof.md` for the evidence and `outputs/executive_memo.md` for the decision rationale.


**Budget recommendation:** A provisional $500,000 monthly budget was allocated across five campaigns based on CPA rankings. Campaign `30801593` received the highest allocation (33.33%, approximately $166,667). All allocations fall within the required 5%–35% limits. ROAS was excluded because revenue data is unavailable.

## File map
| Path | Purpose |
|---|---|
| `lab_statistical_analysis_STUDENT.ipynb` | Complete reproducible analysis |
| `criteo_attribution_dataset.tsv.gz` | Source data archive |
| `instructions.md` | Lab instructions |
| `lab_proof.md` | Reviewer entry point: workflow, evidence, outputs, limitations |
| `outputs/marketing_data.csv` | Processed analysis data |
| `outputs/group_metrics_overview.png` | Campaign metrics overview |
| `outputs/group_distributions.png` | Daily metric distributions |
| `outputs/metric_comparison_heatmap.png` | Pairwise CPA p-values |
| `outputs/rate_comparison.png` | Campaign conversion rates |
| `outputs/correction_comparison.png` | Significance before and after corrections |
| `outputs/power_analysis_cpa.png` | Simulated CPA detection power |
| `outputs/executive_memo.md` | Findings, budget scenario and caveats |
| `reflection.md` | Optional learning reflection, if completed |

## Important limitations
Costs are anonymised and revenue is unavailable. The CPA ranking is therefore based on **anonymised cost units**, not verified dollars; ROAS and profit cannot be calculated. The $500,000 allocation is illustrative and must be tested against actual cost, revenue and campaign capacity before implementation. Power estimates rely on simulated assumptions.

For reviewer evidence and the main conclusions, start with **[`lab_proof.md`](lab_proof.md)**.
