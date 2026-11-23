from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import fisher_exact, false_discovery_control, ttest_ind


HERE = Path(__file__).resolve().parent
DATA = HERE / "marketing_data.csv"


def cohens_d(a, b):
    pooled_std = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return (np.mean(b) - np.mean(a)) / pooled_std if pooled_std > 0 else np.nan


def interpret_d(value):
    magnitude = abs(value)
    if magnitude < 0.2:
        return "negligible"
    if magnitude < 0.5:
        return "small"
    if magnitude < 0.8:
        return "medium"
    return "large"


def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    values = np.asarray(data.dropna() if hasattr(data, "dropna") else data)
    if len(values) == 0:
        return np.nan, np.nan
    boot_means = np.asarray([
        np.mean(np.random.choice(values, size=len(values), replace=True))
        for _ in range(n_bootstrap)
    ])
    alpha = 1 - ci_level
    return np.percentile(boot_means, 100 * alpha / 2), np.percentile(boot_means, 100 * (1 - alpha / 2))


def main():
    np.random.seed(42)
    df = pd.read_csv(DATA)
    df["Date"] = pd.to_datetime(df["Date"])

    daily = df.groupby(["Date", "Channel_Used"], as_index=False).agg(
        Cost=("Acquisition_Cost", "sum"),
        Conversions=("Conversions", "sum"),
        Clicks=("Clicks", "sum"),
    )
    daily["CPA"] = daily["Cost"] / daily["Conversions"].replace(0, np.nan)
    daily["Conversion_Rate"] = daily["Conversions"] / daily["Clicks"].replace(0, np.nan)
    daily = daily.replace([np.inf, -np.inf], np.nan)

    channels = sorted(daily["Channel_Used"].dropna().unique())
    cpa_rows = []
    for a, b in combinations(channels, 2):
        values_a = daily.loc[daily["Channel_Used"] == a, "CPA"].dropna()
        values_b = daily.loc[daily["Channel_Used"] == b, "CPA"].dropna()
        if len(values_a) < 2 or len(values_b) < 2:
            continue
        result = ttest_ind(values_a, values_b, equal_var=False, nan_policy="omit")
        difference = values_b.mean() - values_a.mean()
        d = cohens_d(values_a, values_b)
        cpa_rows.append({
            "group_a": a,
            "group_b": b,
            "mean_a": values_a.mean(),
            "mean_b": values_b.mean(),
            "difference_b_minus_a": difference,
            "percentage_difference": difference / values_a.mean() * 100,
            "t_statistic": result.statistic,
            "p_value": result.pvalue,
            "cohens_d": d,
            "effect_size": interpret_d(d),
            "significant_uncorrected": result.pvalue < 0.05,
        })
    cpa = pd.DataFrame(cpa_rows)

    binary = df.groupby("Channel_Used", as_index=False).agg(
        conversions=("Conversions", "sum"),
        attempts=("Clicks", "sum"),
    )
    binary["non_conversions"] = binary["attempts"] - binary["conversions"]
    binary["conversion_rate"] = binary["conversions"] / binary["attempts"]
    print("\nBinary outcome summary:")
    print(binary.to_string(index=False))

    fisher_rows = []
    for a, b in combinations(binary["Channel_Used"], 2):
        ra = binary.loc[binary["Channel_Used"] == a].iloc[0]
        rb = binary.loc[binary["Channel_Used"] == b].iloc[0]
        table = [
            [int(ra["conversions"]), int(ra["non_conversions"])],
            [int(rb["conversions"]), int(rb["non_conversions"])],
        ]
        result = fisher_exact(table, alternative="two-sided")
        difference = rb["conversion_rate"] - ra["conversion_rate"]
        fisher_rows.append({
            "group_a": a,
            "group_b": b,
            "conversions_a": int(ra["conversions"]),
            "attempts_a": int(ra["attempts"]),
            "conversions_b": int(rb["conversions"]),
            "attempts_b": int(rb["attempts"]),
            "rate_a": ra["conversion_rate"],
            "rate_b": rb["conversion_rate"],
            "difference_b_minus_a": difference,
            "odds_ratio": result.statistic,
            "p_value": result.pvalue,
            "significant_uncorrected": result.pvalue < 0.05,
        })
    fisher = pd.DataFrame(fisher_rows)

    cpa_alpha = 0.05 / len(cpa)
    fisher_alpha = 0.05 / len(fisher)
    cpa["significant_bonferroni"] = cpa["p_value"] < cpa_alpha
    fisher["significant_bonferroni"] = fisher["p_value"] < fisher_alpha
    cpa["p_value_fdr"] = false_discovery_control(cpa["p_value"].to_numpy(), method="bh")
    fisher["p_value_fdr"] = false_discovery_control(fisher["p_value"].to_numpy(), method="bh")
    cpa["significant_fdr"] = cpa["p_value_fdr"] < 0.05
    fisher["significant_fdr"] = fisher["p_value_fdr"] < 0.05

    cpa.to_csv(HERE / "cpa_comparisons.csv", index=False, float_format="%.8f")
    fisher.to_csv(HERE / "conversion_rate_comparisons.csv", index=False, float_format="%.8f")

    summary = pd.DataFrame([
        ["CPA", len(cpa), cpa["significant_uncorrected"].sum(), cpa["significant_bonferroni"].sum(), cpa["significant_fdr"].sum()],
        ["Conversion rate", len(fisher), fisher["significant_uncorrected"].sum(), fisher["significant_bonferroni"].sum(), fisher["significant_fdr"].sum()],
    ], columns=["Metric", "Comparisons", "Uncorrected", "Bonferroni", "FDR"])
    summary.to_csv(HERE / "correction_summary.csv", index=False)
    print("\nCorrection summary:")
    print(summary.to_string(index=False))

    sns.set_theme(style="whitegrid")
    matrix = pd.DataFrame(1.0, index=channels, columns=channels)
    for row in cpa.itertuples():
        matrix.loc[row.group_a, row.group_b] = row.p_value
        matrix.loc[row.group_b, row.group_a] = row.p_value
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(matrix, annot=True, fmt=".3g", cmap="RdYlGn_r", vmin=0, vmax=0.05, ax=ax)
    ax.set_title("CPA Pairwise p-values")
    fig.tight_layout()
    fig.savefig(HERE / "metric_comparison_heatmap.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    plot_binary = binary.sort_values("conversion_rate")
    ax.barh(plot_binary["Channel_Used"], plot_binary["conversion_rate"] * 100)
    for i, value in enumerate(plot_binary["conversion_rate"] * 100):
        ax.text(value, i, f" {value:.2f}%")
    ax.set_xlabel("Conversion rate (%)")
    ax.set_title("Conversion Rate by Channel")
    fig.tight_layout()
    fig.savefig(HERE / "rate_comparison.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(summary))
    width = 0.25
    ax.bar(x - width, summary["Uncorrected"], width, label="Uncorrected")
    ax.bar(x, summary["Bonferroni"], width, label="Bonferroni")
    ax.bar(x + width, summary["FDR"], width, label="FDR")
    ax.set_xticks(x, summary["Metric"])
    ax.set_ylabel("Significant comparisons")
    ax.set_title("Effect of Multiple Comparisons Correction")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HERE / "correction_comparison.png", dpi=150)
    plt.close(fig)

    ci_rows = []
    for channel_name in channels:
        data = daily.loc[daily["Channel_Used"] == channel_name, "CPA"].dropna()
        lower, upper = bootstrap_ci(data)
        ci_rows.append({
            "channel": channel_name,
            "mean_cpa": data.mean(),
            "ci95_lower": lower,
            "ci95_upper": upper,
        })
    ci = pd.DataFrame(ci_rows)
    ci.to_csv(HERE / "cpa_confidence_intervals.csv", index=False, float_format="%.4f")

    channel_summary = pd.read_csv(HERE / "channel_summary.csv")
    channel_summary["cpa_rank"] = channel_summary["CPA"].rank(method="min", ascending=True)
    channel_summary["roas_rank"] = channel_summary["ROAS"].rank(method="min", ascending=False)
    channel_summary["conversion_rank"] = channel_summary["Conversion_Rate"].rank(method="min", ascending=False)
    channel_summary["composite_score"] = (
        0.50 * (len(channel_summary) + 1 - channel_summary["cpa_rank"])
        + 0.30 * channel_summary["conversion_rank"]
        + 0.20 * channel_summary["roas_rank"]
    )
    allocation = channel_summary.sort_values("composite_score", ascending=False).copy()
    allocations = 500_000 * allocation["composite_score"] / allocation["composite_score"].sum()
    allocations = allocations.clip(lower=50_000, upper=125_000)
    allocations = allocations * (500_000 / allocations.sum())
    allocation["allocation_usd"] = allocations
    allocation["allocation_pct"] = allocations / 500_000
    allocation[["Channel_Used", "CPA", "ROAS", "Conversion_Rate", "composite_score", "allocation_usd", "allocation_pct"]].to_csv(
        HERE / "budget_allocation.csv", index=False, float_format="%.6f"
    )

    print("\nCPA comparisons:")
    print(cpa.to_string(index=False))
    print("\nFisher comparisons:")
    print(fisher.to_string(index=False))
    print("\nCPA 95% bootstrap confidence intervals:")
    print(ci.to_string(index=False))


if __name__ == "__main__":
    main()
