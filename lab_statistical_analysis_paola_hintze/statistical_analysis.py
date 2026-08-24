"""Run pairwise tests and multiple-comparison corrections."""

from __future__ import annotations

import itertools
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-paola-stat-lab")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import false_discovery_control, fisher_exact, ttest_ind


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
ALPHA = 0.05


def effect_label(value: float) -> str:
    magnitude = abs(value)
    if magnitude < 0.2:
        return "negligible"
    if magnitude < 0.5:
        return "small"
    if magnitude < 0.8:
        return "medium"
    return "large"


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    pooled = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return float((np.mean(b) - np.mean(a)) / pooled) if pooled > 0 else np.nan


def compare_daily_cpa(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    channels = sorted(frame["channel"].unique())
    for group_a, group_b in itertools.combinations(channels, 2):
        a = frame.loc[frame["channel"].eq(group_a), "cpa"].dropna().to_numpy()
        b = frame.loc[frame["channel"].eq(group_b), "cpa"].dropna().to_numpy()
        if len(a) < 2 or len(b) < 2:
            t_stat, p_value, d_value = np.nan, np.nan, np.nan
        else:
            test = ttest_ind(a, b, equal_var=False, nan_policy="omit")
            t_stat, p_value, d_value = float(test.statistic), float(test.pvalue), cohen_d(a, b)
        mean_a, mean_b = float(np.mean(a)), float(np.mean(b))
        difference = mean_b - mean_a
        rows.append(
            {
                "group_a": group_a,
                "group_b": group_b,
                "n_a": len(a),
                "n_b": len(b),
                "mean_cpa_a": mean_a,
                "mean_cpa_b": mean_b,
                "difference_b_minus_a": difference,
                "percent_difference": difference / mean_a * 100 if mean_a else np.nan,
                "t_statistic": t_stat,
                "p_value": p_value,
                "cohen_d": d_value,
                "effect_size": effect_label(d_value) if np.isfinite(d_value) else "not estimable",
                "significant_uncorrected": bool(p_value < ALPHA) if np.isfinite(p_value) else False,
            }
        )
    return pd.DataFrame(rows)


def compare_conversion_rates(frame: pd.DataFrame) -> pd.DataFrame:
    totals = (
        frame.groupby("channel", as_index=False)
        .agg(conversions=("conversions", "sum"), attempts=("clicks", "sum"))
    )
    totals["non_conversions"] = totals["attempts"] - totals["conversions"]
    totals["conversion_rate"] = totals["conversions"] / totals["attempts"]
    totals.to_csv(OUTPUTS / "conversion_counts_by_channel.csv", index=False)
    indexed = totals.set_index("channel")
    rows: list[dict[str, object]] = []
    for group_a, group_b in itertools.combinations(sorted(indexed.index), 2):
        a, b = indexed.loc[group_a], indexed.loc[group_b]
        table = [
            [int(a["conversions"]), int(a["non_conversions"])],
            [int(b["conversions"]), int(b["non_conversions"])],
        ]
        test = fisher_exact(table, alternative="two-sided")
        rate_a, rate_b = float(a["conversion_rate"]), float(b["conversion_rate"])
        rows.append(
            {
                "group_a": group_a,
                "group_b": group_b,
                "conversions_a": int(a["conversions"]),
                "attempts_a": int(a["attempts"]),
                "conversions_b": int(b["conversions"]),
                "attempts_b": int(b["attempts"]),
                "rate_a": rate_a,
                "rate_b": rate_b,
                "rate_difference_b_minus_a": rate_b - rate_a,
                "relative_difference_pct": (rate_b - rate_a) / rate_a * 100 if rate_a else np.nan,
                "odds_ratio": float(test.statistic),
                "p_value": float(test.pvalue),
                "significant_uncorrected": bool(test.pvalue < ALPHA),
            }
        )
    return pd.DataFrame(rows)


def add_corrections(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    valid = results["p_value"].notna()
    count = int(valid.sum())
    results["bonferroni_alpha"] = ALPHA / count
    results["significant_bonferroni"] = False
    results.loc[valid, "significant_bonferroni"] = (
        results.loc[valid, "p_value"] < ALPHA / count
    )
    results["p_value_fdr"] = np.nan
    results.loc[valid, "p_value_fdr"] = false_discovery_control(
        results.loc[valid, "p_value"].to_numpy(), method="bh"
    )
    results["significant_fdr"] = results["p_value_fdr"].lt(ALPHA).fillna(False)
    return results


def plot_heatmap(results: pd.DataFrame, channels: list[str]) -> None:
    matrix = pd.DataFrame(1.0, index=channels, columns=channels)
    for row in results.itertuples():
        matrix.loc[row.group_a, row.group_b] = row.p_value
        matrix.loc[row.group_b, row.group_a] = row.p_value
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, fmt=".3f", cmap="RdYlGn", vmin=0, vmax=0.10, ax=ax)
    ax.set_title("Welch t-test p-values for daily CPA\n(unadjusted; red = smaller p-value)")
    fig.tight_layout()
    fig.savefig(FIGURES / "cpa_comparison_heatmap.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_conversion_rates() -> None:
    totals = pd.read_csv(OUTPUTS / "conversion_counts_by_channel.csv").sort_values(
        "conversion_rate"
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(totals["channel"], totals["conversion_rate"], color="#4776E6")
    ax.bar_label(bars, labels=[f"{value:.2%}" for value in totals["conversion_rate"]], padding=4)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.1%}"))
    ax.set_title("Aggregate click-to-conversion rate by channel")
    ax.set_xlabel("Conversion rate")
    fig.tight_layout()
    fig.savefig(FIGURES / "rate_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def correction_summary(cpa: pd.DataFrame, fisher: pd.DataFrame) -> pd.DataFrame:
    records = []
    for family, data in [("Daily CPA (Welch t-test)", cpa), ("Conversion rate (Fisher)", fisher)]:
        for method, column in [
            ("Uncorrected", "significant_uncorrected"),
            ("Bonferroni", "significant_bonferroni"),
            ("Benjamini-Hochberg FDR", "significant_fdr"),
        ]:
            records.append(
                {
                    "test_family": family,
                    "method": method,
                    "comparisons": int(data["p_value"].notna().sum()),
                    "significant_comparisons": int(data[column].sum()),
                }
            )
    return pd.DataFrame(records)


def plot_corrections(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(
        data=summary,
        x="method",
        y="significant_comparisons",
        hue="test_family",
        ax=ax,
    )
    ax.set_title("Impact of multiple-comparison correction")
    ax.set_xlabel("")
    ax.set_ylabel("Significant pairwise comparisons")
    ax.legend(title="Test family")
    fig.tight_layout()
    fig.savefig(FIGURES / "correction_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    frame = pd.read_csv(DATA / "marketing_data.csv", parse_dates=["date"])
    cpa = add_corrections(compare_daily_cpa(frame))
    fisher = add_corrections(compare_conversion_rates(frame))
    cpa.to_csv(OUTPUTS / "cpa_pairwise_comparisons.csv", index=False)
    fisher.to_csv(OUTPUTS / "conversion_fisher_comparisons.csv", index=False)
    summary = correction_summary(cpa, fisher)
    summary.to_csv(OUTPUTS / "correction_summary.csv", index=False)
    total_tests = int(cpa["p_value"].notna().sum() + fisher["p_value"].notna().sum())
    (OUTPUTS / "multiple_comparisons_note.txt").write_text(
        f"Total pairwise tests: {total_tests}\n"
        f"Expected false positives at alpha=0.05 under all nulls: {total_tests * ALPHA:.2f}\n"
        "Bonferroni controls family-wise error; BH controls expected false discovery rate.\n",
        encoding="utf-8",
    )
    channels = sorted(frame["channel"].unique())
    plot_heatmap(cpa, channels)
    plot_conversion_rates()
    plot_corrections(summary)
    print("CPA comparisons:", len(cpa), "FDR significant:", int(cpa["significant_fdr"].sum()))
    print("Fisher comparisons:", len(fisher), "FDR significant:", int(fisher["significant_fdr"].sum()))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

