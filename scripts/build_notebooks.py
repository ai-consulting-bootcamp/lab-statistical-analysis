"""Generate the three reader-facing notebooks for this lab."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
KERNEL = {
    "kernelspec": {
        "display_name": "Python (bootcamp-env)",
        "language": "python",
        "name": "bootcamp-env",
    },
    "language_info": {"name": "python", "version": "3.11"},
}


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


def write_notebook(name: str, cells):
    notebook = nbf.v4.new_notebook(cells=cells, metadata=KERNEL)
    nbf.write(notebook, NOTEBOOKS / name)


def build_exploration():
    cells = [
        md("""
# Shopping Mall Paid Search — Data Exploration

## Executive Summary

The dataset covers 190 monthly ad-group records from July to November 2021. It has no missing values or duplicate rows. One source field does need care: the published conversion rate does not match `conversions / clicks` in 160 rows. For that reason, this analysis recalculates every KPI from the underlying counts instead of relying on the supplied ratios.

The main comparison is match type: One-to-one, Exact and Phrase. These labels come directly from the ad-group names, so the groups were defined without looking at which one performed best. Device is used as a secondary view.

This is a historical, observational analysis. It can show where results moved together, but it cannot prove that match type or device caused the differences.
"""),
        md("""
## Business Question and Approach

The business question is straightforward: how did paid-search efficiency and profitability vary by match type, and which areas should the marketing team maintain, optimise or reduce?

**Source.** [Shopping Mall Paid Search Campaign Dataset](https://www.kaggle.com/datasets/marceaxl82/shopping-mall-paid-search-campaign-dataset), published by Marcello D. (`marceaxl82`) under CC0. The publisher describes a real, anonymized US shopping-mall paid-search campaign covering July–November 2021. The underlying company's identity and provenance cannot be independently verified from the public file.

### Working assumptions

- A row is one `ad_group × month` observation; this is validated as a unique composite key.
- `Revenue` is used as the dataset's revenue measure. `Sale Amount` is retained but not treated as revenue because the source does not provide a sufficiently precise financial definition.
- Published ratio columns are audit fields only. Recalculated ratios are authoritative.
- Exact duplicate rows are reported but not removed automatically.
"""),
        code("""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

for candidate in [Path.cwd(), *Path.cwd().parents]:
    if (candidate / "src" / "marketing_analysis.py").exists():
        PROJECT_ROOT = candidate
        break
else:
    raise FileNotFoundError("Run from the repository root or notebooks directory.")

sys.path.insert(0, str(PROJECT_ROOT / "src"))
from marketing_analysis import prepare_data, quality_checks, aggregate_performance, MONTH_ORDER, MATCH_ORDER

DATA_PATH = PROJECT_ROOT / "data" / "shopping_mall_paid_search.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid", context="notebook")
pd.set_option("display.max_columns", 50)
print("Project root:", PROJECT_ROOT)
print("Data source:", DATA_PATH.relative_to(PROJECT_ROOT))
"""),
        md("""
## Data

### Data dictionary

The first table separates fields supplied by the publisher from fields calculated in this project. Currency values are reported exactly as they appear in the dataset. The source does not explain tax treatment, attribution windows, product margin, or whether revenue is gross or net.
"""),
        code("""
raw = pd.read_csv(DATA_PATH)
df = prepare_data(DATA_PATH)
PREPARED_DATA_PATH = PROJECT_ROOT / "data" / "marketing_data.csv"
df.to_csv(PREPARED_DATA_PATH, index=False)
print("Prepared dataset saved to:", PREPARED_DATA_PATH.relative_to(PROJECT_ROOT))

dictionary = pd.DataFrame([
    ("ad_group", "Source", "Anonymized structural ad-group name"),
    ("month", "Source", "Monthly reporting period, July–November 2021"),
    ("impressions", "Source", "Ads served; awareness volume"),
    ("clicks", "Source", "Ad clicks; traffic volume"),
    ("conversions", "Source", "Attributed conversions reported by the publisher"),
    ("cost", "Source", "Paid-search spend"),
    ("revenue", "Source", "Revenue measure reported by the publisher"),
    ("sale_amount", "Source", "Separate sales-value field; definition not independently verified"),
    ("source_ctr / source_conversion_rate / source_cpc / source_p_and_l", "Source", "Published metrics retained only for reconciliation"),
    ("device", "Engineered", "Desktop or Mobile parsed from ad_group"),
    ("match_type", "Engineered", "One-to-one, Exact, or Phrase parsed from ad_group"),
    ("intent_family", "Engineered", "Term family parsed structurally from ad_group"),
    ("ctr", "Engineered", "clicks / impressions"),
    ("conversion_rate", "Engineered", "conversions / clicks"),
    ("cpc", "Engineered", "cost / clicks"),
    ("cpa", "Engineered", "cost / conversions"),
    ("revenue_per_conversion", "Engineered", "revenue / conversions"),
    ("profit", "Engineered", "revenue - cost"),
    ("profit_per_conversion", "Engineered", "profit / conversions"),
    ("roas", "Engineered", "revenue / cost"),
    ("roi", "Engineered", "profit / cost"),
    ("profit_margin", "Engineered", "profit / revenue"),
], columns=["field", "origin", "definition"])
dictionary
"""),
        md("### Shape, types, grain, and coverage"),
        code("""
print(f"Raw shape: {raw.shape}")
print(f"Prepared shape: {df.shape}")
print("Unit of observation: one ad_group × month row")
print("Months:", [str(x) for x in df["month"].dropna().unique()])
print("Unique ad groups:", df["ad_group"].nunique())
print("Rows per month:")
display(df.groupby("month", observed=True).size().rename("rows").to_frame())
display(raw.dtypes.rename("dtype").to_frame())
"""),
        md("""
### Data checks and source-metric reconciliation

When a denominator is zero, the result is left undefined as `NaN`; it is never replaced with zero. A negative profit is a possible business result, so it is not treated as a data error. Missing ad-group/month combinations are reported rather than filled with invented values.
"""),
        code("""
checks = quality_checks(raw, df)
display(checks)
print("Failed checks:")
display(checks.loc[~checks["passed"]])
print("Missing ad_group × month combinations:", df["ad_group"].nunique() * df["month"].nunique() - len(df))
checks.to_csv(OUTPUT_DIR / "data_quality_checks.csv", index=False)
"""),
        code("""
metric_reconciliation = pd.DataFrame({
    "metric": ["CTR", "Conversion rate", "CPC", "P&L"],
    "source_field": ["source_ctr", "source_conversion_rate", "source_cpc", "source_p_and_l"],
    "recalculation": ["clicks / impressions", "conversions / clicks", "cost / clicks", "revenue - cost"],
    "max_absolute_difference": [
        (df["source_ctr"] - df["ctr"]).abs().max(),
        (df["source_conversion_rate"] - df["conversion_rate"]).abs().max(),
        (df["source_cpc"] - df["cpc"]).abs().max(),
        (df["source_p_and_l"] - df["profit"]).abs().max(),
    ],
    "rows_outside_rounding_tolerance": [
        ((df["source_ctr"] - df["ctr"]).abs() > 0.0051).sum(),
        ((df["source_conversion_rate"] - df["conversion_rate"]).abs() > 0.0051).sum(),
        ((df["source_cpc"] - df["cpc"]).abs() > 0.011).sum(),
        ((df["source_p_and_l"] - df["profit"]).abs() > 0.51).sum(),
    ],
})
metric_reconciliation
"""),
        md("""
### What the checks mean for the analysis

