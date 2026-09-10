"""
Part 1: Dataset Discovery & Exploration
Lab: In God we trust, everyone else bring the data

Dataset: Digital Marketing Performance Dataset (Synthetic, Benchmark-Based)
Source: Kaggle (alinaboulsi/digital-marketing-performance-dataset), mirrored on
        Hugging Face at jason1966/alinaboulsi_digital-marketing-performance-dataset
URL:    https://www.kaggle.com/datasets/alinaboulsi/digital-marketing-performance-dataset
Why:    30,000 rows of daily ad performance across 6 real-world advertising
        channels (Meta, Google Search, Google Display, TikTok, LinkedIn,
        Snapchat) spanning 2023-2025, with spend/impressions/clicks/
        conversions/revenue already present -- everything needed to build
        CPA, ROAS, conversion rate, and CTR per channel, plus enough daily
        observations per channel to run t-tests, Fisher's exact tests, and
        power analysis with real sample sizes.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid")

RAW_PATH = "data/raw/digital_marketing_dataset_30k.csv"
CLEAN_PATH = "data/marketing_data.csv"
GROUP_COL = "channel"

# ---------------------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------------------
df = pd.read_csv(RAW_PATH)
print("Raw shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nDtypes:\n", df.dtypes)
print("\nHead:\n", df.head())

# ---------------------------------------------------------------------------
# 2. Explore structure
# ---------------------------------------------------------------------------
print("\nMissing values per column:\n", df.isna().sum()[df.isna().sum() > 0])
print("\nUnique platforms (our grouping variable / 'channel'):")
print(df["platform"].value_counts())

# ---------------------------------------------------------------------------
# 3. Clean & prepare
# ---------------------------------------------------------------------------
# Parse date (DD/MM/YYYY in source file)
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

# Rename the grouping variable to the vocabulary the lab uses ("channel")
df = df.rename(columns={"platform": GROUP_COL})

# Drop redundant human-readable duplicate flag columns (numeric flags kept)
df = df.drop(columns=["is_holiday (text)", "is_weekend (text)"])

# Sanity checks: no negative values, reach <= impressions, clicks <= impressions
numeric_cols = ["spend", "impressions", "reach", "clicks", "conversions", "revenue", "video_views"]
assert (df[numeric_cols] >= 0).all().all(), "Found negative values"
bad_reach = (df["reach"] > df["impressions"]).sum()
bad_clicks = (df["clicks"] > df["impressions"]).sum()
print(f"\nRows where reach > impressions: {bad_reach}")
print(f"Rows where clicks > impressions: {bad_clicks}")

# Aggregate the ad-level rows up to one row per (date, channel): this is the
# level at which we compare channels as groups, giving each channel ~3 years
# of daily observations (hundreds of data points per channel).
daily = (
    df.groupby(["date", GROUP_COL], as_index=False)
    .agg(
        spend=("spend", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        revenue=("revenue", "sum"),
    )
    .sort_values(["date", GROUP_COL])
    .reset_index(drop=True)
)

# Derived per-day metrics, with divide-by-zero -> NaN
daily["ctr"] = daily["clicks"] / daily["impressions"]
daily["conversion_rate"] = daily["conversions"] / daily["clicks"]
daily["cpa"] = daily["spend"] / daily["conversions"]
daily["roas"] = daily["revenue"] / daily["spend"]
daily["profit"] = daily["revenue"] - daily["spend"]
daily["profit_margin"] = daily["profit"] / daily["revenue"]

daily = daily.replace([np.inf, -np.inf], np.nan)

print("\nPrepared daily-by-channel panel shape:", daily.shape)
print(daily.groupby(GROUP_COL).size().rename("n_days"))

daily.to_csv(CLEAN_PATH, index=False)
print(f"\nSaved cleaned dataset -> {CLEAN_PATH}")

# ---------------------------------------------------------------------------
# Step 3: Channel-level summary metrics
# ---------------------------------------------------------------------------
agg = (
    df.groupby(GROUP_COL, as_index=False)
    .agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    )
)
agg["ctr"] = agg["clicks"] / agg["impressions"]
agg["conversion_rate"] = agg["conversions"] / agg["clicks"]
agg["cpa"] = agg["spend"] / agg["conversions"]
agg["roas"] = agg["revenue"] / agg["spend"]
agg["profit"] = agg["revenue"] - agg["spend"]
agg["profit_margin"] = agg["profit"] / agg["revenue"]
agg = agg.replace([np.inf, -np.inf], np.nan).round(4)
agg = agg.sort_values("cpa")

# Round dollar/count columns to 2 decimals, but keep rate columns (ctr,
# conversion_rate, roas, profit_margin) at 4 decimals -- 2 decimals of a
# fraction like 0.0082 rounds every channel's conversion rate down to the
# same 0.01, hiding exactly the differences this analysis is about.
rate_cols = ["ctr", "conversion_rate", "roas", "profit_margin"]
dollar_cols = ["impressions", "clicks", "conversions", "spend", "revenue", "cpa", "profit"]
agg_display = agg.round({**{c: 4 for c in rate_cols}, **{c: 2 for c in dollar_cols}})

print("\n=== Channel Summary Table (full 2023-2025 period) ===")
print(agg_display.to_string(index=False))
agg_display.to_csv("data/channel_summary.csv", index=False)

# ---------------------------------------------------------------------------
# Visualization: group_metrics_overview.png
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(3, 2, figsize=(13, 14))
axes = axes.ravel()

plot_agg = agg.sort_values("cpa")
axes[0].barh(plot_agg[GROUP_COL], plot_agg["cpa"], color="steelblue")
axes[0].set_title("CPA by Channel (lower is better)")
axes[0].set_xlabel("Cost per Acquisition ($)")

plot_agg2 = agg.sort_values("roas")
axes[1].barh(plot_agg2[GROUP_COL], plot_agg2["roas"], color="seagreen")
axes[1].set_title("ROAS by Channel (higher is better)")
axes[1].set_xlabel("Return on Ad Spend")

plot_agg3 = agg.sort_values("conversion_rate")
axes[2].barh(plot_agg3[GROUP_COL], plot_agg3["conversion_rate"] * 100, color="darkorange")
axes[2].set_title("Conversion Rate by Channel")
axes[2].set_xlabel("Conversion Rate (%)")

plot_agg4 = agg.sort_values("conversions")
axes[3].barh(plot_agg4[GROUP_COL], plot_agg4["conversions"], color="mediumpurple")
axes[3].set_title("Total Conversions by Channel")
axes[3].set_xlabel("Conversions")

plot_agg5 = agg.sort_values("spend")
axes[4].barh(plot_agg5[GROUP_COL], plot_agg5["spend"], color="indianred")
axes[4].set_title("Total Spend by Channel")
axes[4].set_xlabel("Spend ($)")

plot_agg6 = agg.sort_values("profit")
colors = ["crimson" if v < 0 else "seagreen" for v in plot_agg6["profit"]]
axes[5].barh(plot_agg6[GROUP_COL], plot_agg6["profit"], color=colors)
axes[5].axvline(0, color="black", linewidth=1)
axes[5].set_title("Profit by Channel (Revenue - Spend)")
axes[5].set_xlabel("Profit ($)")

fig.suptitle("Marketing Channel Performance Overview (2023-2025)", fontsize=14, y=1.00)
fig.tight_layout()
fig.savefig("images/group_metrics_overview.png", dpi=150, bbox_inches="tight")
print("Saved images/group_metrics_overview.png")

# ---------------------------------------------------------------------------
# Visualization: group_distributions.png (daily-level variability)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
metrics_to_plot = [("cpa", "CPA ($)"), ("roas", "ROAS"), ("conversion_rate", "Conversion Rate"), ("ctr", "CTR")]
channels = sorted(daily[GROUP_COL].unique())

for ax, (metric, label) in zip(axes[0], metrics_to_plot[:2]):
    pooled = daily[metric].dropna()
    # Clip the display range to the 1st-95th percentile: a handful of
    # extreme daily outliers (e.g. a $7k LinkedIn CPA day) otherwise stretch
    # the x-axis so every channel's bulk of days collapses to a spike at 0.
    lo, hi = pooled.quantile([0.01, 0.95])
    for ch in channels:
        vals = daily.loc[daily[GROUP_COL] == ch, metric].dropna()
        ax.hist(vals, bins=40, range=(lo, hi), alpha=0.4, label=ch, density=True)
    ax.set_xlim(lo, hi)
    ax.set_title(f"Distribution of Daily {label} by Channel\n(clipped to 1st-95th percentile)")
    ax.set_xlabel(label)
    ax.legend(fontsize=7)

box_data_cpa = [daily.loc[daily[GROUP_COL] == ch, "cpa"].dropna() for ch in channels]
axes[1][0].boxplot(box_data_cpa, tick_labels=channels, showfliers=False)
axes[1][0].set_title("Daily CPA by Channel (box plot)")
axes[1][0].tick_params(axis="x", rotation=45)

box_data_cr = [daily.loc[daily[GROUP_COL] == ch, "conversion_rate"].dropna() for ch in channels]
axes[1][1].boxplot(box_data_cr, tick_labels=channels, showfliers=False)
axes[1][1].set_title("Daily Conversion Rate by Channel (box plot)")
axes[1][1].tick_params(axis="x", rotation=45)

fig.tight_layout()
fig.savefig("images/group_distributions.png", dpi=150, bbox_inches="tight")
print("Saved images/group_distributions.png")

print("\nData exploration complete.")
