# Lab Proof — Statistical Analysis of Marketing Campaigns

## Reviewer entry point
Run `lab_statistical_analysis_STUDENT.ipynb` from top to bottom. The notebook loads the source data, constructs daily campaign metrics, performs statistical tests and simulations, and writes the figures and memo to `outputs/`.

## Input and workflow
- **Input:** `criteo_attribution_dataset.tsv.gz` (source archive); processed analysis data: `outputs/marketing_data.csv`.
- **Groups:** Five anonymised campaign IDs, each with 31 campaign-day observations (155 total); one campaign has 30 valid CPA observations. No campaign-days are missing within the observed day-index range.
- **Metrics:** CPA, click-through rate (clicks / impressions) and conversion rate (conversions / clicks); campaign totals and daily distributions.
- **Tests:** Pairwise Welch t-tests and Cohen's d for daily CPA and conversion rate; Fisher's exact tests for converted/non-converted clicks; Bonferroni and Benjamini–Hochberg (BH-FDR) corrections; simulated power and bootstrap 95% confidence intervals.
- **Decision output:** Provisional $500,000 allocation based on CPA rankings, prioritising lower observed CPA, with a minimum of 5% and maximum of 35% per campaign. ROAS could not be included because revenue is unavailable. See `outputs/executive_memo.md`.

## Evidence and findings
- **Pairwise CPA:** 9 of 10 comparisons significant before and after both corrections.
- **Conversion rates:** 9 of 10 comparisons significant with Welch's t-test and Fisher's exact test; zero disagreements between the tests.
- **Non-significant CPA pair:** Campaigns `5061834` and `17686799` (p ≈ 0.7597).
- **Non-significant conversion pair:** Campaigns `5061834` and `30801593` (Fisher p ≈ 0.3109).
- **Highest observed conversion rate:** `10341182` (23.64%); **lowest:** `17686799` (5.17%).
- **Lowest observed mean daily CPA:** `30801593` (~0.0012 in anonymised cost units).
- **Confidence intervals:** Bootstrap 95% confidence intervals were calculated for mean daily CPA and mean daily conversion rate across all five campaigns (10 intervals total). The complete table is included in `outputs/executive_memo.md`.
- **Power simulation:** The notebook estimates additional days needed to reach 80% statistical power using a simulation-based search up to 365 days. All nine significant CPA comparisons achieved at least 80% simulated power with 31 days, requiring zero additional days under the model assumptions. Smaller hypothetical effects (5–10%) may require more observations.
### Decision considerations
- **Ranking fairness:** Campaigns 5061834 and 17686799 have no significant CPA difference (p ≈ 0.7597), despite receiving different rankings.
- **Budget scalability:** Campaign 30801593 receives the highest allocation, but its ability to maintain the same CPA with increased spending is unverified.
- **Practical significance:** Statistical significance does not necessarily imply financial importance. Actual costs, revenue and profitability must be considered.

## Illustrative budget allocation
| Campaign | Allocation | USD |
|---|---:|---:|
| 30801593 | 33.33% | $166,666.67 |
| 10341182 | 26.67% | $133,333.33 |
| 15398570 | 20.00% | $100,000.00 |
| 5061834 | 13.33% | $66,666.67 |
| 17686799 | 6.67% | $33,333.33 |
| **Total** | **100%** | **$500,000.00** |

## Final outputs
- `outputs/marketing_data.csv`
- `outputs/group_metrics_overview.png`
- `outputs/group_distributions.png`
- `outputs/metric_comparison_heatmap.png`
- `outputs/rate_comparison.png`
- `outputs/correction_comparison.png`
- `outputs/power_analysis_cpa.png`
- `outputs/executive_memo.md`

## Limitation encountered
The dataset uses anonymised costs and lacks revenue. Therefore, CPA cannot be interpreted as a verified dollar cost, and ROAS, profit and financial scalability cannot be established. The proposed budget is a **scenario for further testing**, not a validated investment decision. Results may also depend on attribution assumptions and dependence among observations.

## Reproduction check
The notebook was executed from top to bottom in VS Code/Jupyter without errors. The generated charts, cleaned dataset and executive memo were verified in `outputs/`. The heatmap scale, CPA ranking logic and decision considerations were updated following feedback.