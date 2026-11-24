"""Parts 2-3 · Pairwise comparisons and multiple-comparisons correction (Steps 4-6).

Input:  daily_channel_metrics.csv (from data_exploration.py)
Output: results/ttest_cpa.csv, results/fisher_conversion.csv, results/correction_summary.csv,
        figures/metric_comparison_heatmap.png, figures/rate_comparison.png, figures/correction_comparison.png
"""
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import false_discovery_control, fisher_exact

HERE = Path(__file__).resolve().parent
(HERE / "results").mkdir(exist_ok=True)
(HERE / "figures").mkdir(exist_ok=True)
ALPHA = 0.05


def effect_label(d):
    d = abs(d)
    return "negligible" if d < 0.2 else "small" if d < 0.5 else "medium" if d < 0.8 else "large"


def ttests(daily, metric):
    """Step 4: independent t-test + Cohen's d for every pair of channels on a daily metric."""
    data = daily[["Channel", metric]].replace([np.inf, -np.inf], np.nan).dropna()
    rows = []
    for a, b in combinations(sorted(data["Channel"].unique()), 2):
        xa, xb = data.loc[data.Channel == a, metric], data.loc[data.Channel == b, metric]
        t, p = stats.ttest_ind(xa, xb)
        diff = xb.mean() - xa.mean()
        pooled = np.sqrt((xa.var() + xb.var()) / 2)
        d = diff / pooled if pooled else np.nan
        rows.append({"group_a": a, "group_b": b, "mean_a": xa.mean(), "mean_b": xb.mean(), "diff_b_minus_a": diff,
                     "pct_diff": diff / xa.mean() * 100, "t_stat": t, "p_value": p, "cohens_d": d,
                     "effect_size": effect_label(d), "significant": p < ALPHA, "n_a": len(xa), "n_b": len(xb)})
        print(f"{metric}: {a} vs {b}: mean {xa.mean():.2f} vs {xb.mean():.2f} ({diff / xa.mean() * 100:+.2f}%), "
              f"p={p:.4g}, d={d:.3f} ({effect_label(d)})")
    res = pd.DataFrame(rows)
    print(f"-> {len(res)} comparisons, {res.significant.sum()} significant at alpha={ALPHA}\n")
    return res


def fisher_tests(daily):
    """Step 5: Fisher's exact test on conversions vs non-conversions (clicks that did not convert)."""
    agg = daily.groupby("Channel")[["Conversions", "Clicks"]].sum()
    agg["Non_Conversions"] = agg["Clicks"] - agg["Conversions"]
    agg["Rate"] = agg["Conversions"] / agg["Clicks"]
    print(agg.to_string(), "\n")
    rows = []
    for a, b in combinations(sorted(agg.index), 2):
        table = [[agg.at[a, "Conversions"], agg.at[a, "Non_Conversions"]],
                 [agg.at[b, "Conversions"], agg.at[b, "Non_Conversions"]]]
        odds, p = fisher_exact(table, alternative="two-sided")
        ra, rb = agg.at[a, "Rate"], agg.at[b, "Rate"]
        rows.append({"group_a": a, "group_b": b, "conv_a": agg.at[a, "Conversions"], "clicks_a": agg.at[a, "Clicks"],
                     "conv_b": agg.at[b, "Conversions"], "clicks_b": agg.at[b, "Clicks"], "rate_a": ra, "rate_b": rb,
                     "diff": rb - ra, "pct_diff": (rb - ra) / ra * 100, "odds_ratio": odds, "p_value": p,
                     "significant": p < ALPHA})
        print(f"Conversion: {a} {ra:.4%} vs {b} {rb:.4%} ({(rb - ra) / ra * 100:+.2f}%), OR={odds:.4f}, p={p:.4g}")
    res = pd.DataFrame(rows)
    print(f"-> {len(res)} comparisons, {res.significant.sum()} significant at alpha={ALPHA}\n")
    return res, agg