CTR and P&L reconcile within normal rounding tolerance. The supplied conversion rate does not: 160 of 190 rows differ from the value obtained by dividing conversions by clicks. CPC also has 16 small discrepancies, mainly where rounded source values magnify the difference.

For the marketing team, the relevant point is that the raw counts are internally usable, while some pre-calculated ratios are not. All comparisons that follow use recalculated KPIs. No rows were deleted to make the results look cleaner.
"""),
        md("""
## What the Data Shows

### Structural comparison groups

The second segment of `Ad Group` provides the grouping rule: `1:1 → One-to-one`, `Exact → Exact`, and `Phrase → Phrase`. This gives three groups with 50, 72 and 68 monthly observations respectively. Device (`Desk → Desktop`, `Mob → Mobile`) provides a second view. Intent family is available for exploration, but it is not used to select winners or losers.
"""),
        code("""
group_structure = (
    df.groupby(["match_type", "device"], observed=True)
      .agg(observations=("ad_group", "size"), ad_groups=("ad_group", "nunique"), months=("month", "nunique"))
      .reset_index()
)
display(group_structure)
display(df.groupby("intent_family", observed=True).agg(observations=("ad_group", "size"), ad_groups=("ad_group", "nunique")).sort_values("observations", ascending=False))
"""),
        md("""
### Marketing funnel and unit economics

| Stage | KPI | Business question | Decision supported |
|---|---|---|---|
| Awareness | Impressions | How much eligible search demand did ads reach? | Coverage and reach priorities |
| Traffic / consideration | Clicks, CTR, CPC | Did ads attract traffic, and at what media cost? | Creative/query relevance and bid control |
| Conversion | Conversions, conversion rate, CPA | Did traffic convert efficiently? | Landing-page, targeting, and acquisition decisions |
| Revenue | Revenue, revenue per conversion | How much reported revenue did conversions generate? | Value quality and mix |
| Profitability | Profit, profit margin, ROAS, ROI | Did reported revenue cover media cost? | Budget guardrails and optimisation |

LTV, product gross margin, incrementality, and external benchmarks are absent. Consequently, a true break-even CPA or ROAS cannot be established; ROAS = 1 is only media-cost break-even under the dataset's reported revenue definition, not full business break-even.
"""),
        code("""
match_summary = aggregate_performance(df, "match_type")
device_summary = aggregate_performance(df, "device")
monthly_summary = aggregate_performance(df, "month")

display(match_summary.round(4))
display(device_summary.round(4))
match_summary.to_csv(OUTPUT_DIR / "group_performance_summary.csv", index=False)
device_summary.to_csv(OUTPUT_DIR / "device_performance_summary.csv", index=False)
monthly_summary.to_csv(OUTPUT_DIR / "monthly_performance.csv", index=False)
"""),
        md("""
### Business interpretation of the KPI table

One-to-one carried most of the volume and had the lowest CPA at $6.39. Exact followed at $7.00, while Phrase cost $7.86 per conversion. The profitability picture is less encouraging: ROAS was below 1 and ROI was negative for all three groups. In practical terms, the reported revenue did not cover media cost in any match type.

Desktop showed a higher observed conversion rate than Mobile (17.96% versus 7.80%), while Mobile delivered far more clicks and a slightly lower CPA. This suggests a meaningful device mix difference, but it does not prove that the device itself caused the gap. Query mix, bids, landing pages and attribution may also explain it.
"""),
        md("### Charts for the marketing review"),
        code("""
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
plot_specs = [
    ("conversion_rate", "Conversion rate", ".1%", ""),
    ("cpa", "Cost per acquisition", ",.2f", "$"),
    ("roas", "ROAS", ".2f", ""),
    ("profit", "Profit", ",.0f", "$"),
]
for ax, (metric, title, fmt, prefix) in zip(axes.flat, plot_specs):
    sns.barplot(data=match_summary, x="match_type", y=metric, ax=ax, color="#4C78A8")
    ax.set_title(f"{title} by match type")
    ax.set_xlabel("")
    ax.set_ylabel(title)
    if metric == "profit":
        ax.axhline(0, color="black", lw=1)
    for patch, value in zip(ax.patches, match_summary[metric]):
        label = prefix + format(value, fmt)
        ax.annotate(label, (patch.get_x() + patch.get_width()/2, patch.get_height()),
                    ha="center", va="bottom" if value >= 0 else "top", fontsize=9)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "group_kpis.png", dpi=180, bbox_inches="tight")
fig.savefig(OUTPUT_DIR / "group_metrics_overview.png", dpi=180, bbox_inches="tight")
plt.show()
"""),
        code("""
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, metric, label in zip(axes, ["conversion_rate", "cpa", "roi"], ["Conversion rate", "CPA", "ROI"]):
    sns.boxplot(data=df, x="match_type", y=metric, order=MATCH_ORDER, ax=ax, color="#72B7B2")
    sns.stripplot(data=df, x="match_type", y=metric, order=MATCH_ORDER, ax=ax,
                  color="black", alpha=.35, size=3)
    ax.set_title(f"How monthly ad-group {label} varies")
    ax.set_xlabel("")
    ax.set_ylabel(label)
    if metric == "roi": ax.axhline(0, color="red", ls="--", lw=1)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "metric_distributions.png", dpi=180, bbox_inches="tight")
fig.savefig(OUTPUT_DIR / "group_distributions.png", dpi=180, bbox_inches="tight")
plt.show()
"""),
        code("""
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.lineplot(data=monthly_summary, x="month", y="conversion_rate", marker="o", ax=axes[0], color="#4C78A8")
sns.lineplot(data=monthly_summary, x="month", y="roi", marker="o", ax=axes[1], color="#F58518")
axes[0].set_title("Recalculated conversion rate by month")
axes[1].set_title("Recalculated ROI by month")
axes[1].axhline(0, color="black", lw=1)
for ax in axes: ax.tick_params(axis="x", rotation=30)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "monthly_trends.png", dpi=180, bbox_inches="tight")
plt.show()
"""),
        md("""
## Key Findings

One-to-one is the strongest relative performer: it supplied most conversions and had the best CPA and ROAS of the three groups. It is not a profitable winner, however. Its ROI was still −10.5%.

Phrase had the weakest CPA, ROAS and ROI. The data supports reducing exposure and reviewing its search terms, but not assuming that every Phrase keyword should be paused. Performance may vary within the group.

Desktop converted at a higher observed rate, while Mobile supplied most clicks and had a slightly lower CPA. The sensible next step is a device-level diagnostic, not a claim that Desktop traffic is inherently better.

Most importantly, all three match types lost money under `profit = revenue - cost`. The data is strong enough to identify areas for optimisation, but not to justify broad scaling or a causal claim.

### Limitations

The dataset is monthly and aggregated, covers only five months, and is missing ten possible ad-group/month combinations. It has no user-level assignment, keyword-auction detail, attribution window, margin, seasonality controls or experimental randomisation. The same ad groups appear across months, so those rows are related rather than fully independent. The public claim that the data comes from a real company also cannot be independently verified. These limits keep the findings descriptive.
"""),
    ]
    write_notebook("data_exploration.ipynb", cells)


def build_statistics():
    cells = [
        md("""
# Statistical Analysis and Marketing Decisions

## Executive Summary

The three match types do not perform identically, but the size of the difference depends on the metric. One-to-one converted 0.41 percentage points above Exact and 0.57 points above Phrase. Those gaps are statistically detectable because the dataset contains more than 924,000 clicks, yet the overall conversion effect is very small.

