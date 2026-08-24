# W7D5_LAB_In_God_we_trust_everyone_else_bring_the_data
- Week 7 / Day 5
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-24
---

# Marketing Channel Statistical Analysis

This project analyzes marketing campaign performance across five channels:

- Email
- PPC
- Referral
- SEO
- Social Media

The analysis compares customer-level conversion rates, applies Fisher's exact tests, corrects for multiple comparisons, and performs a simulation-based power analysis.

## Key Findings

- The dataset contains 8,000 customer-level records.
- Referral had the highest observed conversion rate: 88.31%.
- Social Media had the lowest observed conversion rate: 86.83%.
- No channel pair had a statistically significant conversion-rate difference.
- Results remained non-significant after Bonferroni and Benjamini-Hochberg FDR corrections.
- The power analysis showed that small CPA differences need more observations to detect reliably.

## Project Structure

```text
lab_statistical_analysis_An...
|
|-- data/
|   `-- digital_marketing_campaign_dataset.csv
|
|-- graphs/
|   |-- average_ad_spend_by_channel.png
|   |-- average_conversion_rate_by_channel.png
|   |-- correction_comparison.png
|   |-- metric_comparison_heatmap.png
|   |-- power_analysis_cpa.png
|   `-- rate_comparison.png
|
|-- reports/
|   |-- executive_memo.md
|   `-- outputs.md
|
|-- data_exploration.ipynb
|-- statistical_analysis.ipynb
|-- instructions.md
|-- reflection.md
|-- README.md
`-- rubric.md
```

## Files

- `data/digital_marketing_campaign_dataset.csv` — Source dataset used in the analysis.
- `data_exploration.ipynb` — Dataset loading, cleaning, exploration, and summary visualizations.
- `statistical_analysis.ipynb` — Fisher's exact tests, multiple-comparisons correction, and power analysis.
- `graphs/` — Saved charts created during the analysis.
- `reports/executive_memo.md` — Business-focused summary, recommendations, and statistical caveats.
- `reports/outputs.md` — Saved analysis outputs and notes.
- `reflection.md` — Personal reflection on findings, limitations, and learning.
- `instructions.md` — Lab instructions and requirements.
- `rubric.md` — Assessment rubric.

## How to Run

1. Clone this repository.
2. Install Python 3 and Jupyter Notebook or VS Code with the Jupyter extension.
3. Install required libraries:

```bash
pip install pandas numpy matplotlib scipy seaborn jupyter
```

4. Open and run the notebooks in this order:

```text
1. data_exploration.ipynb
2. statistical_analysis.ipynb
```

5. Generated charts will be saved in the `graphs/` folder.

## Methods Used

- Customer-level conversion-rate calculation
- Fisher's exact test for pairwise channel comparisons
- Bonferroni correction
- Benjamini-Hochberg false discovery rate correction
- Simulation-based power analysis for CPA differences

## Notes and Limitations

The dataset does not include a time column, so power is described using customers per channel rather than days. Conversion rates alone should not determine budget allocation; future analysis should also include CPA, revenue, profit, ROAS, and customer lifetime value.
