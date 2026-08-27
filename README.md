# Shopping Mall Paid Search: Statistical Marketing Analysis

This project reviews an anonymized US shopping-mall paid-search campaign from data quality through to a budget recommendation. It combines funnel KPIs, statistical comparisons and experiment planning, but keeps the business question in view: where should the team maintain spend, where should it optimise, and where should it pull back?

## Business question

How did funnel efficiency and profitability vary across structurally defined paid-search match types, and how should a marketing team maintain, optimise, test, or reduce spend while accounting for uncertainty and the limits of observational data?

The three match types are historical groups, not randomized A/B-test arms. Their results can guide investigation and planning, but they do not prove cause and effect.

## Dataset and provenance

- Dataset: [Shopping Mall Paid Search Campaign Dataset](https://www.kaggle.com/datasets/marceaxl82/shopping-mall-paid-search-campaign-dataset)
- Kaggle ID: `marceaxl82/shopping-mall-paid-search-campaign-dataset`
- Publisher: Marcello D. (`marceaxl82`)
- License: CC0
- Period: July–November 2021
- Scope: a paid-search campaign for a US shopping mall, described by the publisher as real and anonymized
- Local file: `data/shopping_mall_paid_search.csv`

The public file does not independently verify the company's identity, original system, accounting definitions, attribution window, or business provenance. `Revenue` is used as the dataset's revenue measure; the separately provided `Sale Amount` is retained but not reinterpreted without documentation.

## Repository structure

```text
data/
  shopping_mall_paid_search.csv        # unchanged source file
  marketing_data.csv                   # prepared data with recalculated KPIs
notebooks/
  data_exploration.ipynb               # validation, engineering, EDA, funnel KPIs
  statistical_analysis.ipynb           # inference, decisions, budget, sensitivity
  power_analysis.ipynb                 # prospective 80% power scenarios
outputs/                               # reproducible CSV summaries and PNG charts
scripts/build_notebooks.py             # deterministic notebook generator
src/marketing_analysis.py              # shared validation and KPI functions
README.md
executive_memo.md
reflection.md
requirements.txt
```

## Environment and installation

The required environment is Conda `bootcamp-env` with Python 3.11.

```bash
conda activate bootcamp-env
python -m pip install -r requirements.txt
python -m ipykernel install --sys-prefix --name bootcamp-env --display-name "Python (bootcamp-env)"
```

All dependencies in `requirements.txt` are directly used by the analysis, notebook generation, or execution.

### Reproducible dataset download

The lab keeps the source CSV and the prepared CSV required by the rubric. To reproduce the source download:

```bash
conda run -n bootcamp-env python -c "import kagglehub; print(kagglehub.dataset_download('marceaxl82/shopping-mall-paid-search-campaign-dataset'))"
```

Copy `final_shop_6modata.csv` from the returned version directory to `data/shopping_mall_paid_search.csv`. Kaggle authentication may be required depending on the local setup.

## Exact execution order

Run from the repository root:

```bash
conda run -n bootcamp-env python scripts/build_notebooks.py
conda run -n bootcamp-env jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=bootcamp-env --ExecutePreprocessor.timeout=600 notebooks/data_exploration.ipynb
conda run -n bootcamp-env jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=bootcamp-env --ExecutePreprocessor.timeout=600 notebooks/statistical_analysis.ipynb
conda run -n bootcamp-env jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=bootcamp-env --ExecutePreprocessor.timeout=600 notebooks/power_analysis.ipynb
```

The notebooks use relative project paths, save outputs in place, and carry the `bootcamp-env` kernelspec.

## Methodology

### Validation and feature engineering

The source has 190 rows, 12 columns, 40 ad groups, and five months. A row represents one `ad_group × month`; this composite key is unique. The pipeline checks types, missingness, exact and key duplicates, non-negative inputs, logical funnel inequalities, zero denominators, and consistency of published ratios.

No duplicate is removed automatically. KPI columns are recalculated from source counts, with `NaN` for undefined ratios:

- CTR = clicks / impressions
- Conversion rate = conversions / clicks
- CPC = cost / clicks
- CPA = cost / conversions
- Revenue per conversion = revenue / conversions
- Profit = revenue − cost
- Profit per conversion = profit / conversions
- ROAS = revenue / cost
- ROI = profit / cost
- Profit margin = profit / revenue

The published `Conv Rate` differs from recalculated conversion rate beyond rounding tolerance in 160 of 190 rows; published ratio fields are audit fields, not analytical inputs.

### Comparison groups

The primary dimension is parsed from `Ad Group` before viewing outcomes:

- `1:1` → One-to-one: 50 monthly observations, 10 ad groups
- `Exact` → Exact: 72 observations, 16 ad groups
- `Phrase` → Phrase: 68 observations, 14 ad groups

This meets the three-group requirement and avoids outcome-based selection. Device (`Desktop`, `Mobile`) is secondary; intent family is descriptive.

### Statistical approach, in plain language

The analysis uses a 5% significance threshold. A p-value below that threshold means the observed gap would be unusual if the groups were truly alike; it does not tell us how valuable the gap is or prove that one group caused it.

The required CPA analysis uses pairwise independent Welch t-tests, which compare mean CPA while allowing unequal variance. Cohen's d reports the size of each CPA difference using the formula specified in the lab. One-to-one has a lower mean CPA than Exact and Phrase after FDR correction.

ROI is highly skewed, so Kruskal–Wallis checks whether the three ROI distributions differ without assuming a bell-shaped curve. Mann–Whitney then compares pairs using ranks. ROI is retained as an additional analysis rather than a substitute for CPA.

For conversions, chi-square asks whether conversion and match type are related overall. Fisher's exact test compares each pair using conversions and non-converting clicks. Benjamini–Hochberg false discovery rate (FDR) correction reduces the risk of false positives when several pairs are tested; the stricter Bonferroni correction is also shown.

A 1,000-sample bootstrap estimates the confidence interval for mean CPA in each match type. A separate 2,000-sample ad-group bootstrap estimates ROI uncertainty while keeping repeated monthly rows together.

The required empirical power analysis simulates CPA differences of 5%, 10%, 15% and 20% across 30, 60, 90, 120 and 180 days. The additional conversion-rate section plans a future randomized test. These are prospective capacity scenarios, not invented historical observations.

At 90 days, simulated power is 61.2% for a 5% CPA difference and at least 99.3% for differences of 10% or more. The two CPA pairs that remain significant after FDR have 100% simulated power at 90 days under the lab assumptions.

## Marketing funnel and decisions

| Stage | KPIs | Business question | Decision enabled |
|---|---|---|---|
| Awareness | Impressions | How much eligible demand was reached? | Coverage and reach priorities |
| Traffic / consideration | Clicks, CTR, CPC | Was traffic attracted efficiently? | Query, creative and bid optimisation |
| Conversion | Conversions, conversion rate, CPA | Did traffic convert at an acceptable acquisition cost? | Landing-page and targeting actions |
| Revenue | Revenue, revenue per conversion | What reported value did conversions produce? | Conversion-quality and mix decisions |
| Profitability | Profit, profit margin, ROAS, ROI | Did reported revenue cover media cost? | Budget guardrails and scaling decisions |

LTV, product margins and external benchmarks are unavailable. A true business break-even CPA or ROAS cannot be calculated. ROAS = 1 is only media-cost break-even under the dataset's reported revenue definition.

## Main results

Across the portfolio there were 2,674,699 impressions, 924,503 clicks and 95,996 conversions. Recalculated CTR was 34.56%, conversion rate 10.38%, CPC $0.69 and CPA $6.62. Cost was $635,372 against reported revenue of $561,960: profit −$73,412, ROAS 0.884 and ROI −11.55%.

| Match type | Conversions | CPA | ROAS | ROI | Cluster-bootstrap ROI 95% CI | Decision |
|---|---:|---:|---:|---:|---:|---|
| One-to-one | 72,388 | $6.39 | 0.895 | −10.5% | −13.7% to −7.6% | Maintain |
| Exact | 15,038 | $7.00 | 0.886 | −11.4% | −26.1% to −5.2% | Optimise/Test |
| Phrase | 8,570 | $7.86 | 0.812 | −18.8% | −31.1% to −11.4% | Reduce/Pause |

The required t-tests compare monthly ad-group CPA observations rather than the aggregate ratios above. Mean row-level CPA was $6.67 for One-to-one, $7.99 for Exact and $8.89 for Phrase. After FDR correction, One-to-one remained lower than Exact by $1.32 (Cohen's d 0.37, small) and lower than Phrase by $2.21 (Cohen's d 0.57, medium). Exact versus Phrase was not significant.

Conversion rates differed globally (χ² = 43.40, p < 0.001), meaning the pattern would be unlikely if all three rates were the same. The size of the relationship was tiny, however: Cramér's V, an effect-size measure, was only 0.0069. One-to-one exceeded Exact by 0.41 percentage points and Phrase by 0.57 points; Exact versus Phrase was not distinguishable after correction.

For the marketing team, the conversion gap is worth investigating but is not a reason to scale on its own. With more than 924,000 clicks, even small differences are easy to detect statistically. Negative ROI across every group carries more weight in the budget decision.

### Guardrailed $500,000 scenario

The score combines CPA efficiency (40%), ROAS (40%) and conversion-volume reliability (20%), with a 20% floor and 40% cap per group. It allocates 40% to One-to-one, 40% to Exact and 20% to Phrase. That is deliberately less concentrated than historical spend.

At unchanged historical rates, the scenario estimates about $437,000 in revenue and a $63,000 loss. The practical recommendation is to release budget in stages and stop adding spend if marginal economics do not improve.

The sensitivity table in `outputs/sensitivity_scenarios.csv` varies CPC, conversion rate and revenue per conversion jointly by ±10%. It is a transparent scenario, not a forecast.

## Marketing applicability

Only paid search is demonstrated by these data. Funnel design, proportion tests, uncertainty intervals, controlled testing and guarded allocation transfer to Paid Social, Display, Email/CRM, Organic and Offline/brand analysis, but their numerical findings do not. Those areas require channel-specific exposure, audience, attribution, cost, incrementality and outcome data; the dataset contains none of those channels.

## Limitations

- Observational, aggregated and non-randomized; associations are not causal.
- Only five monthly periods; ten ad-group/month combinations are absent.
- Repeated months per ad group reduce independence; cluster bootstrap helps but does not solve all dependence.
- No search-term report, bids, quality scores, user-level data, attribution window, product margin, LTV, new-customer flag or incrementality measure.
- Revenue and `Sale Amount` lack sufficiently detailed accounting definitions.
- The publisher's real-company and anonymization claims cannot be independently verified.
- Historical average performance may not scale linearly to a $500,000 budget.

See `executive_memo.md` for the business summary and `reflection.md` for methodological lessons and proposed experimental improvements.