Profitability is the clearer business signal. ROI was negative for One-to-one, Exact and Phrase, and the uncertainty ranges remained below zero for all three. The recommendation is therefore to maintain the strongest relative group, optimise the middle group and reduce the weakest—not to scale a supposed winner.

These are historical associations. They do not show that changing match type will cause the same change in performance.
"""),
        md("""
## Questions, Tests and Plain-English Definitions

**Primary grouping:** match type (`One-to-one`, `Exact`, `Phrase`), parsed before outcome analysis.

**Secondary grouping:** device (`Desktop`, `Mobile`).

**Significance level:** α = 0.05, two-sided. This is the threshold chosen in advance for flagging evidence that would be unusual if there were no real group difference.

**Multiple comparisons:** testing several pairs increases the chance of a false alarm. Benjamini–Hochberg false discovery rate (FDR) correction limits the expected share of false positives among flagged results. The stricter Bonferroni correction is also shown.

**Continuous outcome:** row-level recalculated ROI at the monthly ad-group grain.

**Proportion outcome:** aggregated conversions versus non-converting clicks.

### What is being tested

- For ROI, the null hypothesis (H₀) says the match types have no underlying difference. The alternative (H₁) says at least one differs.
- For conversion, H₀ says the chance of conversion is unrelated to match type. H₁ says the rates are not all the same.

A p-value asks: if there were truly no difference, how unusual would results this large be? A small p-value is evidence against H₀; it is not the probability that H₀ is true, and it says nothing by itself about commercial value.

An effect size describes how large a difference is. A confidence interval shows the range of values reasonably compatible with the data and method. Both are needed because a tiny effect can have a small p-value when traffic volume is large.

The tests below detect association, not incremental lift. Monthly rows repeat ad groups, so simple row-level p-values can look more precise than the evidence really is. The analysis therefore adds intervals that resample whole ad groups.
"""),
        code("""
from pathlib import Path
import sys, json, itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from matplotlib.ticker import PercentFormatter

for candidate in [Path.cwd(), *Path.cwd().parents]:
    if (candidate / "src" / "marketing_analysis.py").exists():
        PROJECT_ROOT = candidate
        break
else:
    raise FileNotFoundError("Run from the repository root or notebooks directory.")
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from marketing_analysis import (
    prepare_data, aggregate_performance, benjamini_hochberg,
    budget_recommendation, sensitivity_scenarios, MATCH_ORDER
)

DATA_PATH = PROJECT_ROOT / "data" / "shopping_mall_paid_search.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
ALPHA = 0.05
RNG_SEED = 42
df = prepare_data(DATA_PATH)
summary = aggregate_performance(df, "match_type")
sns.set_theme(style="whitegrid", context="notebook")
display(summary.round(4))
"""),
        md("""
## Do the ROI Data Fit a Standard Mean Test?

The Shapiro–Wilk test checks whether each group's ROI values resemble a normal, bell-shaped distribution. The Brown–Forsythe version of Levene's test checks whether the spread is broadly similar across groups. These checks help decide whether a standard comparison of means is a good summary.
"""),
        code("""
assumption_rows = []
for group in MATCH_ORDER:
    values = df.loc[df["match_type"].eq(group), "roi"].dropna()
    shapiro = stats.shapiro(values)
    assumption_rows.append({"group": group, "n": len(values), "roi_mean": values.mean(),
                            "roi_median": values.median(), "shapiro_w": shapiro.statistic,
                            "shapiro_p": shapiro.pvalue})
assumptions = pd.DataFrame(assumption_rows)
levene = stats.levene(*[df.loc[df["match_type"].eq(g), "roi"].dropna() for g in MATCH_ORDER], center="median")
display(assumptions)
print(f"Brown–Forsythe/Levene: statistic={levene.statistic:.4f}, p={levene.pvalue:.4g}")
print("Method choice: rank-based tests and ad-group resampling are primary because ROI is skewed and ad groups repeat across months.")
"""),
        md("""
Exact and Phrase clearly fail the normality check (both p-values are far below 0.05), while One-to-one does not. The variance check is not significant (p = 0.143), but the extreme values in Exact and Phrase make their means misleading: both groups have positive mean ROI and negative median ROI.

For the marketing team, that is a warning not to let a few unusually strong monthly rows define the story. Rank-based tests and ad-group resampling are more suitable for the main interpretation. Welch's test is still reported so the required mean comparison remains visible.
"""),
        md("""
## Required CPA Pairwise Comparisons

The lab requires independent t-tests on row-level CPA for every match-type pair. CPA rows with zero conversions are undefined and excluded. Welch's version is used because it does not require equal variances. Cohen's d reports the size of each difference using the lab formula; the sign follows `group B − group A`.
"""),
        code("""
def interpret_cohens_d(value):
    magnitude = abs(value)
    if magnitude < 0.2:
        return "negligible"
    if magnitude < 0.5:
        return "small"
    if magnitude < 0.8:
        return "medium"
    return "large"

cpa_rows = []
for group_a, group_b in itertools.combinations(MATCH_ORDER, 2):
    values_a = df.loc[df["match_type"].eq(group_a), "cpa"].replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    values_b = df.loc[df["match_type"].eq(group_b), "cpa"].replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    test = stats.ttest_ind(values_a, values_b, equal_var=False)
    mean_a, mean_b = values_a.mean(), values_b.mean()
    difference = mean_b - mean_a
    pooled_std = np.sqrt((values_a.var(ddof=1) + values_b.var(ddof=1)) / 2)
    cohens_d = difference / pooled_std if pooled_std else np.nan
    cpa_rows.append({
        "group_a": group_a, "group_b": group_b,
        "n_a": len(values_a), "n_b": len(values_b),
        "mean_cpa_a": mean_a, "mean_cpa_b": mean_b,
        "difference_b_minus_a": difference,
        "percentage_difference": difference / mean_a * 100 if mean_a else np.nan,
        "t_statistic": test.statistic, "p_value": test.pvalue,
        "significant_uncorrected": test.pvalue < ALPHA,
        "cohens_d": cohens_d,
        "effect_size_interpretation": interpret_cohens_d(cohens_d),
    })

cpa_tests = pd.DataFrame(cpa_rows)
cpa_comparisons = len(cpa_tests)
cpa_alpha_bonferroni = ALPHA / cpa_comparisons
cpa_tests["alpha_bonferroni"] = cpa_alpha_bonferroni
cpa_tests["p_value_bonferroni"] = np.minimum(cpa_tests["p_value"] * cpa_comparisons, 1)
cpa_tests["significant_bonferroni"] = cpa_tests["p_value"] < cpa_alpha_bonferroni
cpa_tests["p_value_fdr"] = benjamini_hochberg(cpa_tests["p_value"])
cpa_tests["significant_fdr"] = cpa_tests["p_value_fdr"] < ALPHA

display(cpa_tests)
print(f"CPA comparisons: {cpa_comparisons}; expected false positives at alpha=.05: {cpa_comparisons * ALPHA:.2f}")
cpa_tests.to_csv(OUTPUT_DIR / "cpa_pairwise_tests.csv", index=False)
"""),
        md("""
One-to-one has a lower mean CPA than Exact by $1.32 (19.8%) and Phrase by $2.21 (33.2%). Both comparisons remain significant after FDR. The Cohen's d effects are small for Exact and medium for Phrase. Exact versus Phrase is not significant and has a negligible effect.

This supports maintaining One-to-one and reducing Phrase exposure. It does not show that changing match type will cause CPA to fall, because the groups were not randomized.
"""),
        code("""
