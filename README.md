# Marketing campaign performance and budget analysis

Sergii Rostovskyi · 23 November 2026

| File or folder | Contents |
| --- | --- |
| [executive_memo.md](executive_memo.md) | Findings, confidence intervals, power estimates, and the $500,000 budget scenario |
| [dataset_documentation.md](dataset_documentation.md) | Dataset selection, attribution, validation, metric definitions, and analytical assumptions |
| [data_exploration.py](data_exploration.py) | Raw-data preparation, campaign summaries, and distribution plots |
| [statistical_analysis.py](statistical_analysis.py) | Welch and paired t-tests, Fisher tests, effect sizes, multiplicity adjustments, bootstrap intervals, and allocation |
| [power_analysis.py](power_analysis.py) | CPA power simulation, minimum sample sizes, and data adequacy |
| [data/](data/) | Prepared campaign-day CSV and source audit |
| [tables/](tables/) | Full result tables, confidence intervals, statistical findings, and budget allocation |
| [figures/](figures/) | Six exported figures |
| [reflection.md](reflection.md) | Interpretation and communication takeaways |

## Reproduction

The analysis uses Python 3.11 or later. The prepared CSV supports offline analysis with the dependencies installed. No credentials are required.

~~~console
python -m pip install -r requirements.txt
python data_exploration.py
python statistical_analysis.py
python power_analysis.py
~~~

The optional source build uses the original Hugging Face archive documented in [dataset_documentation.md](dataset_documentation.md).

~~~console
python data_exploration.py --raw /path/to/criteo_attribution_dataset.tsv.gz
~~~
