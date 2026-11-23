# Marketing Channel Statistical Analysis

Analysis of four marketing channel categories for a proposed
monthly budget of USD 500,000.

Start with [lab_proof.md](lab_proof.md) for the run evidence,
main results and limitations.

## File map

| File or folder | Purpose |
| --- | --- |
| instructions.md | Original lab instructions |
| rubric.md | Original grading criteria |
| lab_proof.md | Submission evidence and results |
| lab_statistical_analysis_STUDENT.ipynb | Completed analysis with saved outputs |
| Marketing.csv | Original downloaded dataset |
| outputs/ | Prepared data, result tables, six charts and executive memo |

## How to run

1. Use Python 3.11 and a Jupyter environment.
2. Install the packages below if needed.
3. Keep Marketing.csv next to the notebook.
4. Open the notebook and select the Python environment.
5. Restart the kernel and run all cells from top to bottom.

Installation command:

    python -m pip install numpy pandas matplotlib seaborn "scipy>=1.11" ipykernel

The notebook creates the outputs folder and saves the results.
No API keys are required.

## Dataset

Source: [Digital Marketing Metrics & KPIs to Measure — Kaggle](https://www.kaggle.com/datasets/sinderpreet/analyze-the-marketing-spending)

The original file contains 308 campaign-day records from
1–28 February 2021. The analysis groups campaigns into four
categories, producing 112 channel-day records.

The original business source, real or synthetic status,
currency and attribution rules were not independently verified.

## Analysis

The notebook includes marketing metrics, Welch's t-tests,
Cohen's d, Fisher's exact tests, Bonferroni and BH corrections,
power simulations, bootstrap intervals and a budget scenario.

See [the executive memo](outputs/executive_memo.md)
for recommendations and statistical caveats.

## Optional work

The optional reflection was not completed.