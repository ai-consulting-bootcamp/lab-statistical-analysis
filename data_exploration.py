"""Part 1: dataset discovery, loading, cleaning and key marketing metrics.

Dataset
-------
Name:    Digital Marketing Performance Dataset (Synthetic, Benchmark-Based)
Author:  alinaboulsi on Kaggle
Kaggle:  https://www.kaggle.com/datasets/alinaboulsi/digital-marketing-performance-dataset
Mirror:  https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset
         (pinned to revision aaa929af5f0b69f6c49ab409f718ff836825c744; loaded from here
         because the Kaggle API needs credentials and the HF mirror is a public URL)

Why this one: it is the only candidate I found with every raw column the lab needs
(spend, impressions, clicks, conversions, revenue) per ad per day, across 6 ad
platforms, over 3 years. The more popular "Marketing Campaign Performance 200k"
dataset was rejected: it has no spend, conversion-count or revenue column (only
pre-computed Conversion_Rate, ROI and a campaign-level "Acquisition_Cost"), so
CPA and ROAS could not be derived from raw counts. Caveat: this dataset is synthetic (benchmark
ranges for CPM/CTR/CVR/AOV plus seasonality). Its README says it should not
drive real budget decisions; the memo repeats that caveat.

Run:  python data_exploration.py
Writes: data/marketing_data.csv, results/group_metrics.csv,
        figures/group_metrics_overview.png, figures/group_distributions.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import false_discovery_control, fisher_exact  # noqa: F401 (used in Part 2)

HERE = Path(__file__).resolve().parent
DATA, RESULTS, FIGS = HERE / "data", HERE / "results", HERE / "figures"
for d in (DATA, RESULTS, FIGS):
    d.mkdir(exist_ok=True)

HF_REVISION = "aaa929af5f0b69f6c49ab409f718ff836825c744"
RAW_URL = (
    "https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset"
    f"/resolve/{HF_REVISION}/digital_marketing_dataset_30k.csv"
)
RAW_CACHE = DATA / "raw_digital_marketing_dataset_30k.csv"

sns.set_theme(style="whitegrid")
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)


def section(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


# --------------------------------------------------------------------------
# Step 2.2: load
# --------------------------------------------------------------------------
section("LOAD")
if not RAW_CACHE.exists():
    print(f"Downloading {RAW_URL}")
    pd.read_csv(RAW_URL).to_csv(RAW_CACHE, index=False)
raw = pd.read_csv(RAW_CACHE)
print(f"Shape: {raw.shape}")
print(f"Columns: {list(raw.columns)}")
print(raw.dtypes.value_counts().to_string())
print(raw[["date", "platform", "objective", "spend", "clicks", "conversions", "revenue"]].head())

# --------------------------------------------------------------------------
# Step 2.3: explore structure and quality
# --------------------------------------------------------------------------
section("STRUCTURE AND QUALITY")
raw["date"] = pd.to_datetime(raw["date"], format="%d/%m/%Y")
print(f"Date range: {raw.date.min():%Y-%m-%d} to {raw.date.max():%Y-%m-%d} "
      f"({raw.date.nunique()} distinct days)")
print(f"Missing values: {int(raw.isna().sum().sum())}")
print(f"Exact duplicate rows: {int(raw.duplicated().sum())}")
checks = {
    "clicks > impressions": (raw.clicks > raw.impressions).sum(),
    "conversions > clicks": (raw.conversions > raw.clicks).sum(),
    "negative spend/clicks/conv/revenue": (raw[["spend", "clicks", "conversions", "revenue"]] < 0).any(axis=1).sum(),
    "zero spend": (raw.spend == 0).sum(),
}
for k, v in checks.items():
    print(f"  {k:<38} {int(v)}")

print("\nGrouping variable: platform (6 channels)")
print(raw.platform.value_counts().to_string())

print("\nSpend vs conversions/revenue by campaign objective:")
by_obj = raw.groupby("objective")[["spend", "conversions", "revenue"]].sum().round(0)
print(by_obj.to_string())
print(
    "\n-> Reach/Traffic/Engagement/Video Views campaigns spend ~$8.9M but produce almost no\n"
    "   conversions and zero revenue by design. Including them would make CPA a measure of\n"
    "   how much awareness spend a platform carries, not how well it sells. Leads carry a\n"
    "   lead-value *proxy* as revenue, not purchases. For an e-commerce budget question the\n"
    "   right population is objective == 'Sales' (purchase-optimised campaigns)."
)

# Outliers at row level (ad-day): heavy right tail is expected in ad data
sales = raw[raw.objective == "Sales"].copy()
q = sales[["spend", "clicks", "conversions", "revenue"]].quantile([0.5, 0.99, 1.0]).T
q.columns = ["median", "p99", "max"]
print("\nSales rows, per ad-day distribution (heavy right tail, kept, not errors):")
print(q.round(1).to_string())
print(f"Sales ad-days with zero conversions: {(sales.conversions == 0).mean():.1%}")

# --------------------------------------------------------------------------
# Step 2.4: prepare. Unit of analysis = platform x ISO week
# --------------------------------------------------------------------------
section("PREPARE: platform x week panel")
print(
    "Why weekly, not daily: Sales campaigns average ~0.8 rows per platform per day, so many\n"
    "platform-days have 0 or 1 ads and CPA is undefined or one ad's luck. Weekly sums give\n"
    "~5 ads per cell and ~155 complete weeks per platform. Partial first/last weeks are dropped."
)
sales["week"] = sales["date"].dt.to_period("W-SUN").dt.start_time
weekly = (
    sales.groupby(["platform", "week"])
    .agg(n_ads=("ad_id", "size"), impressions=("impressions", "sum"), clicks=("clicks", "sum"),
         conversions=("conversions", "sum"), cost=("spend", "sum"), revenue=("revenue", "sum"))
    .reset_index()
)
first_full = raw.date.min() + pd.offsets.Week(weekday=0)  # first Monday
last_full = raw.date.max() - pd.Timedelta(days=6)
weekly = weekly[(weekly.week >= first_full.normalize()) & (weekly.week <= last_full)]

weekly["ctr"] = weekly.clicks / weekly.impressions
weekly["conversion_rate"] = weekly.conversions / weekly.clicks
weekly["cpa"] = (weekly.cost / weekly.conversions).replace([np.inf, -np.inf], np.nan)
weekly["roas"] = (weekly.revenue / weekly.cost).replace([np.inf, -np.inf], np.nan)
weekly["profit"] = weekly.revenue - weekly.cost

weekly.to_csv(DATA / "marketing_data.csv", index=False)
print(f"\nSaved data/marketing_data.csv: {len(weekly)} rows")
print("Transformations: parsed dd/mm/yyyy dates; kept objective == 'Sales' (5,453 of 30,000 rows);")
print("summed to platform x ISO week; dropped partial edge weeks; derived CTR, CVR, CPA, ROAS,")
print("profit; division-by-zero CPA/ROAS set to NaN.")

summary = weekly.groupby("platform").agg(
    weeks=("week", "size"), ads=("n_ads", "sum"), weeks_zero_conv=("conversions", lambda s: int((s == 0).sum())),
    first_week=("week", "min"), last_week=("week", "max"))
print(f"\nGroups: {weekly.platform.nunique()}")
print(summary.to_string())

# --------------------------------------------------------------------------
# Step 3.1: aggregate metrics by channel
# --------------------------------------------------------------------------
section("KEY METRICS BY CHANNEL (totals over the whole period)")
g = weekly.groupby("platform")[["impressions", "clicks", "conversions", "cost", "revenue"]].sum()
g["ctr"] = g.clicks / g.impressions
g["conversion_rate"] = g.conversions / g.clicks
g["cpa"] = g.cost / g.conversions
g["roas"] = g.revenue / g.cost
g["profit"] = g.revenue - g.cost
g["profit_margin"] = g.profit / g.revenue
g = g.replace([np.inf, -np.inf], np.nan).sort_values("cpa")
g.round(4).to_csv(RESULTS / "group_metrics.csv")

show = g.copy()
for c in ("ctr", "conversion_rate", "profit_margin"):
    show[c] = (show[c] * 100).round(2).astype(str) + "%"
print(show.round(2).to_string())

# --------------------------------------------------------------------------
# Step 3.2: overview figure
# --------------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
panels = [
    ("cpa", "CPA ($, lower is better)", "{:.0f}"),
    ("roas", "ROAS (revenue / cost)", "{:.2f}"),
    ("conversion_rate", "Conversion rate (conv / clicks)", "{:.2%}"),
    ("conversions", "Total conversions", "{:,.0f}"),
    ("cost", "Total cost ($)", "{:,.0f}"),
    ("profit", "Profit ($ revenue - cost)", "{:,.0f}"),
]
palette = dict(zip(g.index, sns.color_palette("tab10", len(g))))
for ax, (col, title, fmt) in zip(axes.flat, panels):
    s = g[col].sort_values()
    ax.barh(s.index, s.values, color=[palette[p] for p in s.index])
    ax.set_title(title, fontweight="bold")
    for i, v in enumerate(s.values):
        ax.text(v, i, " " + fmt.format(v), va="center", fontsize=9)
    if col == "profit":
        ax.axvline(0, color="black", lw=1)
    if col == "roas":
        ax.axvline(1, color="grey", ls="--", lw=1)
    ax.margins(x=0.25)
fig.suptitle("Sales-objective campaigns by platform, 2023-2025 (weekly panel totals)", fontsize=14)
fig.tight_layout()
fig.savefig(FIGS / "group_metrics_overview.png", dpi=130)
plt.close(fig)

# --------------------------------------------------------------------------
# Step 3.3: distributions of weekly metrics
# --------------------------------------------------------------------------
section("WEEKLY DISTRIBUTIONS (variability)")
dist = weekly.groupby("platform")[["cpa", "conversion_rate", "roas"]].agg(["mean", "std"])
cv = (dist.xs("std", axis=1, level=1) / dist.xs("mean", axis=1, level=1)).add_suffix("_cv")
print(dist.round(3).to_string())
print("\nCoefficient of variation (std / mean) per platform:")
print(cv.round(2).to_string())
print(f"\nMean weekly CPA CV across platforms: {cv.cpa_cv.mean():.2f} "
      "(the lab's power simulation assumes 0.15; Part 4 tests both)")

order = g.index.tolist()
fig, axes = plt.subplots(2, 3, figsize=(17, 9))
for ax, col, title in zip(axes[0], ["cpa", "conversion_rate", "roas"],
                          ["Weekly CPA ($, log scale)", "Weekly conversion rate", "Weekly ROAS (log scale)"]):
    d = weekly.dropna(subset=[col])
    if col != "conversion_rate":
        d = d[d[col] > 0]  # log scale: drops the few zero-revenue weeks from the ROAS plot only
    vals = np.log10(d[col]) if col != "conversion_rate" else d[col]
    for p in order:
        ax.hist(vals[d.platform == p], bins=30, alpha=0.45, label=p, color=palette[p])
    ax.set_title(f"{title}: histogram", fontweight="bold")
    if col != "conversion_rate":
        ax.set_xlabel(f"log10({col})")
    ax.legend(fontsize=8)
for ax, col, title in zip(axes[1], ["cpa", "conversion_rate", "roas"],
                          ["Weekly CPA ($)", "Weekly conversion rate", "Weekly ROAS"]):
    sns.boxplot(data=weekly, x="platform", y=col, order=order, hue="platform", palette=palette,
                legend=False, ax=ax, fliersize=2)
    if col != "conversion_rate":
        ax.set_yscale("log")
    ax.set_title(f"{title}: box plot", fontweight="bold")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=30)
fig.suptitle("Week-to-week variability by platform", fontsize=14)
fig.tight_layout()
fig.savefig(FIGS / "group_distributions.png", dpi=130)
plt.close(fig)

section("SEASONALITY (pooled CPA by quarter)")
season = weekly.assign(quarter="Q" + weekly.week.dt.quarter.astype(str)).groupby(["quarter", "platform"])[
    ["cost", "conversions"]].sum()
season = (season.cost / season.conversions).unstack().round(2)
print(season.to_string())
print("-> Q4 CPA is ~40% below Q1-Q3 on every platform (holiday demand). Rankings are stable across\n"
      "   quarters, but levels are not: any short-window comparison must say which season it covers.")

section("KEY INSIGHTS")
print(f"- Best CPA: {g.cpa.idxmin()} (${g.cpa.min():.2f}); worst: {g.cpa.idxmax()} (${g.cpa.max():.2f}).")
print(f"- Best ROAS: {g.roas.idxmax()} ({g.roas.max():.2f}x). ROAS < 1 (loses money): "
      f"{', '.join(g.index[g.roas < 1])}.")
print(f"- Most variable weekly CPA (CV): {cv.cpa_cv.idxmax()} ({cv.cpa_cv.max():.2f}).")
print("- Meta, Snapchat and TikTok sit in a tight $25-31 CPA cluster: that is where the tests matter.")
print("- Mean of weekly CPAs is above the pooled CPA (e.g. Google Search $6.43 vs $5.31): averaging\n"
      "  ratios over-weights low-volume weeks. Tests use weekly values; the budget view uses pooled totals.")
print("- Outliers are single big-revenue weeks (right tail), not data errors; kept.")
print("\nSaved figures/group_metrics_overview.png and figures/group_distributions.png")
