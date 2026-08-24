import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, fisher_exact
from itertools import combinations


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/marketing_data_clean.csv"
TABLE_DIR = "results/tables"
FIGURE_DIR = "results/figures"

ALPHA = 0.05


# ============================================================
# LOAD DATA
# ============================================================

print("Loading processed dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df):,} rows.")
print(f"Platforms: {df['platform'].nunique()}")


# ============================================================
# PART 1 — PAIRWISE T-TESTS
# ============================================================

print("\n" + "=" * 60)
print("PAIRWISE T-TESTS")
print("=" * 60)

# We use CPA as our main continuous metric.
# Rows with zero conversions cannot have a valid CPA.
cpa_data = df[
    (df["conversions"] > 0) &
    (df["cpa"].notna()) &
    (np.isfinite(df["cpa"]))
].copy()

platforms = sorted(cpa_data["platform"].unique())

print(f"Platforms included in CPA analysis: {len(platforms)}")
print(platforms)


def cohens_d(group_a, group_b):
    """Calculate Cohen's d using pooled standard deviation."""

    n_a = len(group_a)
    n_b = len(group_b)

    var_a = np.var(group_a, ddof=1)
    var_b = np.var(group_b, ddof=1)

    pooled_sd = np.sqrt((var_a + var_b) / 2)

    if pooled_sd == 0:
        return np.nan

    return (np.mean(group_b) - np.mean(group_a)) / pooled_sd


def effect_size_label(d):
    """Interpret Cohen's d."""

    if pd.isna(d):
        return "undefined"
    elif abs(d) < 0.2:
        return "negligible"
    elif abs(d) < 0.5:
        return "small"
    elif abs(d) < 0.8:
        return "medium"
    else:
        return "large"


ttest_results = []


for platform_a, platform_b in combinations(platforms, 2):

    values_a = cpa_data.loc[
        cpa_data["platform"] == platform_a, "cpa"
    ]

    values_b = cpa_data.loc[
        cpa_data["platform"] == platform_b, "cpa"
    ]

    # Welch's t-test is safer when groups may have different variances.
    t_stat, p_value = ttest_ind(
        values_a,
        values_b,
        equal_var=False
    )

    mean_a = values_a.mean()
    mean_b = values_b.mean()

    difference = mean_b - mean_a

    if mean_a != 0:
        percentage_difference = (difference / mean_a) * 100
    else:
        percentage_difference = np.nan

    d = cohens_d(values_a, values_b)

    ttest_results.append({
        "metric": "CPA",
        "group_a": platform_a,
        "group_b": platform_b,
        "n_a": len(values_a),
        "n_b": len(values_b),
        "mean_a": mean_a,
        "mean_b": mean_b,
        "difference_b_minus_a": difference,
        "percentage_difference": percentage_difference,
        "t_statistic": t_stat,
        "p_value": p_value,
        "cohens_d": d,
        "effect_size": effect_size_label(d),
        "significant_uncorrected": p_value < ALPHA
    })


ttest_df = pd.DataFrame(ttest_results)

ttest_df = ttest_df.sort_values("p_value")

ttest_df.to_csv(
    f"{TABLE_DIR}/cpa_ttest_results.csv",
    index=False
)

print("\nCPA t-test results:")
print(
    ttest_df[
        [
            "group_a",
            "group_b",
            "mean_a",
            "mean_b",
            "p_value",
            "cohens_d",
            "effect_size",
            "significant_uncorrected"
        ]
    ].round(4).to_string(index=False)
)

print(
    f"\nTotal CPA comparisons: {len(ttest_df)}"
)

print(
    f"Significant before correction: "
    f"{ttest_df['significant_uncorrected'].sum()}"
)


# ============================================================
# CPA P-VALUE HEATMAP
# ============================================================

print("\nCreating CPA p-value heatmap...")

p_matrix = pd.DataFrame(
    np.ones((len(platforms), len(platforms))),
    index=platforms,
    columns=platforms
)

for _, row in ttest_df.iterrows():

    a = row["group_a"]
    b = row["group_b"]
    p = row["p_value"]

    p_matrix.loc[a, b] = p
    p_matrix.loc[b, a] = p


plt.figure(figsize=(9, 7))

plt.imshow(
    p_matrix.values,
    cmap="RdYlGn_r",
    vmin=0,
    vmax=0.05
)

plt.colorbar(label="p-value")

plt.xticks(
    range(len(platforms)),
    platforms,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(platforms)),
    platforms
)

for i in range(len(platforms)):
    for j in range(len(platforms)):

        value = p_matrix.iloc[i, j]

        if value < 0.0001:
            text = "<0.0001"
        else:
            text = f"{value:.4f}"

        plt.text(
            j,
            i,
            text,
            ha="center",
            va="center",
            fontsize=8
        )