def correct(res, label):
    """Step 6: Bonferroni and Benjamini-Hochberg (FDR)."""
    m = len(res)
    res["alpha_bonferroni"] = ALPHA / m
    res["significant_bonferroni"] = res["p_value"] < ALPHA / m
    res["p_value_fdr"] = false_discovery_control(res["p_value"].values, method="bh")
    res["significant_fdr"] = res["p_value_fdr"] < ALPHA
    print(f"{label}: uncorrected {res.significant.sum()} | Bonferroni (alpha={ALPHA / m:.5f}) "
          f"{res.significant_bonferroni.sum()} | FDR {res.significant_fdr.sum()} (of {m})")
    for _, r in res[res.significant_fdr].iterrows():
        print(f"   still significant after FDR: {r.group_a} vs {r.group_b} (adj. p={r.p_value_fdr:.4g})")
    return res


def main():
    daily = pd.read_csv(HERE / "daily_channel_metrics.csv", parse_dates=["Date"])
    cpa = ttests(daily, "CPA")
    roas = ttests(daily, "ROAS")
    conv, agg = fisher_tests(daily)

    total = len(cpa) + len(conv)
    print(f"Total comparisons (CPA + conversion rate): {total}. "
          f"Expected false positives by chance at alpha=0.05: {total * ALPHA:.2f}\n")
    cpa = correct(cpa, "CPA t-tests")
    roas = correct(roas, "ROAS t-tests")
    conv = correct(conv, "Conversion-rate Fisher tests")
    cpa.to_csv(HERE / "results/ttest_cpa.csv", index=False)
    roas.to_csv(HERE / "results/ttest_roas.csv", index=False)
    conv.to_csv(HERE / "results/fisher_conversion.csv", index=False)

    summary = pd.DataFrame({
        "Uncorrected (alpha=0.05)": [cpa.significant.sum(), conv.significant.sum()],
        "Bonferroni": [cpa.significant_bonferroni.sum(), conv.significant_bonferroni.sum()],
        "FDR (Benjamini-Hochberg)": [cpa.significant_fdr.sum(), conv.significant_fdr.sum()],
    }, index=["CPA (t-test)", "Conversion rate (Fisher)"])
    summary["Comparisons"] = [len(cpa), len(conv)]
    summary.to_csv(HERE / "results/correction_summary.csv")
    print("\n", summary.to_string())

    # Heatmap of CPA p-values
    chans = sorted(daily["Channel"].unique())
    mat = pd.DataFrame(1.0, index=chans, columns=chans)
    for _, r in cpa.iterrows():
        mat.loc[r.group_a, r.group_b] = mat.loc[r.group_b, r.group_a] = r.p_value
    fig, ax = plt.subplots(figsize=(8, 6.5))
    im = ax.imshow(mat.values, cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(chans)), chans, rotation=30, ha="right")
    ax.set_yticks(range(len(chans)), chans)
    for i in range(len(chans)):
        for j in range(len(chans)):
            ax.text(j, i, f"{mat.values[i, j]:.3f}", ha="center", va="center", fontsize=9)
    fig.colorbar(im, label="p-value (red = small = significant)")
    ax.set_title("Daily CPA: pairwise t-test p-values (uncorrected)")
    fig.tight_layout()
    fig.savefig(HERE / "figures/metric_comparison_heatmap.png", dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    s = agg["Rate"].sort_values()
    ax.barh(s.index, s.values * 100, color="#2C5F2D")
    for i, v in enumerate(s.values * 100):
        ax.text(v, i, f" {v:.3f}%", va="center")
    ax.set_xlabel("Conversion rate (%)")
    ax.set_title("Conversion rate by channel (all campaigns)")
    ax.set_xlim(0, s.max() * 100 * 1.15)
    fig.tight_layout()
    fig.savefig(HERE / "figures/rate_comparison.png", dpi=120)
    plt.close(fig)

    ax = summary.drop(columns="Comparisons").plot.bar(figsize=(9, 5), color=["#B5462F", "#D99A1E", "#2C5F2D"], rot=0)
    ax.set_ylabel("Number of significant comparisons")
    ax.set_title("Effect of multiple-comparisons correction")
    plt.tight_layout()
    plt.savefig(HERE / "figures/correction_comparison.png", dpi=120)
    plt.close()
    print("\nSaved results/*.csv and figures/.")


if __name__ == "__main__":
    main()
