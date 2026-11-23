from itertools import combinations

from data_exploration import DATA, TABLES, FIGURES, save_plot, ratio

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.special import logsumexp
from scipy.stats import fisher_exact, false_discovery_control, hypergeom, ttest_ind, ttest_rel

ALPHA = 0.05
RATE_THRESHOLD_PP = 0.5
CPA_THRESHOLD_PCT = 10


def effect_label(d):
    return np.select(np.abs(d) < np.array([0.2, 0.5, 0.8]),
                     ["negligible", "small", "medium"], default="large").item()


def relative_difference(a, b):
    return (b - a) * 100 / a if a else np.nan


def adjust(results, p_column="p_value", label=""):
    results = results.copy()
    p_values = results[p_column].to_numpy()
    results[f"{label}significant_raw"] = p_values < ALPHA
    results[f"{label}alpha_bonferroni"] = ALPHA / len(p_values)
    results[f"{label}p_value_bonferroni"] = np.minimum(1, p_values * len(p_values))
    results[f"{label}significant_bonferroni"] = p_values < ALPHA / len(p_values)
    results[f"{label}p_value_fdr"] = false_discovery_control(p_values, method="bh")
    results[f"{label}significant_fdr"] = results[f"{label}p_value_fdr"] < ALPHA
    return results


def compare_daily(daily, metric):
    wide = daily.pivot(index="day", columns="campaign", values=metric).replace([np.inf, -np.inf], np.nan)
    results = []
    for campaign_a, campaign_b in combinations(wide.columns, 2):
        a = wide[campaign_a].dropna()
        b = wide[campaign_b].dropna()
        mean_a, mean_b = a.mean(), b.mean()
        pooled_sd = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
        d = (mean_b - mean_a) / pooled_sd
        welch = ttest_ind(b, a, equal_var=False)
        ci = welch.confidence_interval()
        paired = wide[[campaign_a, campaign_b]].dropna()
        matched = ttest_rel(paired[campaign_b], paired[campaign_a])
        row = {
            "campaign_a": campaign_a, "campaign_b": campaign_b, "n_a": len(a), "n_b": len(b),
            "mean_a": mean_a, "mean_b": mean_b, "difference_b_minus_a": mean_b - mean_a,
            "difference_pct_of_a": relative_difference(mean_a, mean_b),
            "difference_ci_lower": ci.low, "difference_ci_upper": ci.high,
            "t_statistic": welch.statistic, "p_value": welch.pvalue, "cohens_d": d,
            "effect_size": effect_label(d), "paired_days": len(paired),
            "paired_t_statistic": matched.statistic, "paired_p_value": matched.pvalue,
        }
        results.append(row)
    return adjust(adjust(pd.DataFrame(results)), p_column="paired_p_value", label="paired_")


def fisher_log10_p(table, probability):
    if probability > 0:
        return np.log10(probability)
    table = np.asarray(table)
    population = table.sum()
    successes = table[:, 0].sum()
    draws = table[0].sum()
    distribution = hypergeom(population, successes, draws)
    lo, hi = distribution.support()
    log_mass = distribution.logpmf(np.arange(lo, hi + 1))
    observed = log_mass[table[0, 0] - lo]
    # Summing in log space preserves the two-sided tail below float precision.
    return logsumexp(log_mass[log_mass <= observed + 1e-12]) / np.log(10)


def compare_binary(totals):
    results = []
    for campaign_a, campaign_b in combinations(totals.index, 2):
        a, b = totals.loc[campaign_a], totals.loc[campaign_b]
        table = [[int(a.conversions), int(a.non_conversions)],
                 [int(b.conversions), int(b.non_conversions)]]
        test = fisher_exact(table, alternative="two-sided")
        rate_a, rate_b = a.conversion_rate, b.conversion_rate
        pooled_sd = np.sqrt((rate_a * (1 - rate_a) + rate_b * (1 - rate_b)) / 2)
        d = (rate_b - rate_a) / pooled_sd
        results.append({
            "campaign_a": campaign_a, "campaign_b": campaign_b,
            "conversions_a": int(a.conversions), "conversions_b": int(b.conversions),
            "clicks_a": int(a.clicks), "clicks_b": int(b.clicks),
            "non_conversions_a": int(a.non_conversions), "non_conversions_b": int(b.non_conversions),
            "rate_a": rate_a, "rate_b": rate_b, "difference_pp_b_minus_a": (rate_b - rate_a) * 100,
            "difference_pct_of_a": relative_difference(rate_a, rate_b),
            "odds_ratio_a_over_b": test.statistic, "p_value": test.pvalue,
            "p_value_underflow": test.pvalue == 0,
            "log10_raw_p_value": fisher_log10_p(table, test.pvalue),
            "cohens_d_binary": d, "effect_size": effect_label(d),
        })
    return adjust(pd.DataFrame(results))


