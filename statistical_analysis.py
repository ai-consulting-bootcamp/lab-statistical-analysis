from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import false_discovery_control, fisher_exact, ttest_ind

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

ALPHA = 0.05
MONTHLY_BUDGET = 500_000


def effect_label(d):
    value = abs(d)
    if value < 0.2:
        return "negligible"
    if value < 0.5:
        return "small"
    if value < 0.8:
        return "medium"
    return "large"


def cohen_d(a, b):
    var_a = np.var(a, ddof=1)
    var_b = np.var(b, ddof=1)
    pooled_std = np.sqrt((var_a + var_b) / 2)
    if pooled_std == 0 or np.isnan(pooled_std):
        return np.nan
    return (np.mean(b) - np.mean(a)) / pooled_std


def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95, seed=42):
    values = np.asarray(data, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.nan, np.nan

    rng = np.random.default_rng(seed)
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        sample = rng.choice(values, size=len(values), replace=True)
        means[i] = sample.mean()

    alpha = 1 - ci_level
    return (
        float(np.quantile(means, alpha / 2)),
        float(np.quantile(means, 1 - alpha / 2)),
    )


def bounded_budget(weights, total_budget, min_share=0.05, max_share=0.25):
    """Allocate proportionally while keeping each of 7 channels between 5% and 25%."""
    weights = pd.Series(weights, dtype=float)
    weights = weights.clip(lower=0.000001)
    free = set(weights.index)
    shares = pd.Series(0.0, index=weights.index)
    remaining = 1.0

    while free:
        free_list = list(free)
        free_weights = weights.loc[free_list]
        proposed = remaining * free_weights / free_weights.sum()

        low = proposed[proposed < min_share]
        high = proposed[proposed > max_share]

        if low.empty and high.empty:
            shares.loc[free_list] = proposed
            break

        changed = False
        for idx in low.index:
            shares.loc[idx] = min_share
            remaining -= min_share
            free.remove(idx)
            changed = True
        for idx in high.index:
            if idx in free:
                shares.loc[idx] = max_share
                remaining -= max_share
                free.remove(idx)
                changed = True

        if not changed:
            shares.loc[free_list] = proposed
            break

    # Small floating-point cleanup.
    shares = shares / shares.sum()
    return shares * total_budget


def main():
    daily_path = ROOT / "daily_channel_metrics.csv"
    data_path = ROOT / "marketing_data.csv"
    summary_path = ROOT / "channel_summary.csv"

    for path in [daily_path, data_path, summary_path]:
        if not path.exists():
            raise FileNotFoundError(
                f"{path.name} is missing. Run data_exploration.py first."
            )

    daily = pd.read_csv(daily_path, parse_dates=["date"])
    data = pd.read_csv(data_path, parse_dates=["date"])
    channel_summary = pd.read_csv(summary_path)

    channels = sorted(daily["channel"].unique())

    # -----------------------------
    # 1) Pairwise t-tests for CPA
    # -----------------------------
    t_rows = []
    for group_a, group_b in combinations(channels, 2):
        a = daily.loc[daily["channel"] == group_a, "cpa"].replace(
            [np.inf, -np.inf], np.nan
        ).dropna().values
        b = daily.loc[daily["channel"] == group_b, "cpa"].replace(
            [np.inf, -np.inf], np.nan
        ).dropna().values

        if len(a) < 2 or len(b) < 2:
            continue

        t_stat, p_value = ttest_ind(a, b, equal_var=False)
        mean_a = float(np.mean(a))
        mean_b = float(np.mean(b))
        difference = mean_b - mean_a
        pct_difference = (
            difference / mean_a * 100 if mean_a != 0 else np.nan
        )
        d = cohen_d(a, b)

        t_rows.append(
            {
                "group_a": group_a,
                "group_b": group_b,
                "n_a": len(a),
                "n_b": len(b),
                "mean_cpa_a": mean_a,
                "mean_cpa_b": mean_b,
                "difference_b_minus_a": difference,
                "pct_difference": pct_difference,
                "t_statistic": t_stat,
                "p_value": p_value,
                "cohen_d": d,
                "effect_size": effect_label(d) if np.isfinite(d) else "undefined",
                "significant_uncorrected": p_value < ALPHA,
            }
        )

    cpa_results = pd.DataFrame(t_rows)

    # -----------------------------
    # 2) Fisher's exact tests
    # -----------------------------
    aggregate = (
        data.groupby("channel", as_index=False)[["clicks", "conversions"]].sum()
    )
    aggregate["non_conversions"] = aggregate["clicks"] - aggregate["conversions"]

    fisher_rows = []
    indexed = aggregate.set_index("channel")
    for group_a, group_b in combinations(channels, 2):
        conv_a = int(indexed.loc[group_a, "conversions"])
        total_a = int(indexed.loc[group_a, "clicks"])
        conv_b = int(indexed.loc[group_b, "conversions"])
        total_b = int(indexed.loc[group_b, "clicks"])
        non_a = total_a - conv_a
        non_b = total_b - conv_b

        odds_ratio, p_value = fisher_exact(
            [[conv_a, non_a], [conv_b, non_b]],
            alternative="two-sided",
        )
        rate_a = conv_a / total_a if total_a else np.nan
        rate_b = conv_b / total_b if total_b else np.nan
        difference = rate_b - rate_a
        pct_difference = (
            difference / rate_a * 100 if rate_a and np.isfinite(rate_a) else np.nan
        )

        fisher_rows.append(
            {
                "group_a": group_a,
                "group_b": group_b,
                "conversions_a": conv_a,
                "attempts_a": total_a,
                "conversion_rate_a": rate_a,
                "conversions_b": conv_b,
                "attempts_b": total_b,
                "conversion_rate_b": rate_b,
                "difference_b_minus_a": difference,
                "pct_difference": pct_difference,
                "odds_ratio": odds_ratio,
                "p_value": p_value,
                "significant_uncorrected": p_value < ALPHA,
            }
        )

    fisher_results = pd.DataFrame(fisher_rows)

    # -----------------------------
    # 3) Multiple comparisons
    # -----------------------------
    total_comparisons = len(cpa_results) + len(fisher_results)
    expected_false_positives = total_comparisons * ALPHA
    print(f"Total pairwise tests: {total_comparisons}")
    print(
        f"Expected false positives at alpha=0.05 by chance alone: "
        f"{expected_false_positives:.2f}"
    )

    for frame in [cpa_results, fisher_results]:
        n_tests = len(frame)
        bonf_alpha = ALPHA / n_tests
        frame["bonferroni_alpha"] = bonf_alpha
        frame["significant_bonferroni"] = frame["p_value"] < bonf_alpha
        frame["p_value_fdr"] = false_discovery_control(
            frame["p_value"].to_numpy(), method="bh"
        )
        frame["significant_fdr"] = frame["p_value_fdr"] < ALPHA

    cpa_results.to_csv(ROOT / "cpa_pairwise_results.csv", index=False)
    fisher_results.to_csv(ROOT / "fisher_pairwise_results.csv", index=False)

    correction_rows = []
    for metric, frame in [
        ("CPA t-tests", cpa_results),
        ("Conversion rate Fisher tests", fisher_results),
    ]:
        correction_rows.extend(
            [
                {
                    "metric": metric,
                    "method": "Uncorrected",
                    "significant_comparisons": int(
                        frame["significant_uncorrected"].sum()
                    ),
                },
                {
                    "metric": metric,
                    "method": "Bonferroni",
                    "significant_comparisons": int(
                        frame["significant_bonferroni"].sum()
                    ),
                },
                {
                    "metric": metric,
                    "method": "Benjamini-Hochberg FDR",
                    "significant_comparisons": int(
                        frame["significant_fdr"].sum()
                    ),
                },
            ]
        )
    correction_summary = pd.DataFrame(correction_rows)
    correction_summary.to_csv(ROOT / "correction_summary.csv", index=False)

    # -----------------------------
    # 4) CPA p-value heatmap
    # -----------------------------
    matrix = pd.DataFrame(1.0, index=channels, columns=channels)
    for _, row in cpa_results.iterrows():
        matrix.loc[row["group_a"], row["group_b"]] = row["p_value"]
        matrix.loc[row["group_b"], row["group_a"]] = row["p_value"]

    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(matrix.values, cmap="RdYlGn_r", vmin=0, vmax=0.10)
    ax.set_xticks(range(len(channels)), labels=channels, rotation=45, ha="right")
    ax.set_yticks(range(len(channels)), labels=channels)
    ax.set_title("Pairwise CPA t-test p-values")
    for i in range(len(channels)):
        for j in range(len(channels)):
            ax.text(j, i, f"{matrix.iloc[i, j]:.3f}", ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=ax, label="p-value")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "metric_comparison_heatmap.png", dpi=160)
    plt.close(fig)

    # -----------------------------
    # 5) Conversion rate chart
    # -----------------------------
    aggregate["conversion_rate"] = (
        aggregate["conversions"] / aggregate["clicks"].replace(0, np.nan)
    )
    aggregate = aggregate.sort_values("conversion_rate")

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(aggregate["channel"], aggregate["conversion_rate"] * 100)
    ax.set_title("Conversion rate by channel")
    ax.set_xlabel("Conversion rate (%)")
    for bar, value in zip(bars, aggregate["conversion_rate"] * 100):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f" {value:.2f}%", va="center")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "rate_comparison.png", dpi=160)
    plt.close(fig)

    # -----------------------------
    # 6) Correction comparison chart
    # -----------------------------
    pivot = correction_summary.pivot(
        index="method", columns="metric", values="significant_comparisons"
    )
    ax = pivot.plot(kind="bar", figsize=(9, 6))
    ax.set_title("Significant comparisons before and after correction")
    ax.set_ylabel("Number significant")
    ax.tick_params(axis="x", rotation=20)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "correction_comparison.png", dpi=160)
    plt.close(fig)

    # -----------------------------
    # 7) Bootstrap 95% CI for daily CPA
    # -----------------------------
    ci_rows = []
    for channel in channels:
        values = daily.loc[daily["channel"] == channel, "cpa"].dropna().values
        lower, upper = bootstrap_ci(values)
        ci_rows.append(
            {
                "channel": channel,
                "mean_daily_cpa": float(np.mean(values)),
                "ci_95_lower": lower,
                "ci_95_upper": upper,
                "n_days_with_defined_cpa": len(values),
            }
        )
    ci_df = pd.DataFrame(ci_rows).sort_values("mean_daily_cpa")
    ci_df.to_csv(ROOT / "confidence_intervals.csv", index=False)

    # -----------------------------
    # 8) Composite ranking and $500K budget
    # -----------------------------
    rank_df = channel_summary[
        ["channel", "cpa", "roas", "conversion_rate_calc"]
    ].copy()

    # 1 = best rank in each metric.
    rank_df["rank_cpa"] = rank_df["cpa"].rank(ascending=True, method="average")
    rank_df["rank_roas"] = rank_df["roas"].rank(ascending=False, method="average")
    rank_df["rank_conversion"] = rank_df["conversion_rate_calc"].rank(
        ascending=False, method="average"
    )

    n_channels = len(rank_df)
    rank_df["composite_score"] = (
        0.4 * (n_channels + 1 - rank_df["rank_cpa"])
        + 0.4 * (n_channels + 1 - rank_df["rank_roas"])
        + 0.2 * (n_channels + 1 - rank_df["rank_conversion"])
    )

    allocation = bounded_budget(
        rank_df.set_index("channel")["composite_score"],
        MONTHLY_BUDGET,
        min_share=0.05,
        max_share=0.25,
    )
    rank_df["recommended_budget"] = rank_df["channel"].map(allocation)
    rank_df["budget_pct"] = rank_df["recommended_budget"] / MONTHLY_BUDGET
    rank_df = rank_df.sort_values("recommended_budget", ascending=False)
    rank_df.to_csv(ROOT / "budget_allocation.csv", index=False)

    # -----------------------------
    # 9) Compact statistical findings
    # -----------------------------
    cpa_sig = cpa_results[cpa_results["significant_fdr"]].copy()
    fisher_sig = fisher_results[fisher_results["significant_fdr"]].copy()

    lines = [
        "# Statistical Findings",
        "",
        f"- CPA pairwise comparisons: {len(cpa_results)}",
        f"- CPA significant before correction: {int(cpa_results['significant_uncorrected'].sum())}",
        f"- CPA significant after Bonferroni: {int(cpa_results['significant_bonferroni'].sum())}",
        f"- CPA significant after FDR: {int(cpa_results['significant_fdr'].sum())}",
        f"- Conversion-rate pairwise comparisons: {len(fisher_results)}",
        f"- Conversion-rate significant before correction: {int(fisher_results['significant_uncorrected'].sum())}",
        f"- Conversion-rate significant after Bonferroni: {int(fisher_results['significant_bonferroni'].sum())}",
        f"- Conversion-rate significant after FDR: {int(fisher_results['significant_fdr'].sum())}",
        "",
        "## FDR-significant CPA differences",
    ]

    if cpa_sig.empty:
        lines.append("- None.")
    else:
        for _, row in cpa_sig.sort_values("p_value_fdr").head(10).iterrows():
            lines.append(
                f"- {row['group_a']} vs {row['group_b']}: "
                f"adjusted p={row['p_value_fdr']:.4g}, "
                f"Cohen's d={row['cohen_d']:.2f} ({row['effect_size']})."
            )

    lines += ["", "## FDR-significant conversion-rate differences"]
    if fisher_sig.empty:
        lines.append("- None.")
    else:
        for _, row in fisher_sig.sort_values("p_value_fdr").head(10).iterrows():
            lines.append(
                f"- {row['group_a']} vs {row['group_b']}: "
                f"adjusted p={row['p_value_fdr']:.4g}, "
                f"odds ratio={row['odds_ratio']:.2f}."
            )

    (ROOT / "statistical_findings.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print("\nCPA t-test results:")
    print(
        cpa_results[
            ["group_a", "group_b", "p_value", "cohen_d", "effect_size", "significant_fdr"]
        ].round(4).to_string(index=False)
    )
    print("\nCorrection summary:")
    print(correction_summary.to_string(index=False))
    print("\nRecommended $500K allocation:")
    print(
        rank_df[
            ["channel", "recommended_budget", "budget_pct", "composite_score"]
        ].round(3).to_string(index=False)
    )

    print("\nSaved statistical analysis outputs.")


if __name__ == "__main__":
    main()