cpa_p_matrix = pd.DataFrame(1.0, index=MATCH_ORDER, columns=MATCH_ORDER)
for row in cpa_tests.itertuples():
    cpa_p_matrix.loc[row.group_a, row.group_b] = row.p_value
    cpa_p_matrix.loc[row.group_b, row.group_a] = row.p_value

fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(cpa_p_matrix, annot=True, fmt=".4f", cmap="RdYlGn", vmin=0, vmax=1,
            square=True, linewidths=.5, cbar_kws={"label": "CPA t-test p-value"}, ax=ax)
ax.set_title("Pairwise CPA p-values by match type")
ax.set_xlabel("Match type"); ax.set_ylabel("Match type")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "metric_comparison_heatmap.png", dpi=180, bbox_inches="tight")
plt.show()
"""),
        md("""
### Bootstrap confidence intervals for mean CPA

The bootstrap resamples the available CPA observations 1,000 times. The interval shows how much the estimated mean CPA moves under repeated resampling.
"""),
        code("""
def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    values = pd.Series(data).replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    rng = np.random.default_rng(RNG_SEED)
    means = np.array([rng.choice(values, size=len(values), replace=True).mean() for _ in range(n_bootstrap)])
    tail = (1 - ci_level) / 2
    return np.quantile(means, [tail, 1 - tail])

cpa_ci_rows = []
for group in MATCH_ORDER:
    values = df.loc[df["match_type"].eq(group), "cpa"]
    ci_low, ci_high = bootstrap_ci(values)
    cpa_ci_rows.append({"match_type": group, "mean_cpa": values.replace([np.inf, -np.inf], np.nan).mean(),
                        "ci_95_low": ci_low, "ci_95_high": ci_high})
cpa_bootstrap_ci = pd.DataFrame(cpa_ci_rows)
display(cpa_bootstrap_ci)
cpa_bootstrap_ci.to_csv(OUTPUT_DIR / "cpa_bootstrap_ci.csv", index=False)
"""),
        md("""
## Does ROI Differ by Match Type?

Kruskal–Wallis first asks whether the three ROI distributions differ somewhere. It compares their ranks rather than assuming a bell-shaped distribution. If the global result flags a difference, Mann–Whitney tests compare each pair using the same rank-based logic.

Welch's t-test answers a different question: do the average ROI values differ? It allows unequal variances, but unusual values can still influence the mean. This ROI section is retained as an extension; Cohen's d is reported in the required CPA section above.
"""),
        code("""
roi_groups = [df.loc[df["match_type"].eq(g), "roi"].dropna() for g in MATCH_ORDER]
kruskal = stats.kruskal(*roi_groups)
print(f"Kruskal–Wallis H={kruskal.statistic:.4f}, p={kruskal.pvalue:.4g}")

rows = []
for a, b in itertools.combinations(MATCH_ORDER, 2):
    x = df.loc[df["match_type"].eq(a), "roi"].dropna()
    y = df.loc[df["match_type"].eq(b), "roi"].dropna()
    welch = stats.ttest_ind(x, y, equal_var=False)
    mw = stats.mannwhitneyu(x, y, alternative="two-sided")
    rows.append({"comparison": f"{a} vs {b}", "group_a": a, "group_b": b,
                 "n_a": len(x), "n_b": len(y), "mean_diff_roi": x.mean()-y.mean(),
                 "median_diff_roi": x.median()-y.median(),
                 "welch_t": welch.statistic, "welch_p": welch.pvalue,
                 "mann_whitney_u": mw.statistic, "mann_whitney_p": mw.pvalue})
continuous_tests = pd.DataFrame(rows)
for family in ["welch", "mann_whitney"]:
    pcol = f"{family}_p"
    continuous_tests[f"{family}_p_fdr"] = benjamini_hochberg(continuous_tests[pcol])
    continuous_tests[f"{family}_p_bonferroni"] = np.minimum(continuous_tests[pcol] * len(continuous_tests), 1)
display(continuous_tests)
continuous_tests.to_csv(OUTPUT_DIR / "continuous_pairwise_tests.csv", index=False)
"""),
        md("""
### What the ROI tests found

Kruskal–Wallis produced H = 11.05 and p = 0.004. In plain language, the rank pattern is unlikely to look this different if all three match types shared the same ROI distribution.

After FDR correction, Mann–Whitney flags One-to-one versus Exact (adjusted p = 0.037) and One-to-one versus Phrase (adjusted p = 0.004). The stricter Bonferroni correction retains only One-to-one versus Phrase. Exact versus Phrase is not distinguishable in this test. All Welch p-values are above 0.45, so the mean differences are not clear relative to the noisy row-level spread.

In practical terms, the typical rank ordering differs most clearly between One-to-one and Phrase. The evidence is not strong enough to claim stable mean ROI differences across every pair, and it cannot show that match type caused the pattern.
"""),
        md("""
### How uncertain are the profitability estimates?

A bootstrap repeatedly resamples the observed data to see how much an estimate moves. Here, 2,000 samples are drawn at the ad-group level so each selected ad group keeps all its monthly rows together. The resulting 95% confidence interval is the central range produced by that process; it is a practical picture of uncertainty, not a guarantee that future performance will fall inside it.
"""),
        code("""
def aggregate_roi(frame):
    return (frame["revenue"].sum() - frame["cost"].sum()) / frame["cost"].sum()

