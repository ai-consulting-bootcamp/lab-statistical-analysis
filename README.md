# In God We Trust, Everyone Else Bring The Data

## Marketing Channel Statistical Analysis

**Track:** Module 5 — Evaluation & Strategy  
**Lab:** In God We Trust, Everyone Else Bring The Data  
**Status:** Completed

## Project Overview

This project analyzes marketing channel performance for a simulated e-commerce company.

The objective is to use statistical analysis to compare six marketing platforms and provide a data-driven recommendation for allocating a $500,000 monthly marketing budget.

The analysis covers:

- Marketing performance metrics
- CPA, ROAS and conversion rates
- Pairwise statistical comparisons
- Cohen's d effect sizes
- Fisher's exact tests
- Bonferroni correction
- Benjamini-Hochberg FDR correction
- Statistical power analysis
- Bootstrap confidence intervals
- Budget allocation recommendations
- Executive business recommendations

## Platforms Analyzed

The analysis compares:

- Google Search
- Google Display
- Meta
- LinkedIn
- Snapchat
- TikTok

## Key Findings

Google Search is the strongest-performing platform in the analysis.

It has:

- The lowest aggregate CPA
- The highest ROAS
- The highest conversion rate
- The highest profit
- The highest composite performance score

The statistical analysis found significant differences between several platforms. These findings remained significant after both Bonferroni and Benjamini-Hochberg corrections.

The power analysis indicates that the current 90-day dataset has strong power for detecting differences of approximately 10% or larger, but is insufficient for reliably detecting a 5% CPA difference.

The analysis therefore distinguishes between statistical significance and practical business significance.

## Project Structure

```text
.
├── data/
│   └── processed/
│       └── marketing_data_clean.csv
│
├── results/
│   ├── figures/
│   │   ├── group_metrics_overview.png
│   │   ├── group_distributions.png
│   │   ├── metric_comparison_heatmap.png
│   │   ├── rate_comparison.png
│   │   ├── correction_comparison.png
│   │   └── power_analysis_cpa.png
│   │
│   └── tables/
│       ├── platform_summary.csv
│       ├── cpa_ttest_results.csv
│       ├── conversion_summary.csv
│       ├── fisher_exact_results.csv
│       ├── cpa_multiple_comparisons.csv
│       ├── fisher_multiple_comparisons.csv
│       ├── multiple_comparisons_summary.csv
│       ├── power_analysis_results.csv
│       ├── minimum_sample_size.csv
│       ├── cpa_confidence_intervals.csv
│       └── budget_allocation.csv
│
├── src/
│   ├── inspect_dataset.py
│   ├── data_exploration.py
│   ├── create_visualizations.py
│   ├── statistical_analysis.py
│   ├── multiple_comparisons.py
│   ├── power_analysis.py
│   └── business_recommendations.py
│
├── executive_memo.md
├── instructions.md
├── rubric.md
└── README.md


How to Run

Run the scripts from the project root directory.

1. Data exploration
python src/inspect_dataset.py
python src/data_exploration.py
2. Create visualizations
python src/create_visualizations.py
3. Statistical analysis
python src/statistical_analysis.py

This performs:

Pairwise CPA t-tests
Cohen's d calculations
Fisher's exact tests
Statistical significance testing
Comparison visualizations
4. Multiple comparisons correction
python src/multiple_comparisons.py

This applies:

Bonferroni correction
Benjamini-Hochberg FDR correction
5. Power analysis
python src/power_analysis.py

This evaluates statistical power for different effect sizes and sample sizes.

6. Business recommendations
python src/business_recommendations.py

This generates:

Bootstrap confidence intervals
Platform performance rankings
$500K monthly budget allocation
Executive memo
Main Deliverables
Data Exploration

src/data_exploration.py

Produces the cleaned dataset and platform-level performance metrics.

Statistical Analysis

src/statistical_analysis.py

Produces pairwise comparisons using t-tests and Fisher's exact tests.

Multiple Comparisons

src/multiple_comparisons.py

Controls for multiple hypothesis testing using Bonferroni and Benjamini-Hochberg FDR.

Power Analysis

src/power_analysis.py

Evaluates whether the available data is sufficient to detect meaningful CPA differences.

Business Recommendations

src/business_recommendations.py

Translates the statistical findings into business recommendations and budget allocation.

Executive Memo

executive_memo.md

Contains the executive-level interpretation of the analysis, recommendations and statistical caveats.

Statistical Approach

The analysis uses:

Independent two-sample t-tests for continuous CPA comparisons
Cohen's d for practical effect size
Fisher's exact test for conversion-rate comparisons
Bonferroni correction for conservative family-wise error control
Benjamini-Hochberg FDR correction
Bootstrap confidence intervals
Simulation-based statistical power analysis

A significance threshold of:

alpha = 0.05

is used throughout the analysis.

Important Caveats

Statistical significance does not automatically imply business significance.

The dataset represents observed marketing performance and does not by itself establish causal relationships between marketing platform and business outcomes.

Budget recommendations should therefore be treated as a data-driven starting point and validated through controlled experiments, incremental testing and continued monitoring.

The power analysis also shows that detecting smaller effects requires substantially more observations.

Final Recommendation

Google Search should receive the highest priority because it demonstrates the strongest overall performance across CPA, ROAS, conversion rate and profit.

The remaining platforms should not necessarily be eliminated solely because of weaker performance. Instead, their budgets should be monitored and optimized through controlled experiments, with particular attention to incremental ROI and marginal CPA.