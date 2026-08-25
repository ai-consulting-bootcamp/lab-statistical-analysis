"""
Part 1: Dataset discovery, cleaning, exploration and marketing metrics.

Dataset: "Digital Marketing Metrics & KPIs to Measure (SQL)" (sinderpreet, Kaggle)
URL: https://www.kaggle.com/datasets/sinderpreet/analyze-the-marketing-spending

Outputs:
  data/marketing_data.csv         cleaned daily panel
  outputs/campaign_summary.csv    aggregate metrics per campaign
  outputs/category_summary.csv    aggregate metrics per category
  figures/group_metrics_overview.png
  figures/group_distributions.png
"""

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
RAW = "data/marketing_raw.csv"
CLEAN = "data/marketing_data.csv"

# ---------------------------------------------------------------- load
df = pd.read_csv(RAW)
print("=" * 70)
print("RAW DATA")
print("=" * 70)
print(f"shape: {df.shape}")
print(f"columns: {list(df.columns)}")
print(df.dtypes)
print(df.head())
print("\nmissing values per column:")
print(df.isna().sum())

# ---------------------------------------------------------------- clean
# 1. campaign_name has inconsistent capitalisation ("facebOOK_tier2").
#    Left uncorrected this creates a phantom extra group.
before = df["campaign_name"].nunique()
df["campaign_name"] = df["campaign_name"].str.strip().str.lower()
after = df["campaign_name"].nunique()
print(f"\ncampaign_name distinct values: {before} raw -> {after} after case normalisation")