def cluster_bootstrap_group(frame, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    groups = frame["ad_group"].unique()
    estimates = np.empty(n_boot)
    for i in range(n_boot):
        sampled = rng.choice(groups, size=len(groups), replace=True)
        pieces = [frame.loc[frame["ad_group"].eq(g)] for g in sampled]
        estimates[i] = aggregate_roi(pd.concat(pieces, ignore_index=True))
    return estimates

bootstrap_samples = {}
bootstrap_rows = []
for idx, group in enumerate(MATCH_ORDER):
    frame = df.loc[df["match_type"].eq(group)]
    boot = cluster_bootstrap_group(frame, seed=RNG_SEED + idx)
    bootstrap_samples[group] = boot
    bootstrap_rows.append({"match_type": group, "bootstrap_ad_groups": frame["ad_group"].nunique(),
                           "roi": aggregate_roi(frame), "roi_ci_low": np.quantile(boot, .025),
                           "roi_ci_high": np.quantile(boot, .975)})
bootstrap_ci = pd.DataFrame(bootstrap_rows)
display(bootstrap_ci)
bootstrap_ci.to_csv(OUTPUT_DIR / "group_roi_bootstrap_ci.csv", index=False)

diff_rows = []
for a, b in itertools.combinations(MATCH_ORDER, 2):
    diffs = bootstrap_samples[a] - bootstrap_samples[b]
    diff_rows.append({"comparison": f"{a} vs {b}", "roi_difference": aggregate_roi(df[df.match_type.eq(a)])-aggregate_roi(df[df.match_type.eq(b)]),
                      "ci_low": np.quantile(diffs,.025), "ci_high": np.quantile(diffs,.975)})
bootstrap_diffs = pd.DataFrame(diff_rows)
display(bootstrap_diffs)
bootstrap_diffs.to_csv(OUTPUT_DIR / "roi_bootstrap_differences.csv", index=False)
"""),
        md("""
All three ROI intervals stay below zero: One-to-one ranges from −13.7% to −7.6%, Exact from −26.1% to −5.2%, and Phrase from −31.1% to −11.4%. This is more important for the budget decision than the pairwise p-values: none of the groups has evidence of positive historical profitability.

One-to-one's ROI is about 8.2 percentage points above Phrase, with a bootstrap interval from 0.4 to 21.3 points. The intervals for One-to-one versus Exact and Exact versus Phrase cross zero, so their relative profitability remains uncertain. The data is strong enough to treat Phrase as the weakest historical group, but not to rank every pair with confidence or promise the same result after reallocating spend.
"""),
        md("""
## Do Conversion Rates Differ?

The denominator for conversion rate is clicks, so non-converting clicks are calculated as `clicks - conversions`. The chi-square test asks whether conversion and match type are related across all three groups. Fisher's exact test then compares each pair using a 2×2 table of conversions and non-converting clicks.

Cramér's V is the global effect size: it indicates how strong the association is, from zero for no association upward. Odds ratios and absolute percentage-point differences make the pairwise results easier to interpret. FDR and Bonferroni corrections again account for the three comparisons.
"""),
        code("""
counts = summary.set_index("match_type")[["clicks", "conversions"]].copy()
counts["non_converting_clicks"] = counts["clicks"] - counts["conversions"]
display(counts.rename(columns={"clicks": "total_attempts"}))
contingency = counts.loc[MATCH_ORDER, ["conversions", "non_converting_clicks"]].to_numpy()
chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
n_total = contingency.sum()
cramers_v = np.sqrt(chi2 / (n_total * min(contingency.shape[0]-1, contingency.shape[1]-1)))
print(f"Chi-square={chi2:.3f}, df={dof}, p={chi_p:.4g}, Cramér's V={cramers_v:.4f}")

conversion_rows = []
for a, b in itertools.combinations(MATCH_ORDER, 2):
    ca, na = int(counts.loc[a,"conversions"]), int(counts.loc[a,"non_converting_clicks"])
    cb, nb = int(counts.loc[b,"conversions"]), int(counts.loc[b,"non_converting_clicks"])
    odds_ratio, p = stats.fisher_exact([[ca,na],[cb,nb]], alternative="two-sided")
    rate_a, rate_b = ca/(ca+na), cb/(cb+nb)
    risk_diff = rate_a-rate_b
    se = np.sqrt(rate_a*(1-rate_a)/(ca+na) + rate_b*(1-rate_b)/(cb+nb))
    conversion_rows.append({
        "comparison": f"{a} vs {b}", "group_a": a, "group_b": b,
        "conversions_a": ca, "attempts_a": ca + na,
        "conversions_b": cb, "attempts_b": cb + nb,
        "rate_a": rate_a, "rate_b": rate_b,
        "difference_b_minus_a": rate_b - rate_a,
        "percentage_difference": (rate_b - rate_a) / rate_a * 100 if rate_a else np.nan,
        "risk_difference_a_minus_b": risk_diff,
        "risk_difference_ci_low": risk_diff-1.96*se,
        "risk_difference_ci_high": risk_diff+1.96*se,
        "odds_ratio": odds_ratio, "p_value": p,
        "significant_uncorrected": p < ALPHA,
    })
conversion_tests = pd.DataFrame(conversion_rows)
conversion_comparisons = len(conversion_tests)
conversion_alpha_bonferroni = ALPHA / conversion_comparisons
conversion_tests["alpha_bonferroni"] = conversion_alpha_bonferroni
conversion_tests["p_value_bonferroni"] = np.minimum(conversion_tests["p_value"] * conversion_comparisons, 1)
conversion_tests["significant_bonferroni"] = conversion_tests["p_value"] < conversion_alpha_bonferroni
conversion_tests["p_value_fdr"] = benjamini_hochberg(conversion_tests["p_value"])
conversion_tests["significant_fdr"] = conversion_tests["p_value_fdr"] < ALPHA
display(conversion_tests)
print(f"Conversion-rate comparisons: {conversion_comparisons}; expected false positives at alpha=.05: {conversion_comparisons * ALPHA:.2f}")
conversion_tests.to_csv(OUTPUT_DIR / "conversion_pairwise_tests.csv", index=False)
"""),
        md("""
### What the conversion tests found

The global chi-square result is 43.40 with p < 0.001, so the rates are not identical. Cramér's V is only 0.0069, however, which means the overall association is very small.

One-to-one converted at 10.50%, compared with 10.09% for Exact and 9.93% for Phrase. The differences are 0.41 and 0.57 percentage points respectively, and both remain significant after FDR and Bonferroni correction. Exact versus Phrase differs by only 0.16 points; its confidence interval crosses zero and its adjusted p-value is not significant.

For the marketing team, the relevant point is that One-to-one has a consistent but modest conversion advantage. The click volume makes that small gap easy to detect statistically. It may matter at scale, but it does not outweigh negative ROI and does not prove that moving traffic into One-to-one will create the same lift.
"""),
        code("""
rate_plot = summary.sort_values("conversion_rate", ascending=True)
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(
    rate_plot["match_type"].astype(str),
    rate_plot["conversion_rate"],
    color="#4C78A8",
)
ax.bar_label(
    bars,
    labels=[f"{value:.2%}" for value in rate_plot["conversion_rate"]],
    padding=4,
)
ax.set_title("Observed conversion rate by match type")
ax.set_xlabel("Conversion rate"); ax.set_ylabel("Match type")
ax.xaxis.set_major_formatter(PercentFormatter(1.0))
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "rate_comparison.png", dpi=180, bbox_inches="tight")
plt.show()
"""),
        md("""
## Multiple-Comparison Corrections

There are three CPA comparisons and three conversion-rate comparisons, six in total. At an uncorrected 5% threshold, the expected number of false positives is 0.30 across the full set. Bonferroni uses a stricter threshold; FDR adjusts p-values while retaining more power.
"""),
        code("""
total_comparisons = cpa_comparisons + conversion_comparisons
expected_false_positives = total_comparisons * ALPHA
correction_summary = pd.DataFrame([
    {"metric_family": "CPA", "method": "Uncorrected", "significant_count": int(cpa_tests["significant_uncorrected"].sum()), "total_comparisons": cpa_comparisons},
    {"metric_family": "CPA", "method": "Bonferroni", "significant_count": int(cpa_tests["significant_bonferroni"].sum()), "total_comparisons": cpa_comparisons},
    {"metric_family": "CPA", "method": "FDR", "significant_count": int(cpa_tests["significant_fdr"].sum()), "total_comparisons": cpa_comparisons},
    {"metric_family": "Conversion rate", "method": "Uncorrected", "significant_count": int(conversion_tests["significant_uncorrected"].sum()), "total_comparisons": conversion_comparisons},
    {"metric_family": "Conversion rate", "method": "Bonferroni", "significant_count": int(conversion_tests["significant_bonferroni"].sum()), "total_comparisons": conversion_comparisons},
    {"metric_family": "Conversion rate", "method": "FDR", "significant_count": int(conversion_tests["significant_fdr"].sum()), "total_comparisons": conversion_comparisons},
])
correction_summary["expected_false_positives_at_0_05"] = correction_summary["total_comparisons"] * ALPHA
print(f"Total comparisons: {total_comparisons}; expected false positives at alpha=.05: {expected_false_positives:.2f}")
display(correction_summary)
correction_summary.to_csv(OUTPUT_DIR / "multiple_comparison_summary.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(data=correction_summary, x="method", y="significant_count", hue="metric_family",
            order=["Uncorrected", "Bonferroni", "FDR"], ax=ax)
