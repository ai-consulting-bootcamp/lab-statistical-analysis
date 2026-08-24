"""
Part 1: Dataset Discovery & Exploration
Marketing Channel Budget Allocation Lab

Dataset: "Marketing Campaign Performance Dataset"
Source: Kaggle (mirrored/used in the public GitHub project below, same file,
        same columns/row count as the original Kaggle release)
URL: https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset
     (CSV pulled via https://github.com/vignesh4005/Marketing_Campaign_Performance_Insights)
Why chosen: 22,029 individual campaign records across 6 real digital marketing
channels (Facebook, Google Ads, Instagram, Website, Email, YouTube) with cost,
conversion rate, ROI, clicks and impressions per campaign -- exactly the
multi-group, sufficiently-powered structure the CMO scenario needs, and it
maps directly onto the 7-channel budget-allocation ask (we have 6 of the 7
in real data; see executive_memo.md for how the analysis generalizes).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid")
RAW_PATH = "data/marketing_campaign_raw.csv"
CLEAN_PATH = "data/marketing_data.csv"

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
print("\nGrouping variable -> Channel_Used:")
print(df["Channel_Used"].value_counts())

print("\nMissing values per column:")
print(df.isna().sum())

print("\nDate range:", df["Date"].min(), "to", df["Date"].max())

# ---------------------------------------------------------------------------
# 3. Clean + derive marketing metrics per campaign
# ---------------------------------------------------------------------------
clean = df.copy()
clean["Date"] = pd.to_datetime(clean["Date"], format="%d-%m-%Y")
clean = clean.rename(columns={"Channel_Used": "Channel", "Acquisition_Cost": "Cost"})

# The raw file gives Conversion_Rate (%), Cost, ROI (%), Clicks, Impressions.
# We derive the standard marketing metrics the lab asks for:
#   Conversions      = Clicks * Conversion_Rate / 100          (estimated conversions)
#   Revenue           = Cost * (1 + ROI / 100)                  (since ROI = (Rev-Cost)/Cost*100)
#   CPA               = Cost / Conversions
#   ROAS              = Revenue / Cost
#   CTR               = Clicks / Impressions
#   Profit            = Revenue - Cost
#   Profit_Margin     = Profit / Revenue
# NOTE on Conversions: estimated (not a raw column) as Clicks * Conversion_Rate / 100,
# rounded to the nearest whole conversion. We do NOT clip to a minimum of 1 -- a genuine
# zero-conversion campaign should stay zero, not be inflated into a "successful" one.
# Zero-conversion campaigns naturally produce an infinite CPA (Cost / 0 conversions);
# we replace those with NaN below and they are excluded from CPA comparisons rather
# than being silently forced to some fake performance number.
#
# NOTE on Revenue/ROI: the raw dataset does not include a Revenue column, only ROI (%).
# We assume the dataset's ROI is defined the standard way, ROI = (Revenue - Cost) / Cost,
# which lets us back out Revenue = Cost * (1 + ROI/100). This is an assumption made
# necessary by the dataset's fields, not a value given directly by the source -- flagged
# here and in executive_memo.md so any reader knows how Revenue/ROAS were derived.
clean["Conversions"] = (clean["Clicks"] * clean["Conversion_Rate"] / 100).round().astype(int)
clean["Revenue"] = clean["Cost"] * (1 + clean["ROI"] / 100)
clean["CPA"] = clean["Cost"] / clean["Conversions"]          # inf/NaN where Conversions == 0
clean["ROAS"] = clean["Revenue"] / clean["Cost"]
clean["CTR"] = clean["Clicks"] / clean["Impressions"]
clean["Profit"] = clean["Revenue"] - clean["Cost"]
clean["Profit_Margin"] = clean["Profit"] / clean["Revenue"]

# Handle infinities (e.g. zero-conversion campaigns) defensively -- these become NaN and
# are excluded by pandas/scipy in downstream aggregation and t-tests rather than distorting them.
n_zero_conversion = int((clean["Conversions"] == 0).sum())
clean = clean.replace([np.inf, -np.inf], np.nan)

# Save prepared dataset
clean.to_csv(CLEAN_PATH, index=False)
print(f"\nSaved cleaned dataset -> {CLEAN_PATH}  (shape={clean.shape})")

# ---------------------------------------------------------------------------
# 4. Group summary
# ---------------------------------------------------------------------------
group_summary = clean.groupby("Channel").agg(
    n_campaigns=("Campaign_ID", "count"),
    total_cost=("Cost", "sum"),
    total_revenue=("Revenue", "sum"),
    total_clicks=("Clicks", "sum"),
    total_impressions=("Impressions", "sum"),
    total_conversions=("Conversions", "sum"),
    mean_conversion_rate=("Conversion_Rate", "mean"),
    mean_CPA=("CPA", "mean"),
    mean_ROAS=("ROAS", "mean"),
    mean_CTR=("CTR", "mean"),
    mean_ROI_pct=("ROI", "mean"),
    total_profit=("Profit", "sum"),
).round(2)
group_summary["profit_margin_%"] = (group_summary["total_profit"] / group_summary["total_revenue"] * 100).round(2)
print("\nGroup (channel) summary:\n", group_summary)
group_summary.to_csv("outputs/group_summary.csv")

# ---------------------------------------------------------------------------
# 5. Visualize key metrics
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(3, 2, figsize=(13, 14))
order = group_summary.sort_values("mean_CPA").index

group_summary.loc[order, "mean_CPA"].plot(kind="barh", ax=axes[0, 0], color="#4C72B0")
axes[0, 0].set_title("Mean CPA by Channel ($)")
axes[0, 0].set_xlabel("CPA ($)")

group_summary.loc[order, "mean_ROAS"].plot(kind="barh", ax=axes[0, 1], color="#55A868")
axes[0, 1].set_title("Mean ROAS by Channel")
axes[0, 1].set_xlabel("ROAS (x)")

group_summary.loc[order, "mean_conversion_rate"].plot(kind="barh", ax=axes[1, 0], color="#C44E52")
axes[1, 0].set_title("Mean Conversion Rate by Channel (%)")
axes[1, 0].set_xlabel("Conversion Rate (%)")

group_summary.loc[order, "total_conversions"].plot(kind="barh", ax=axes[1, 1], color="#8172B2")
axes[1, 1].set_title("Total Estimated Conversions by Channel")
axes[1, 1].set_xlabel("Conversions")

group_summary.loc[order, "total_cost"].plot(kind="barh", ax=axes[2, 0], color="#CCB974")
axes[2, 0].set_title("Total Spend by Channel ($)")
axes[2, 0].set_xlabel("Cost ($)")

group_summary.loc[order, "total_profit"].plot(kind="barh", ax=axes[2, 1], color="#64B5CD")
axes[2, 1].axvline(0, color="black", linewidth=1)
axes[2, 1].set_title("Total Profit by Channel ($)")
axes[2, 1].set_xlabel("Profit ($)")

plt.tight_layout()
plt.savefig("outputs/group_metrics_overview.png", dpi=150)
plt.close()
print("Saved outputs/group_metrics_overview.png")

# ---------------------------------------------------------------------------
# 6. Distributions (per-campaign variability within each channel)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
channels = clean["Channel"].unique()
colors = plt.cm.tab10(np.linspace(0, 1, len(channels)))

for ch, c in zip(channels, colors):
    subset = clean[clean["Channel"] == ch]
    axes[0, 0].hist(subset["CPA"], bins=30, alpha=0.4, label=ch, color=c)
    axes[0, 1].hist(subset["Conversion_Rate"], bins=30, alpha=0.4, label=ch, color=c)

axes[0, 0].set_title("CPA Distribution by Channel")
axes[0, 0].set_xlabel("CPA ($)")
axes[0, 0].legend(fontsize=7)

axes[0, 1].set_title("Conversion Rate Distribution by Channel")
axes[0, 1].set_xlabel("Conversion Rate (%)")
axes[0, 1].legend(fontsize=7)

clean.boxplot(column="CPA", by="Channel", ax=axes[1, 0], rot=45)
axes[1, 0].set_title("CPA by Channel (box plot)")
axes[1, 0].set_xlabel("")
plt.suptitle("")

clean.boxplot(column="Conversion_Rate", by="Channel", ax=axes[1, 1], rot=45)
axes[1, 1].set_title("Conversion Rate by Channel (box plot)")
axes[1, 1].set_xlabel("")
plt.suptitle("")

plt.tight_layout()
plt.savefig("outputs/group_distributions.png", dpi=150)
plt.close()
print("Saved outputs/group_distributions.png")

print("\n=== Part 1 complete ===")
best_roas = group_summary["mean_ROAS"].idxmax()
best_cpa = group_summary["mean_CPA"].idxmin()
worst_cpa = group_summary["mean_CPA"].idxmax()
cpa_std = clean.groupby("Channel")["CPA"].std().sort_values(ascending=False)
most_variable = cpa_std.index[0]

print("Best mean ROAS:", best_roas, group_summary.loc[best_roas, "mean_ROAS"])
print("Best mean CPA (lowest):", best_cpa, group_summary.loc[best_cpa, "mean_CPA"])
print("Highest variability (CPA std):")
print(cpa_std)
print(f"Zero-conversion campaigns (excluded from CPA, kept in raw counts): {n_zero_conversion}")

# ---------------------------------------------------------------------------
# 7. Key insights (written takeaway, not just printed numbers)
# ---------------------------------------------------------------------------
insights = f"""KEY INSIGHTS -- Part 1 Exploration
====================================
- Groups: {len(group_summary)} channels ({', '.join(group_summary.index)}), each with
  roughly {group_summary['n_campaigns'].min()}-{group_summary['n_campaigns'].max()} campaigns
  (well above the 3-5 group / hundreds-per-group minimum the lab asks for).
- Best point-estimate ROAS: {best_roas} ({group_summary.loc[best_roas, 'mean_ROAS']}x).
- Best point-estimate CPA (lowest/cheapest): {best_cpa} (${group_summary.loc[best_cpa, 'mean_CPA']}).
- Worst point-estimate CPA (most expensive): {worst_cpa} (${group_summary.loc[worst_cpa, 'mean_CPA']}).
- Most variable channel by CPA std dev: {most_variable} (std=${cpa_std.iloc[0]:.2f}) -- this
  channel's campaign-level performance is the least consistent, which matters for risk,
  not just average return.
- Zero-conversion campaigns: {n_zero_conversion} out of {len(clean)} -- these are excluded
  from CPA/ROAS averages (division by zero) rather than forced to a fake minimum.
- Caveat: these are point-estimate rankings only. Whether the CPA/ROAS gaps between
  channels are statistically distinguishable (vs. noise) is tested in Part 2-3 --
  do not act on this ranking alone.
"""
print(insights)
with open("outputs/key_insights.md", "w") as f:
    f.write(insights)
print("Saved outputs/key_insights.md")