# 2. types
df["c_date"] = pd.to_datetime(df["c_date"])
num_cols = ["impressions", "mark_spent", "clicks", "leads", "orders", "revenue"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# 3. structural checks
dupes = df.duplicated(subset=["c_date", "campaign_name"]).sum()
print(f"duplicate campaign/day rows: {dupes}")
print(f"negative values present: {(df[num_cols] < 0).any().any()}")
print(f"date range: {df.c_date.min().date()} to {df.c_date.max().date()} "
      f"({df.c_date.nunique()} distinct days)")

# 4. daily derived metrics.
#    Zero-order days give infinite CPA. We keep the rows (they are real,
#    informative days) and mark CPA as NaN so downstream tests can drop
#    them explicitly rather than silently.
df["ctr"] = df["clicks"] / df["impressions"]
df["lead_rate"] = df["leads"] / df["clicks"]
df["conv_rate"] = df["orders"] / df["clicks"]          # order per click
df["cpa"] = df["mark_spent"] / df["orders"]
df["roas"] = df["revenue"] / df["mark_spent"]
df["profit"] = df["revenue"] - df["mark_spent"]
df["aov"] = df["revenue"] / df["orders"]
df = df.replace([np.inf, -np.inf], np.nan)

zero_order_days = int((df["orders"] == 0).sum())
print(f"\nzero-order days (CPA undefined): {zero_order_days} of {len(df)} rows "
      f"({zero_order_days / len(df):.1%})")
print("zero-order days by campaign:")
print(df[df["orders"] == 0]["campaign_name"].value_counts())

df.to_csv(CLEAN, index=False)
print(f"\ncleaned panel saved to {CLEAN}")

# ---------------------------------------------------------------- aggregates
def aggregate(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    g = frame.groupby(key).agg(
        days=("c_date", "nunique"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        leads=("leads", "sum"),
        orders=("orders", "sum"),
        spend=("mark_spent", "sum"),
        revenue=("revenue", "sum"),
    )
    g["CTR"] = g["clicks"] / g["impressions"]
    g["lead_rate"] = g["leads"] / g["clicks"]
    g["conv_rate"] = g["orders"] / g["clicks"]
    g["CPA"] = g["spend"] / g["orders"]
    g["ROAS"] = g["revenue"] / g["spend"]
    g["profit"] = g["revenue"] - g["spend"]
    g["profit_margin"] = g["profit"] / g["revenue"]
    g["AOV"] = g["revenue"] / g["orders"]
    return g.replace([np.inf, -np.inf], np.nan).sort_values("ROAS", ascending=False)

camp = aggregate(df, "campaign_name")
cat = aggregate(df, "category")

pd.set_option("display.width", 200)
print("\n" + "=" * 70)
print("CAMPAIGN SUMMARY (primary grouping, 11 groups)")
print("=" * 70)
print(camp.round(3).to_string())

print("\n" + "=" * 70)
print("CATEGORY SUMMARY (secondary grouping, 4 groups)")
print("=" * 70)
print(cat.round(3).to_string())
print("\nNOTE: categories are unbalanced (social = 6 campaigns, media = 1). "
      "A category-level test on daily values is partly a test of that imbalance, "
      "which is why campaigns are the primary unit.")

camp.round(4).to_csv("outputs/campaign_summary.csv")
cat.round(4).to_csv("outputs/category_summary.csv")

# ---------------------------------------------------------------- figure 1
metrics = [
    ("CPA", "CPA (spend per order, lower is better)", True),
    ("ROAS", "ROAS (revenue per unit spend)", False),
    ("conv_rate", "Order rate per click", False),
    ("orders", "Total orders", False),
    ("spend", "Total spend", False),
    ("profit", "Profit (revenue minus spend)", False),
]
fig, axes = plt.subplots(3, 2, figsize=(14, 13))
for ax, (col, title, ascending) in zip(axes.ravel(), metrics):
    s = camp[col].sort_values(ascending=not ascending)
    colors = ["#c0392b" if v < 0 else "#2e86c1" for v in s.values]
    ax.barh(s.index, s.values, color=colors)
    ax.set_title(title, fontsize=11)
    if col in ("ROAS",):
        ax.axvline(1.0, color="black", ls="--", lw=1, label="break even")
        ax.legend(fontsize=8)
    if col == "profit":
        ax.axvline(0, color="black", ls="--", lw=1)
fig.suptitle("Campaign performance overview (Feb 2021, 28 days)", fontsize=14)
fig.tight_layout()
fig.savefig("figures/group_metrics_overview.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------- figure 2
fig, axes = plt.subplots(1, 3, figsize=(19, 6))
d_cpa = df.dropna(subset=["cpa"])
order = camp.index.tolist()

sns.boxplot(data=d_cpa, y="campaign_name", x="cpa", order=order, ax=axes[0])
axes[0].set_title("Daily CPA distribution by campaign")
axes[0].set_xlabel("daily CPA")
axes[0].set_ylabel("")

sns.boxplot(data=df, y="campaign_name", x="roas", order=order, ax=axes[1])
axes[1].axvline(1.0, color="red", ls="--", lw=1)
axes[1].set_title("Daily ROAS distribution by campaign")
axes[1].set_xlabel("daily ROAS")
axes[1].set_ylabel("")

for c in order:
    sub = d_cpa[d_cpa["campaign_name"] == c]["cpa"]
    axes[2].hist(sub, bins=12, alpha=0.35, label=c)
axes[2].set_title("Daily CPA overlay (spread, not just level)")
axes[2].set_xlabel("daily CPA")
axes[2].legend(fontsize=7)
fig.tight_layout()
fig.savefig("figures/group_distributions.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------- notes
print("\n" + "=" * 70)
print("DATA QUALITY FLAGS")
print("=" * 70)
imp = camp["impressions"].sort_values(ascending=False)
print(f"1. Impression volume is extremely skewed. Top campaign "
      f"({imp.index[0]}) has {imp.iloc[0]:,.0f} impressions versus "
      f"{imp.iloc[-1]:,.0f} for the smallest. Its CTR is therefore not "
      f"comparable to click-priced campaigns.")
print(f"2. {zero_order_days} zero-order days are excluded from every CPA test. "
      f"Dropping them biases observed CPA downward for the affected campaigns.")
print("3. Only 28 days per campaign. Every per-campaign test has n = 28 at most.")
print("4. Currency is unlabelled in the source. Treated as generic units and "
      "mapped onto the $500K brief as proportions, not absolute amounts.")
print("\nPart 1 complete.")