def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    rng = np.random.default_rng(417)
    means = rng.choice(data, size=(n_bootstrap, len(data)), replace=True).mean(axis=1)
    tail = (1 - ci_level) / 2
    return np.quantile(means, [tail, 1 - tail])


def cpa_intervals(daily):
    rng = np.random.default_rng(374)
    results = []
    for campaign, data in daily.sort_values("day").groupby("campaign"):
        values = data["cpa"].dropna().to_numpy()
        low, high = bootstrap_ci(values, n_bootstrap=5000)
        # The moving block resample keeps spend, conversions and adjacent days together.
        n_days, block_length = len(data), 7
        n_blocks = (n_days + block_length - 1) // block_length
        starts = rng.integers(0, n_days - block_length + 1, size=(5000, n_blocks, 1))
        indices = (starts + np.arange(block_length)).reshape(5000, -1)[:, :n_days]
        resampled_cost = data["cost"].to_numpy()[indices].sum(axis=1)
        resampled_conversions = data["conversions"].to_numpy()[indices].sum(axis=1)
        low_weighted, high_weighted = np.quantile(
            resampled_cost[resampled_conversions > 0] / resampled_conversions[resampled_conversions > 0],
            [0.025, 0.975],
        )
        results.append({
            "campaign": campaign, "valid_cpa_days": len(values), "zero_conversion_days": n_days - len(values),
            "mean_daily_cpa": values.mean(), "mean_ci_lower": low, "mean_ci_upper": high,
            "aggregate_cpa": data["cost"].sum() / data["conversions"].sum(),
            "aggregate_block_ci_lower": low_weighted, "aggregate_block_ci_upper": high_weighted,
        })
    return pd.DataFrame(results)


def plot_comparisons(cpa, totals, correction):
    campaigns = totals.index
    matrix = pd.DataFrame(np.eye(len(campaigns)), index=campaigns, columns=campaigns)
    for row in cpa.itertuples():
        matrix.loc[row.campaign_a, row.campaign_b] = row.p_value
        matrix.loc[row.campaign_b, row.campaign_a] = row.p_value
    annotations = matrix.map(lambda p: f"{p:.2g}" if p >= 0.001 else f"{p:.1e}").mask(np.eye(len(matrix), dtype=bool), "—")
    fig, ax = plt.subplots(figsize=(9, 7), layout="constrained")
    cmap = ListedColormap(["#bd644e", "#f3ddd3", "#e6ecee"])
    norm = BoundaryNorm([0, ALPHA / len(cpa), ALPHA, 1.0001], cmap.N)
    sns.heatmap(matrix, annot=annotations, fmt="", square=True, linewidths=0.6,
                cmap=cmap, norm=norm, cbar=False, ax=ax)
    ax.set(title="Step 4 — Primary CPA comparison: two-sided Welch tests",
           xlabel=f"Raw p-values; colors use CPA-family thresholds (Bonferroni α={ALPHA / len(cpa):.4f}, α=0.05)",
           ylabel="Campaign")
    fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                 ticks=[ALPHA / len(cpa), ALPHA, 1], label="Raw p-value (CPA family)")
    save_plot(fig, "metric_comparison_heatmap.png")

    ordered = totals.sort_values("conversion_rate")
    fig, ax = plt.subplots(figsize=(9, 5.4), layout="constrained")
    bars = ax.barh(ordered.index.astype(str), ordered["conversion_rate"] * 100, color="#287271")
    ax.bar_label(bars, labels=[f"{rate:.2%}" for rate in ordered["conversion_rate"]], padding=5)
    ax.set(xlim=(0, ordered["conversion_rate"].max() * 123), xlabel="Credited conversions per 100 clicks",
           ylabel="Campaign", title="Attributed post-click conversion by campaign")
    ax.grid(axis="y", visible=False)
    save_plot(fig, "rate_comparison.png")

    fig, ax = plt.subplots(figsize=(11, 5.6), layout="constrained")
    correction.set_index("family")[["raw", "bonferroni", "benjamini_hochberg"]].rename(columns={
        "raw": "Unadjusted", "bonferroni": "Bonferroni", "benjamini_hochberg": "Benjamini–Hochberg",
    }).plot.bar(ax=ax, rot=0, color=["#bac9cf", "#287271", "#bd7950"])
    for bars in ax.containers:
        ax.bar_label(bars, padding=3)
    ax.set(xlabel="", ylabel="Pairs below threshold",
           ylim=(0, len(cpa) + 3))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncols=3)
    fig.suptitle("Effect of multiple-testing corrections", fontsize=15, fontweight="bold")
    save_plot(fig, "correction_comparison.png")