ax.set_title("Significant pairwise results after correction")
ax.set_xlabel("Correction method"); ax.set_ylabel("Number of significant comparisons")
ax.set_ylim(0, max(correction_summary["total_comparisons"]) + .5)
ax.legend(title="Metric family")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "correction_comparison.png", dpi=180, bbox_inches="tight")
plt.show()
"""),
        md("""
CPA has two significant pairs before correction, one after Bonferroni and two after FDR. Conversion rate has two under all three methods. The corrections do not reverse the marketing conclusion: One-to-one remains the strongest relative group, Phrase remains the weakest, and negative ROI still blocks a Scale recommendation.
"""),
        md("""
## Turning Evidence into a Marketing Decision

The classification combines volume, CPA, ROAS and the bootstrap ROI interval. `Scale` requires enough volume and an ROI interval that stays above zero; no group qualifies. `Maintain` is used for the strongest high-volume group when it is still unprofitable. `Reduce/Pause` requires the weakest ROAS and an ROI interval that remains negative. The remaining group is marked `Optimise/Test`.
"""),
        code("""
decision = summary.merge(bootstrap_ci, on=["match_type", "roi"], how="left")
median_volume = decision["conversions"].median()
best_roi = decision["roi"].max()
weakest_roas = decision["roas"].min()
def classify(row):
    if row.roi_ci_low > 0 and row.conversions >= median_volume:
        return "Scale"
    if row.roi == best_roi and row.conversions >= median_volume:
        return "Maintain"
    if row.roas == weakest_roas and row.roi_ci_high < 0:
        return "Reduce/Pause"
    return "Optimise/Test"
decision["decision"] = decision.apply(classify, axis=1)
decision["rationale"] = decision.apply(
    lambda r: f"{int(r.conversions):,} conversions; CPA ${r.cpa:.2f}; ROAS {r.roas:.3f}; ROI {r.roi:.1%} (cluster 95% CI {r.roi_ci_low:.1%} to {r.roi_ci_high:.1%}).", axis=1)
display(decision[["match_type","observations","ad_groups","conversions","cpa","roas","roi","roi_ci_low","roi_ci_high","decision","rationale"]])
decision.to_csv(OUTPUT_DIR / "business_decision_matrix.csv", index=False)
"""),
        md("""
## A Guardrailed $500,000 Planning Scenario

This is a planning scenario, not a return forecast. The score weights CPA efficiency at 40%, ROAS at 40% and conversion-volume reliability at 20%. Each match type must receive between 20% and 40% of budget. The cap prevents the historically dominant One-to-one group from taking most of the money; the floor keeps enough budget for controlled learning.

Because every historical ROI estimate is negative, the $500,000 should be treated as an upper planning envelope and released in stages, not committed all at once.
"""),
        code("""
allocation = budget_recommendation(summary, budget=500_000)
assert allocation["allocation"].sum() == 500_000
display(allocation[["match_type","allocation","allocation_pct","historical_cost_share","cpa","roas","roi","justification","principal_risk"]])
allocation.to_csv(OUTPUT_DIR / "budget_allocation.csv", index=False)

sensitivity = sensitivity_scenarios(allocation)
display(sensitivity)
sensitivity.to_csv(OUTPUT_DIR / "sensitivity_scenarios.csv", index=False)
"""),
        md("""
The rule assigns $200,000 to One-to-one, $200,000 to Exact and $100,000 to Phrase. Under unchanged historical CPC, conversion rate and revenue per conversion, the model estimates about $437,000 in revenue and a $63,000 loss. The downside scenario widens the loss to roughly $178,000. The upside scenario produces about $88,000 in profit only when CPC falls 10% while conversion rate and revenue per conversion each rise 10%.

This sensitivity shows what would have to change for the economics to improve. It is not a prediction: auction prices, traffic quality and conversion volume may change when spend changes.
"""),
        code("""
fig, axes = plt.subplots(1, 2, figsize=(14,5))
sns.barplot(data=allocation, x="match_type", y="allocation", color="#4C78A8", ax=axes[0])
axes[0].set_title("Proposed allocation with 20%–40% guardrails")
axes[0].set_xlabel(""); axes[0].set_ylabel("Allocation ($)")
sns.barplot(data=sensitivity, x="scenario", y="estimated_profit", color="#F58518", ax=axes[1])
axes[1].axhline(0,color="black",lw=1); axes[1].set_title("Estimated profit changes sharply by scenario")
axes[1].set_xlabel(""); axes[1].set_ylabel("Estimated profit ($)")
fig.tight_layout(); fig.savefig(OUTPUT_DIR / "budget_and_sensitivity.png", dpi=180, bbox_inches="tight"); plt.show()
"""),
        md("""
## Marketing applicability

| Area | Demonstrated here | Transferable method | Additional data required |
|---|---|---|---|
| Paid Search | Impressions→clicks→conversions→reported revenue/cost by match type and device | Funnel KPIs, unit economics, guarded allocation | Keywords/search terms, bids, quality score, attribution, incrementality, margin |
| Paid Social / Meta | Not contained | Same funnel and uncertainty framework | Campaign/ad set/creative, reach, frequency, view/click attribution, audience |
| Display | Not contained | CTR/CPC/conversion and controlled testing | Viewability, placements, reach/frequency, view-through attribution |
| Email / CRM | Not contained | Proportion tests, revenue per conversion, experiments | Sends, deliveries, opens, clicks, users, holdout assignment, unsubscribe |
| Organic | Not contained | Funnel rates and cohort uncertainty | Queries, rankings, landing pages, sessions, assisted conversions, content cost |
| Offline / brand | Not contained | Scenario planning and experimental design | Geography/store exposure, reach, brand lift, matched controls, MMM inputs |

Only the paid-search findings are evidenced here. The measurement approach can transfer to other channels, but the numerical results cannot.
"""),
        md("""
## 30/60/90-day action plan

| Horizon | Action | Metrics and guardrails |
|---|---|---|
| 0–30 days | Maintain One-to-one under the 40% cap; reduce Phrase exposure; audit search terms, conversion definitions, mobile landing pages, revenue mapping, and the inconsistent published conversion-rate field. | Recalculated CTR/CVR/CPC/CPA, revenue per conversion, ROAS/ROI; no budget increase while marginal ROI is negative. |
| 31–60 days | Run controlled creative/landing-page and match-type tests with pre-registered primary outcomes; add negative keywords and separate device reporting. | Random assignment where feasible, sample-ratio checks, incremental conversions, uncertainty intervals, FDR-controlled secondary metrics. |
| 61–90 days | Reallocate only after tests reach planned sample size; scale cells with positive incremental economics and stable quality. | Incremental CPA/ROAS, gross-margin contribution, new-customer rate, attribution lag, saturation and frequency. |

For a future A/B test, define one treatment difference, randomize eligible traffic within comparable auctions, log assignment/exposure before outcomes, choose conversion rate or profit per eligible search as the primary metric, calculate sample size in advance, maintain a holdout, and analyze intention-to-treat. Do not reuse the observational comparisons here as an experimental control.
"""),
        md("## Reproducible Results Record"),
        code("""
