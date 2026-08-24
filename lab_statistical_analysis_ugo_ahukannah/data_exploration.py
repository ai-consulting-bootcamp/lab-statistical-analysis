"""Part 1 - load, clean and explore the marketing dataset.

Steps 2 and 3 of the lab: understand the shape of the data, identify the groups
to compare, compute the headline marketing metrics, and look at the
distributions before running a single test on them.

Run:  python data_exploration.py

Outputs: figures/exploration_overview.png, figures/cost_distributions.png,
         group_performance_summary.csv

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from marketing_data import (FIGURES, HERE, N_GROUPS, analysis_frame, group_summary,
                            load_criteo, load_synthetic, wilson_ci)

pd.set_option("display.width", 160)


def explore(df: pd.DataFrame) -> None:
    print("=" * 78)
    print("DATASET: criteo/criteo-attribution-dataset (real ad-serving logs)")
    print("=" * 78)
    print(f"rows                {len(df):,}")
    print(f"columns             {list(df.columns)}")
    print(f"rows dropped        {df.attrs.get('rows_dropped', 0)}")
    print(f"campaigns           {df['campaign'].nunique():,}")
    print(f"missing values      {int(df.isna().sum().sum())}")
    print(f"impressions         {len(df):,}")
    print(f"clicks              {int(df['click'].sum()):,}  (CTR {df['click'].mean():.2%})")
    print(f"conversions         {int(df['conversion'].sum()):,}  (CVR {df['conversion'].mean():.2%})")
    print(f"total cost          {df['cost'].sum():.4f} Criteo cost units")

    print("\nWhy the cost column has no currency: Criteo anonymises it by a uniform"
          "\nscaling factor. Ratios between campaigns are meaningful; the absolute"
          "\nnumbers are not money and are never presented as money.")

    concentration = df["campaign"].value_counts()
    share = concentration.head(N_GROUPS).sum() / len(df)
    print(f"\ncampaign concentration: the largest {N_GROUPS} carry {share:.1%} of impressions")
    print(f"campaigns with >=1,000 impressions: {(concentration >= 1000).sum()}")


def summarise(sub: pd.DataFrame) -> pd.DataFrame:
    g = group_summary(sub)
    lo_hi = [wilson_ci(int(r.conversions), int(r.impressions)) for r in g.itertuples()]
    g["cvr_ci_low_pct"] = [lo * 100 for lo, _ in lo_hi]
    g["cvr_ci_high_pct"] = [hi * 100 for _, hi in lo_hi]

    print("\n" + "=" * 78)
    print("GROUP PERFORMANCE SUMMARY (the six largest campaigns)")
    print("=" * 78)
    show = g[["impressions", "clicks", "conversions", "ctr_pct", "cvr_pct",
              "cvr_ci_low_pct", "cvr_ci_high_pct", "total_cost", "cpa"]]
    print(show.round(4).to_string())

    spread = g["cpa"].max() / g["cpa"].min()
    print(f"\nCPA spread across campaigns: {spread:.1f}x "
          f"({g['cpa'].idxmin()} cheapest, {g['cpa'].idxmax()} dearest)")
    print(f"CVR spread: {g['cvr_pct'].min():.2f}% to {g['cvr_pct'].max():.2f}%")
    print("\nThose gaps are what the rest of the analysis has to justify or dismiss.")
    return g


def roas_from_synthetic() -> pd.DataFrame:
    """ROAS by platform, from the SECONDARY SYNTHETIC dataset.

    The Criteo release has no revenue column, and no public dataset of real ad
    spend carries revenue either - it is commercially sensitive. Rather than
    silently skip ROAS or invent a revenue column on the real data, this uses a
    clearly-labelled synthetic set for that one metric.
    """
    s = load_synthetic()
    r = s.groupby("platform").agg(spend=("spend", "sum"), revenue=("revenue", "sum"),
                                  conversions=("conversions", "sum"),
                                  clicks=("clicks", "sum"), impressions=("impressions", "sum"))
    r["roas"] = r["revenue"] / r["spend"]
    r["cpa"] = np.where(r["conversions"] > 0, r["spend"] / r["conversions"], np.nan)
    r["cvr_pct"] = r["conversions"] / r["clicks"] * 100
    print("\n" + "=" * 78)
    print("ROAS BY PLATFORM - SECONDARY DATASET, SYNTHETIC (see dataset_documentation.md)")
    print("=" * 78)
    print(r.sort_values("roas", ascending=False).round(3).to_string())
    print("\nThese figures are illustrative only. They come from a simulated set and"
          "\nare never mixed with the Criteo results or used for a recommendation.")
    return r


def draw(sub: pd.DataFrame, g: pd.DataFrame, roas: pd.DataFrame) -> None:
    fig, ax = plt.subplots(2, 2, figsize=(14, 9))

    g_sorted = g.sort_values("cvr_pct", ascending=False)
    err = np.vstack([g_sorted["cvr_pct"] - g_sorted["cvr_ci_low_pct"],
                     g_sorted["cvr_ci_high_pct"] - g_sorted["cvr_pct"]])
    ax[0, 0].bar(g_sorted.index, g_sorted["cvr_pct"], yerr=err, capsize=4, color="#2e7d32")
    ax[0, 0].set_title("Conversion rate by campaign (95% Wilson interval)", fontweight="bold")
    ax[0, 0].set_ylabel("conversion rate (%)")
    ax[0, 0].tick_params(axis="x", rotation=30)

    g_cpa = g.sort_values("cpa")
    ax[0, 1].bar(g_cpa.index, g_cpa["cpa"], color="#1565c0")
    ax[0, 1].set_title("Cost per acquisition (Criteo cost units)", fontweight="bold")
    ax[0, 1].set_ylabel("cost per conversion")
    ax[0, 1].tick_params(axis="x", rotation=30)

    ax[1, 0].scatter(g["impressions"], g["cvr_pct"], s=90, color="#6a1b9a")
    for name, r in g.iterrows():
        ax[1, 0].annotate(name.replace("Campaign ", ""), (r["impressions"], r["cvr_pct"]),
                          xytext=(6, 3), textcoords="offset points", fontsize=9)
    ax[1, 0].set_title("Volume against conversion rate", fontweight="bold")
    ax[1, 0].set_xlabel("impressions"); ax[1, 0].set_ylabel("conversion rate (%)")

    rs = roas.sort_values("roas", ascending=False)
    ax[1, 1].bar(rs.index, rs["roas"], color="#ef6c00")
    ax[1, 1].set_title("ROAS by platform - SYNTHETIC dataset, illustrative", fontweight="bold")
    ax[1, 1].set_ylabel("revenue / spend")
    ax[1, 1].tick_params(axis="x", rotation=30)

    for a in ax.ravel():
        a.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGURES / "exploration_overview.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Cost distributions - the variable the t-tests operate on.
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))
    groups = list(g.index)
    data = [sub.loc[sub["group"] == n, "cost"].values for n in groups]
    axes[0].boxplot(data, tick_labels=[n.replace("Campaign ", "") for n in groups], showfliers=False)
    axes[0].set_title("Cost per impression by campaign (outliers hidden)", fontweight="bold")
    axes[0].set_ylabel("cost per impression")

    axes[1].hist(sub["cost"], bins=60, color="#455a64")
    axes[1].set_yscale("log")
    axes[1].set_title("Cost per impression, all six campaigns (log count)", fontweight="bold")
    axes[1].set_xlabel("cost per impression")
    for a in axes:
        a.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGURES / "cost_distributions.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nfigures written to {FIGURES.name}/")


def main() -> int:
    df = load_criteo()
    explore(df)
    sub = analysis_frame(df)
    g = summarise(sub)
    roas = roas_from_synthetic()
    draw(sub, g, roas)

    out = HERE / "group_performance_summary.csv"
    g.to_csv(out)
    print(f"written: {out.name}")

    print("\nNote on distribution shape: cost per impression is heavily right-skewed,"
          "\nso Welch's t-test is used rather than Student's, and the effect size is"
          "\nreported alongside every p-value. See statistical_analysis.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