def significant_findings(cpa, fisher):
    rows = []
    for row in cpa.loc[cpa["significant_fdr"]].itertuples():
        lower_is_a = row.mean_a < row.mean_b
        lower, higher = sorted([row.mean_a, row.mean_b])
        relative_drop = (higher - lower) / higher * 100
        rows.append({
            "metric": "Mean daily CPA", "better_campaign": row.campaign_a if lower_is_a else row.campaign_b,
            "other_campaign": row.campaign_b if lower_is_a else row.campaign_a,
            "absolute_advantage": higher - lower, "unit": "transformed cost units",
            "relative_advantage_pct": relative_drop, "p_value_fdr": row.p_value_fdr,
            "absolute_cohens_d": abs(row.cohens_d), "meets_practical_threshold": relative_drop >= CPA_THRESHOLD_PCT,
            "sensitivity_bh": row.paired_significant_fdr,
        })
    for row in fisher.loc[fisher["significant_fdr"]].itertuples():
        higher_is_b = row.rate_b > row.rate_a
        rows.append({
            "metric": "Attributed post-click conversion rate",
            "better_campaign": row.campaign_b if higher_is_b else row.campaign_a,
            "other_campaign": row.campaign_a if higher_is_b else row.campaign_b,
            "absolute_advantage": abs(row.difference_pp_b_minus_a), "unit": "percentage points",
            "relative_advantage_pct": abs(row.rate_b - row.rate_a) / min(row.rate_a, row.rate_b) * 100,
            "p_value_fdr": row.p_value_fdr, "absolute_cohens_d": abs(row.cohens_d_binary),
            "meets_practical_threshold": abs(row.difference_pp_b_minus_a) >= RATE_THRESHOLD_PP,
            "sensitivity_bh": np.nan,
        })
    return pd.DataFrame(rows)


def pilot_budget(totals):
    budget = 500_000
    reserve = 450_000
    pilot = budget - reserve
    ranking = totals[["cpa", "conversion_rate", "conversions"]].copy()
    ranking["cpa_rank"] = ranking["cpa"].rank(ascending=False)
    ranking["conversion_rate_rank"] = ranking["conversion_rate"].rank()
    ranking["volume_rank"] = ranking["conversions"].rank()
    ranking["composite_score"] = 0.60 * ranking["cpa_rank"] + 0.25 * ranking["conversion_rate_rank"] + 0.15 * ranking["volume_rank"]
    ranking = ranking.sort_values("composite_score", ascending=False)
    # A 5% floor protects test coverage. The remaining 65% follows the composite ranks.
    pilot_shares = 0.05 + (1 - 0.05 * len(ranking)) * ranking["composite_score"] / ranking["composite_score"].sum()
    assert pilot_shares.between(0.05, 0.25).all()
    unrounded = pilot * pilot_shares
    rounded = np.floor(unrounded).astype(int)
    remainder = pilot - rounded.sum()
    rounded.loc[(unrounded - rounded).nlargest(remainder).index] += 1
    ranking["allocation_usd"] = rounded
    ranking["pilot_pct"] = 100 * rounded / pilot
    ranking["total_budget_pct"] = 100 * rounded / budget
    allocation = ranking.reset_index().assign(campaign=lambda x: x["campaign"].astype(str))
    return pd.concat([allocation, pd.DataFrame([{
        "campaign": "Existing allocation / reserve", "allocation_usd": reserve, "total_budget_pct": 100 * reserve / budget,
    }])], ignore_index=True)