overall = aggregate_performance(df.assign(portfolio="All paid search"), "portfolio").iloc[0]
analysis_summary = {
    "rows": int(len(df)), "months": [str(x) for x in df["month"].cat.categories],
    "ad_groups": int(df["ad_group"].nunique()),
    "overall": {k: float(overall[k]) for k in ["impressions","clicks","conversions","cost","revenue","ctr","conversion_rate","cpc","cpa","revenue_per_conversion","profit","roas","roi","profit_margin"]},
    "kruskal": {"statistic": float(kruskal.statistic), "p_value": float(kruskal.pvalue)},
    "conversion_chi_square": {"statistic": float(chi2), "p_value": float(chi_p), "cramers_v": float(cramers_v)},
    "cpa_comparisons": {
        "total": int(cpa_comparisons),
        "significant_uncorrected": int(cpa_tests["significant_uncorrected"].sum()),
        "significant_bonferroni": int(cpa_tests["significant_bonferroni"].sum()),
        "significant_fdr": int(cpa_tests["significant_fdr"].sum()),
    },
    "conversion_comparisons": {
        "total": int(conversion_comparisons),
        "significant_uncorrected": int(conversion_tests["significant_uncorrected"].sum()),
        "significant_bonferroni": int(conversion_tests["significant_bonferroni"].sum()),
        "significant_fdr": int(conversion_tests["significant_fdr"].sum()),
    },
    "budget_total": int(allocation["allocation"].sum()),
    "allocation": {str(row.match_type): int(row.allocation) for row in allocation.itertuples()},
    "decisions": {str(row.match_type): row.decision for row in decision.itertuples()},
    "base_sensitivity": sensitivity.loc[sensitivity.scenario.eq("Base")].iloc[0].to_dict(),
}
with open(OUTPUT_DIR / "analysis_summary.json", "w") as handle:
    json.dump(analysis_summary, handle, indent=2)
print(json.dumps(analysis_summary, indent=2))
"""),
        md("""
## What This Means

The statistical tests answer a useful but limited question: which historical patterns are too consistent to dismiss as random noise under the model? They do not decide where the next dollar should go.

For this campaign, One-to-one has a lower mean CPA than Exact and Phrase after FDR correction. Its conversion advantage is also consistent but small in percentage-point terms. The negative ROI intervals remain the stronger commercial constraint. Maintain One-to-one, optimise Exact and reduce Phrase exposure while the team fixes measurement and runs prospective tests. Do not scale any group until marginal revenue covers media cost under an agreed business definition.
"""),
    ]
    write_notebook("statistical_analysis.ipynb", cells)


def build_power():
    cells = [
        md("""
# Prospective Power Analysis

## Executive Summary

This notebook answers a planning question: how much traffic would a future two-group experiment need to detect a worthwhile change in conversion rate?

The target is 80% statistical power. In plain language, if the specified improvement is real and all model assumptions hold, a study of the planned size should detect it about 80% of the time. This does not mean there is an 80% chance that a result is true.

Historical traffic is used only to estimate planning capacity. The source data is monthly, so the 30/60/90/120/180-day views are future scenarios—not reconstructed daily observations.
"""),
        md("""
## Planning Question and Method

The planned outcome is click-to-conversion rate. The calculation assumes two equally sized, independent groups: control and treatment.

Statistical power is the chance that a test will detect a specified effect when that effect is genuinely present. The minimum detectable effect (MDE) is the smallest conversion-rate gap that a design of a given size is expected to detect reliably. Smaller effects require more traffic.

The normal approximation estimates sample size for target relative lifts and MDE for fixed traffic windows. A live design would still need adjustments for auction constraints, repeated users, seasonality, attribution lag, traffic loss and an uneven split between groups.

**H₀:** future treatment and control conversion rates are equal.

**H₁:** they differ.

**Target power:** 80%. **Two-sided α:** 0.05. **Allocation:** 50/50.
"""),
        code("""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import norm

for candidate in [Path.cwd(), *Path.cwd().parents]:
    if (candidate / "src" / "marketing_analysis.py").exists():
        PROJECT_ROOT = candidate
        break
else:
    raise FileNotFoundError("Run from the repository root or notebooks directory.")
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from marketing_analysis import prepare_data, aggregate_performance

DATA_PATH = PROJECT_ROOT / "data" / "shopping_mall_paid_search.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"; OUTPUT_DIR.mkdir(exist_ok=True)
df = prepare_data(DATA_PATH)
overall = aggregate_performance(df.assign(portfolio="All"), "portfolio").iloc[0]
BASELINE_RATE = overall["conversion_rate"]
BASE_CPA = overall["cpa"]
HISTORICAL_DAYS = 153  # July 1 through November 30, 2021
CLICKS_PER_CALENDAR_DAY = overall["clicks"] / HISTORICAL_DAYS
RNG_SEED = 42
ALPHA = 0.05; POWER = 0.80
Z_ALPHA = norm.ppf(1-ALPHA/2); Z_POWER = norm.ppf(POWER)
print(f"Historical baseline conversion rate: {BASELINE_RATE:.3%}")
print(f"Historical aggregate CPA: ${BASE_CPA:.2f}")
print(f"Observed aggregate clicks / 153 calendar days: {CLICKS_PER_CALENDAR_DAY:,.1f}")
"""),
        md("""
## Required Empirical Power Analysis for CPA

The simulation asks how often an independent t-test would detect a true CPA difference under the lab assumptions. Channel A is centered on the historical CPA. Channel B is 5%, 10%, 15% or 20% higher. Both use a standard deviation equal to 15% of base CPA, with simulated values floored at 50% of base CPA.
"""),
        code("""
def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=0.05):
    seed = RNG_SEED + int(round(true_diff_pct * 10_000)) * 1_000 + int(n_days)
    rng = np.random.default_rng(seed)
    standard_deviation = base_cpa * 0.15
    minimum_cpa = base_cpa * 0.50
    significant_results = 0
    for _ in range(n_sim):
        channel_a = np.maximum(rng.normal(base_cpa, standard_deviation, n_days), minimum_cpa)
        channel_b = np.maximum(
            rng.normal(base_cpa * (1 + true_diff_pct), standard_deviation, n_days),
            minimum_cpa,
        )
        p_value = stats.ttest_ind(channel_a, channel_b, equal_var=True).pvalue
        significant_results += p_value < alpha
    return significant_results / n_sim

effect_sizes = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [30, 60, 90, 120, 180]
cpa_power_rows = []
for effect_size in effect_sizes:
    for n_days in sample_sizes:
        cpa_power_rows.append({
            "effect_size_pct": int(effect_size * 100),
            "n_days": n_days,
            "power": empirical_power_cpa(effect_size, BASE_CPA, n_days),
        })
cpa_power = pd.DataFrame(cpa_power_rows)
display(cpa_power.pivot(index="n_days", columns="effect_size_pct", values="power"))
cpa_power.to_csv(OUTPUT_DIR / "cpa_power_results.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5))
for effect_size, group in cpa_power.groupby("effect_size_pct"):
    ax.plot(group["n_days"], group["power"], marker="o", label=f"{effect_size}% CPA difference")
ax.axhline(.80, color="black", linestyle="--", label="80% target")
ax.set_title("Empirical power to detect CPA differences")
ax.set_xlabel("Days per group"); ax.set_ylabel("Power")
ax.set_ylim(0, 1.03); ax.grid(alpha=.3); ax.legend()
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "power_analysis_cpa.png", dpi=180, bbox_inches="tight")
plt.show()
"""),
        md("""
### Minimum sample size and current-data adequacy

The next table finds the first tested duration that reaches 80% power for each planned effect. It also checks whether 90 days would be sufficient under the same simulation assumptions.
"""),
        code("""