plt.title("CPA Pairwise Comparison — p-values")
plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/metric_comparison_heatmap.png",
    dpi=300
)

plt.close()

print(
    f"Saved: {FIGURE_DIR}/metric_comparison_heatmap.png"
)


# ============================================================
# PART 2 — FISHER'S EXACT TEST
# ============================================================

print("\n" + "=" * 60)
print("FISHER'S EXACT TEST — CONVERSION RATES")
print("=" * 60)


# Aggregate clicks and conversions by platform.
conversion_summary = (
    df.groupby("platform")
    .agg(
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum")
    )
    .reset_index()
)

conversion_summary["non_conversions"] = (
    conversion_summary["clicks"]
    - conversion_summary["conversions"]
)

conversion_summary["conversion_rate"] = (
    conversion_summary["conversions"]
    / conversion_summary["clicks"]
)


conversion_summary.to_csv(
    f"{TABLE_DIR}/conversion_summary.csv",
    index=False
)

print("\nConversion summary:")
print(
    conversion_summary.round(4).to_string(index=False)
)


fisher_results = []


for platform_a, platform_b in combinations(platforms, 2):

    row_a = conversion_summary[
        conversion_summary["platform"] == platform_a
    ].iloc[0]

    row_b = conversion_summary[
        conversion_summary["platform"] == platform_b
    ].iloc[0]

    table = [
        [
            row_a["conversions"],
            row_a["non_conversions"]
        ],
        [
            row_b["conversions"],
            row_b["non_conversions"]
        ]
    ]

    odds_ratio, p_value = fisher_exact(
        table,
        alternative="two-sided"
    )

    rate_a = row_a["conversion_rate"]
    rate_b = row_b["conversion_rate"]

    difference = rate_b - rate_a

    if rate_a != 0:
        percentage_difference = (
            difference / rate_a
        ) * 100
    else:
        percentage_difference = np.nan

    fisher_results.append({
        "group_a": platform_a,
        "group_b": platform_b,
        "conversions_a": row_a["conversions"],
        "clicks_a": row_a["clicks"],
        "conversion_rate_a": rate_a,
        "conversions_b": row_b["conversions"],
        "clicks_b": row_b["clicks"],
        "conversion_rate_b": rate_b,
        "difference_b_minus_a": difference,
        "percentage_difference": percentage_difference,
        "odds_ratio": odds_ratio,
        "p_value": p_value,
        "significant_uncorrected": p_value < ALPHA
    })


fisher_df = pd.DataFrame(fisher_results)

fisher_df = fisher_df.sort_values("p_value")

fisher_df.to_csv(
    f"{TABLE_DIR}/fisher_exact_results.csv",
    index=False
)

print("\nFisher's exact test results:")

print(
    fisher_df[
        [
            "group_a",
            "group_b",
            "conversion_rate_a",
            "conversion_rate_b",
            "difference_b_minus_a",
            "odds_ratio",
            "p_value",
            "significant_uncorrected"
        ]
    ].round(6).to_string(index=False)
)

print(
    f"\nTotal Fisher comparisons: {len(fisher_df)}"
)

print(
    f"Significant before correction: "
    f"{fisher_df['significant_uncorrected'].sum()}"
)


# ============================================================
# CONVERSION RATE VISUALIZATION
# ============================================================

print("\nCreating conversion rate comparison chart...")

plot_data = conversion_summary.sort_values(
    "conversion_rate",
    ascending=True
)

plt.figure(figsize=(10, 6))

bars = plt.barh(
    plot_data["platform"],
    plot_data["conversion_rate"] * 100
)

plt.xlabel("Conversion Rate (%)")
plt.ylabel("Platform")
plt.title("Conversion Rate by Marketing Platform")

for bar, value in zip(
    bars,
    plot_data["conversion_rate"] * 100
):
    plt.text(
        bar.get_width(),
        bar.get_y() + bar.get_height() / 2,
        f" {value:.2f}%",
        va="center"
    )

plt.tight_layout()

plt.savefig(
    f"{FIGURE_DIR}/rate_comparison.png",
    dpi=300
)

plt.close()

print(
    f"Saved: {FIGURE_DIR}/rate_comparison.png"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("STATISTICAL ANALYSIS COMPLETED")
print("=" * 60)

print("\nFiles created:")

print("- results/tables/cpa_ttest_results.csv")
print("- results/tables/conversion_summary.csv")
print("- results/tables/fisher_exact_results.csv")
print("- results/figures/metric_comparison_heatmap.png")
print("- results/figures/rate_comparison.png")

print("\nNext step:")
print("Multiple comparisons correction — Bonferroni + Benjamini-Hochberg")