def main():
    for directory in [TABLES, FIGURES]:
        directory.mkdir(exist_ok=True)
    daily = pd.read_csv(DATA / "marketing_data.csv")
    totals = daily.groupby("campaign")[["conversions", "clicks", "cost"]].sum()
    totals["non_conversions"] = totals["clicks"] - totals["conversions"]
    totals["conversion_rate"] = ratio(totals["conversions"], totals["clicks"])
    totals["cpa"] = ratio(totals["cost"], totals["conversions"])
    totals.to_csv(TABLES / "binary_outcome_counts.csv")
    cpa = compare_daily(daily, "cpa")
    rate = compare_daily(daily, "conversion_rate")
    fisher = compare_binary(totals)
    families = {"Daily CPA (Welch)": cpa, "Daily CVR (Welch)": rate, "Pooled CVR (Fisher)": fisher}
    correction = pd.DataFrame([{
        "family": label, "tests": len(frame),
        "expected_raw_false_positives_if_all_null": len(frame) * ALPHA,
        "raw": frame["significant_raw"].sum(), "bonferroni": frame["significant_bonferroni"].sum(),
        "benjamini_hochberg": frame["significant_fdr"].sum(),
    } for label, frame in families.items()])
    findings = significant_findings(cpa, fisher)
    intervals = cpa_intervals(daily)
    allocation = pilot_budget(totals)
    assert allocation["allocation_usd"].sum() == 500_000
    for name, frame in [
        ("cpa_pairwise", cpa), ("daily_conversion_rate_pairwise", rate),
        ("fisher_conversion_rate_pairwise", fisher), ("correction_summary", correction),
        ("significant_findings", findings), ("cpa_confidence_intervals", intervals),
        ("budget_allocation", allocation),
    ]:
        frame.to_csv(TABLES / f"{name}.csv", index=False)
    agreement = rate[["campaign_a", "campaign_b", "significant_fdr", "paired_significant_fdr"]].rename(
        columns={"significant_fdr": "daily_welch_bh", "paired_significant_fdr": "daily_paired_bh"}
    )
    agreement["fisher_bh"] = fisher["significant_fdr"]
    agreement.to_csv(TABLES / "conversion_test_agreement.csv", index=False)
    print(totals.round(5).to_string())
    primary_cpa_columns = [
        "campaign_a", "campaign_b", "n_a", "n_b", "mean_a", "mean_b",
        "difference_b_minus_a", "difference_pct_of_a", "t_statistic", "p_value",
        "cohens_d", "significant_raw", "significant_bonferroni", "p_value_fdr", "significant_fdr",
    ]
    paired_cpa_columns = [
        "campaign_a", "campaign_b", "paired_days", "paired_t_statistic", "paired_p_value",
        "paired_significant_raw", "paired_significant_bonferroni", "paired_p_value_fdr", "paired_significant_fdr",
    ]
    print("\nStep 4 - Primary CPA comparison")
    print("Two-sided Welch t-tests; one observation is one campaign-day CPA ratio (daily transformed display cost / credited conversions). "
          "Each valid day has equal weight in the comparison of means.")
    print(cpa[primary_cpa_columns].to_string(index=False))
    print("\nStep 4 sensitivity check - same-day paired CPA t-tests (not the primary deliverable)")
    print(cpa[paired_cpa_columns].to_string(index=False))
    print("\nDaily conversion-rate comparisons - two-sided Welch tests (separate from Step 4 CPA)")
    print(rate.to_string(index=False))
    print("\nPooled conversion-rate comparisons - two-sided Fisher exact tests (separate from Step 4 CPA)")
    print(fisher.to_string(index=False))
    expected = correction["expected_raw_false_positives_if_all_null"].sum()
    print(f"\nThe all-null benchmark gives {expected:.2f} expected nominal false positives across "
          "the three primary families. The realized false discovery count is unknown.")
    print(correction.to_string(index=False))
    print("\nBH-significant findings\n" + findings.to_string(index=False))
    print("\nConfidence intervals\n" + intervals.round(3).to_string(index=False))
    print("\nMonthly budget scenario\n" + allocation.round(3).to_string(index=False))
    sns.set_theme(style="whitegrid", context="notebook")
    plot_comparisons(cpa, totals, correction)


if __name__ == "__main__":
    main()