minimum_rows = []
for effect_size in [5, 10, 15, 20]:
    effect_results = cpa_power.loc[cpa_power["effect_size_pct"].eq(effect_size)].sort_values("n_days")
    qualifying = effect_results.loc[effect_results["power"].ge(.80), "n_days"]
    power_at_90 = effect_results.loc[effect_results["n_days"].eq(90), "power"].iloc[0]
    minimum_rows.append({
        "effect_size_pct": effect_size,
        "minimum_tested_days_for_80_power": int(qualifying.iloc[0]) if not qualifying.empty else np.nan,
        "power_at_90_days": power_at_90,
        "is_90_days_sufficient": power_at_90 >= .80,
    })
cpa_minimum_days = pd.DataFrame(minimum_rows)
display(cpa_minimum_days)
cpa_minimum_days.to_csv(OUTPUT_DIR / "cpa_minimum_sample_size.csv", index=False)

cpa_tests_path = OUTPUT_DIR / "cpa_pairwise_tests.csv"
if not cpa_tests_path.exists():
    raise FileNotFoundError("Run statistical_analysis.ipynb before power_analysis.ipynb")
cpa_tests = pd.read_csv(cpa_tests_path)
significant_cpa_pairs = cpa_tests.loc[cpa_tests["significant_fdr"]].copy()
adequacy_rows = []
for row in significant_cpa_pairs.itertuples():
    observed_difference = abs(row.percentage_difference) / 100
    baseline = min(row.mean_cpa_a, row.mean_cpa_b)
    power_90 = empirical_power_cpa(observed_difference, baseline, 90)
    estimated_days = 90
    if power_90 < .80:
        estimated_days = np.nan
        for candidate_days in range(100, 721, 10):
            if empirical_power_cpa(observed_difference, baseline, candidate_days) >= .80:
                estimated_days = candidate_days
                break
    adequacy_rows.append({
        "comparison": f"{row.group_a} vs {row.group_b}",
        "observed_cpa_difference_pct": abs(row.percentage_difference),
        "power_at_90_days": power_90,
        "estimated_days_for_80_power": estimated_days,
        "additional_days_needed": max(0, estimated_days - 90) if pd.notna(estimated_days) else np.nan,
        "is_90_days_sufficient": power_90 >= .80,
    })
cpa_data_adequacy = pd.DataFrame(adequacy_rows, columns=[
    "comparison", "observed_cpa_difference_pct", "power_at_90_days",
    "estimated_days_for_80_power", "additional_days_needed", "is_90_days_sufficient"
])
if cpa_data_adequacy.empty:
    print("No CPA pair remains significant after FDR; no pair-specific adequacy assessment is forced.")
else:
    display(cpa_data_adequacy)
cpa_data_adequacy.to_csv(OUTPUT_DIR / "cpa_data_adequacy.csv", index=False)
"""),
        md("""
The power results are planning aids, not evidence that the monthly rows are daily observations. The pair-specific table is limited to CPA differences that survived FDR in the statistical notebook.
"""),
        md("## Additional Extension: Traffic Needed for Conversion-Rate Lifts"),
        code("""
def required_n_per_arm(p1, p2, alpha=.05, power=.80):
    z_alpha = norm.ppf(1-alpha/2); z_power = norm.ppf(power)
    pooled = (p1+p2)/2
    numerator = (z_alpha*np.sqrt(2*pooled*(1-pooled)) + z_power*np.sqrt(p1*(1-p1)+p2*(1-p2)))**2
    return int(np.ceil(numerator/(p2-p1)**2))

required_rows = []
for relative_lift in [.05,.10,.15,.20]:
    treatment_rate = BASELINE_RATE*(1+relative_lift)
    n_arm = required_n_per_arm(BASELINE_RATE, treatment_rate)
    required_rows.append({"relative_lift": relative_lift, "baseline_rate": BASELINE_RATE,
                          "treatment_rate": treatment_rate, "absolute_lift_pp": 100*(treatment_rate-BASELINE_RATE),
                          "required_clicks_per_arm": n_arm, "required_total_clicks": 2*n_arm,
                          "estimated_calendar_days_at_historical_volume": 2*n_arm/CLICKS_PER_CALENDAR_DAY})
required = pd.DataFrame(required_rows)
display(required)
required.to_csv(OUTPUT_DIR / "power_required_sample.csv", index=False)
"""),
        md("""
### How to read the sample-size table

At the historical baseline conversion rate of 10.38%, detecting a 5% relative lift—about 0.52 percentage points—requires roughly 55,386 clicks per group, or 110,772 in total. A 10% relative lift requires about 14,142 clicks per group because a larger change is easier to detect.

Using the historical average traffic only as a capacity guide, the 5% scenario corresponds to about 18 calendar days. That estimate is not a recommended test duration: the team may need a longer window to cover weekday patterns, attribution delay and auction variation.
"""),
        md("""
## Prospective 30/60/90/120/180-Day Scenarios

The calculation converts total historical volume into an average planning rate and assumes an even future split. It does not create daily records or assume that traffic was actually stable each day.
"""),
        code("""
window_rows = []
for days in [30,60,90,120,180]:
    total_clicks = CLICKS_PER_CALENDAR_DAY*days
    n_arm = total_clicks/2
    mde_abs = (Z_ALPHA+Z_POWER)*np.sqrt(2*BASELINE_RATE*(1-BASELINE_RATE)/n_arm)
    window_rows.append({"prospective_days": days, "estimated_total_clicks": total_clicks,
                        "estimated_clicks_per_arm": n_arm, "mde_absolute_pp": 100*mde_abs,
                        "mde_relative": mde_abs/BASELINE_RATE})
windows = pd.DataFrame(window_rows)
display(windows)
windows.to_csv(OUTPUT_DIR / "power_window_scenarios.csv", index=False)
"""),
        md("""
### Business interpretation

With traffic similar to the historical average, a 30-day test could detect an absolute conversion-rate difference of about 0.40 percentage points, or a 3.87% relative lift from the baseline. Extending the planning window to 180 days lowers the approximate MDE to 0.16 points, or a 1.58% relative lift.

In practical terms, longer tests can detect smaller changes, but statistical sensitivity is not the only consideration. The team should choose an effect that would actually change a budget or creative decision; there is little value in powering a test to find a difference too small to matter commercially.
"""),
        code("""
fig, ax = plt.subplots(figsize=(9,5))
ax.plot(windows["prospective_days"], windows["mde_relative"]*100, marker="o", color="#4C78A8")
ax.set(title="Longer test windows can detect smaller conversion lifts", xlabel="Planning window (days)", ylabel="Approximate MDE (% relative lift)")
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUTPUT_DIR / "power_scenarios.png", dpi=180, bbox_inches="tight"); plt.show()
"""),
        md("""
## What This Plan Can and Cannot Support

The calculations use 80% power, a two-sided 5% significance threshold and a 50/50 traffic split. They are suitable for initial planning, not final experiment approval.

The baseline comes from observational history and may change. The monthly dataset cannot reveal weekday patterns, novelty effects, ramp-up, contamination or attribution lag. Calendar estimates therefore describe possible traffic capacity, not promised delivery dates.

Before launch, the team should choose the smallest lift worth acting on, confirm eligible traffic and gross-margin economics, and recalculate power at the actual randomisation unit. The test plan should also define the primary metric, stopping rule and treatment of secondary metrics in advance. Random assignment, exposure logging, sample-ratio checks and intention-to-treat analysis remain essential.
"""),
    ]
    write_notebook("power_analysis.ipynb", cells)


if __name__ == "__main__":
    NOTEBOOKS.mkdir(exist_ok=True)
    build_exploration()
    build_statistics()
    build_power()
    print("Built data_exploration.ipynb, statistical_analysis.ipynb, power_analysis.ipynb")
