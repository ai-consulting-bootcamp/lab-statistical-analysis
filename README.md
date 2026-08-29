# Marketing Statistical Analysis

Statistical validation of paid search performance to support a $500K marketing budget decision.

## Business Question

How should a $500K paid search budget be allocated across the available match types based on acquisition efficiency, return and the strength of the evidence behind the observed differences?

The analysis uses five months of historical paid search data from July to November 2021.

## Campaign Snapshot

| Metric | Result |
|---|---:|
| Impressions | 2.67M |
| Clicks | 924,503 |
| Conversions | 95,996 |
| CTR | 34.56% |
| Conversion rate | 10.38% |
| CPC | $0.69 |
| CPA | $6.62 |
| Revenue | $561,960 |
| Media cost | $635,372 |
| ROAS | 0.884 |
| ROI | -11.55% |

The campaign generated strong traffic and conversion volume, but reported revenue did not cover media spend during the period analysed.

## Performance by Match Type

| Match type | Conversions | CPA | ROAS | ROI | Recommendation |
|---|---:|---:|---:|---:|---|
| One to one | 72,388 | $6.39 | 0.895 | -10.5% | Maintain |
| Exact | 15,038 | $7.00 | 0.886 | -11.4% | Optimise and test |
| Phrase | 8,570 | $7.86 | 0.812 | -18.8% | Reduce |

One to one provides the strongest current base, combining the largest conversion volume with the lowest CPA.

Exact performs relatively close and remains a good candidate for optimisation and testing.

Phrase has the weakest acquisition economics and should receive less budget while the reasons behind its performance are investigated.

## What the Statistical Analysis Added

The campaign KPIs showed the initial performance pattern. Statistical testing helped determine how much confidence I could place in those differences.

The CPA advantage of One to one over Exact and Phrase remained statistically significant after correcting for multiple comparisons. The difference against Exact was relatively small, while the difference against Phrase was larger.

Conversion rate differences were also statistically significant, but their size was very small. This is important because a large dataset can make small differences statistically detectable without making them commercially important.

The analysis therefore considers statistical evidence together with CPA, ROAS, ROI, conversion volume and business relevance.

## Data Validation

Before running the analysis, I recalculated the main marketing KPIs from impressions, clicks, conversions, cost and revenue.

The conversion rate provided in the original dataset did not match `Conversions / Clicks` in 160 of 190 records. Recalculating the metrics ensured that the statistical analysis used consistent KPI definitions.

## $500K Budget Recommendation

| Match type | Budget | Action |
|---|---:|---|
| One to one | $200,000 | Maintain |
| Exact | $200,000 | Optimise and test |
| Phrase | $100,000 | Reduce |
| **Total** | **$500,000** | |

This is a staged planning allocation rather than a recommendation to immediately spend the full $500K.

All three match types had negative historical ROI. I would therefore protect the strongest area, retain enough budget to test Exact and limit exposure to Phrase while investigating its weaker performance.

Additional budget should only be released when improvements are both statistically supported and commercially meaningful.

## Analysis

The project includes:

| File | Purpose |
|---|---|
| `notebooks/data_exploration.ipynb` | Data validation, KPI calculation and exploratory analysis |
| `notebooks/statistical_analysis.ipynb` | Statistical comparison of campaign performance |
| `notebooks/power_analysis.ipynb` | Sample size and statistical power analysis |
| `executive_memo.md` | Marketing findings and budget recommendation |
| `reflection.md` | Practical reflection on using statistics in marketing analysis |
| `outputs/` | Charts and statistical results |
| `data/marketing_data.csv` | Prepared dataset used in the analysis |

## Statistical Approach

The analysis uses independent tests for CPA and conversion performance, effect sizes, corrections for multiple comparisons, bootstrap confidence intervals and power analysis.

The purpose of these methods is not to replace the marketing KPIs, but to test how strongly the available evidence supports the differences observed in them.

## How to Run

Create the environment and install the project dependencies:

```bash
conda create -n bootcamp-env python=3.11
conda activate bootcamp-env
pip install -r requirements.txt
````

Run the notebooks in this order:

```text
1. notebooks/data_exploration.ipynb
2. notebooks/statistical_analysis.ipynb
3. notebooks/power_analysis.ipynb
```

## Limitations

The analysis is based on historical observational data, so it identifies performance differences but does not establish what caused them.

The dataset does not include product margin, customer lifetime value, search terms, bids or detailed attribution. These would be required before setting a true profitability target or break even CPA.

Historical performance should also not be assumed to scale linearly as budget increases.