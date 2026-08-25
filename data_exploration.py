"""
data_exploration.py
Part 1: Dataset Discovery & Exploration
Marketing channel performance analysis lab

Dataset: alsayed7/marketing_dataset (Hugging Face)
URL: https://huggingface.co/datasets/alsayed7/marketing_dataset
Why chosen: 2,000 real-format e-commerce campaign records spanning 4 marketing
channels (Influencer Marketing, Paid Ads, Email, Social Media) with the exact
fields needed for CPA/ROAS/conversion-rate analysis (impressions, clicks,
conversions, spend, revenue). For this lab, a representative sample of the
first 400 campaigns was pulled via the HF Datasets Viewer API (network access
inside the analysis environment is restricted, so rows were retrieved through
the dataset viewer and reassembled locally as marketing_data_raw.csv).
"""

import numpy as np  # type: ignore[reportMissingImports]
import pandas as pd  # type: ignore[reportMissingImports]
import matplotlib.pyplot as plt  # type: ignore[reportMissingImports]

pd.set_option("display.width", 120)
plt.style.use("seaborn-v0_8-whitegrid")

# ---------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------
df = pd.read_csv("marketing_data_raw.csv")
print("Shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nDtypes:\n", df.dtypes)
print("\nHead:\n", df.head())

# ---------------------------------------------------------------
# 2. Explore structure
# ---------------------------------------------------------------
print("\nMarketing_Channel value counts:\n", df["Marketing_Channel"].value_counts())
print("\nMissing values per column:\n", df.isna().sum())
print("\nNumeric summary:\n", df[["Impressions", "Clicks", "Conversions",
                                   "Total_Spend", "Revenue_Generated"]].describe())

# Sanity checks: Clicks should not exceed Impressions, Conversions should not
# exceed Clicks. Flag (but do not silently drop) violations.
bad_clicks = (df["Clicks"] > df["Impressions"]).sum()
bad_conv = (df["Conversions"] > df["Clicks"]).sum()
print(f"\nRows where Clicks > Impressions: {bad_clicks}")
print(f"Rows where Conversions > Clicks: {bad_conv}")

# ---------------------------------------------------------------
# 3. Clean + feature engineering
# ---------------------------------------------------------------
df["Start_Date"] = pd.to_datetime(df["Start_Date"])
df["End_Date"] = pd.to_datetime(df["End_Date"])

# Per-campaign derived metrics
df["CTR"] = df["Clicks"] / df["Impressions"]
df["Conversion_Rate"] = df["Conversions"] / df["Clicks"]
df["CPA"] = df["Total_Spend"] / df["Conversions"]
df["ROAS"] = df["Revenue_Generated"] / df["Total_Spend"]
df["Profit"] = df["Revenue_Generated"] - df["Total_Spend"]
df["Profit_Margin"] = df["Profit"] / df["Revenue_Generated"]

# Replace inf (zero-cost / zero-click edge cases) with NaN rather than dropping rows
df = df.replace([np.inf, -np.inf], np.nan)

df.to_csv("marketing_data.csv", index=False)
print("\nSaved cleaned dataset -> marketing_data.csv")
print("Rows with NaN CPA/ROAS (zero spend or zero conversions):",
      df["CPA"].isna().sum(), "/", df["ROAS"].isna().sum())

# ---------------------------------------------------------------
# 4. Group-level (channel-level) summary metrics
# ---------------------------------------------------------------
agg = df.groupby("Marketing_Channel").agg(
    n_campaigns=("Campaign_ID", "count"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Conversions=("Conversions", "sum"),
    Total_Spend=("Total_Spend", "sum"),
    Revenue_Generated=("Revenue_Generated", "sum"),
).reset_index()

agg["CTR"] = agg["Clicks"] / agg["Impressions"]
agg["Conversion_Rate"] = agg["Conversions"] / agg["Clicks"]
agg["CPA"] = agg["Total_Spend"] / agg["Conversions"]
agg["ROAS"] = agg["Revenue_Generated"] / agg["Total_Spend"]
agg["Profit"] = agg["Revenue_Generated"] - agg["Total_Spend"]
agg["Profit_Margin"] = agg["Profit"] / agg["Revenue_Generated"]

agg_display = agg.round(2)
print("\n=== Channel summary (aggregate) ===")
print(agg_display.to_string(index=False))
agg.to_csv("output/data/channel_summary.csv", index=False)

# ---------------------------------------------------------------
# 5. Visualize: group_metrics_overview.png
# ---------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
order = agg.sort_values("CPA")["Marketing_Channel"]

def barh(ax, data, x, title, fmt="{:.2f}", color="#4C72B0"):
    d = data.set_index("Marketing_Channel").loc[order]
    bars = ax.barh(d.index, d[x], color=color)
    ax.set_title(title, fontsize=11, fontweight="bold")
    for b, v in zip(bars, d[x]):
        ax.text(b.get_width(), b.get_y() + b.get_height() / 2, " " + fmt.format(v),
                va="center", fontsize=9)
    ax.invert_yaxis()

barh(axes[0, 0], agg, "CPA", "CPA by Channel ($)", color="#C44E52")
barh(axes[0, 1], agg, "ROAS", "ROAS by Channel (x)", color="#55A868")
barh(axes[0, 2], agg, "Conversion_Rate", "Conversion Rate by Channel",
     fmt="{:.2%}", color="#8172B2")
barh(axes[1, 0], agg, "Conversions", "Total Conversions by Channel", fmt="{:,.0f}",
     color="#4C72B0")
barh(axes[1, 1], agg, "Total_Spend", "Total Spend by Channel ($)", fmt="${:,.0f}",
     color="#CCB974")
ax = axes[1, 2]
d = agg.set_index("Marketing_Channel").loc[order]
colors = ["#55A868" if v >= 0 else "#C44E52" for v in d["Profit"]]
ax.barh(d.index, d["Profit"], color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Profit by Channel ($)", fontsize=11, fontweight="bold")
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("output/images/group_metrics_overview.png", dpi=150)
plt.close()
print("Saved output/images/group_metrics_overview.png")

# ---------------------------------------------------------------
# 6. Distributions: group_distributions.png
# ---------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
channels = df["Marketing_Channel"].unique()
palette = dict(zip(channels, ["#4C72B0", "#C44E52", "#55A868", "#8172B2"]))

for ch in channels:
    sub = df[df["Marketing_Channel"] == ch]
    axes[0, 0].hist(sub["CPA"].dropna(), bins=25, alpha=0.5, label=ch, color=palette[ch])
    axes[0, 1].hist(sub["ROAS"].dropna(), bins=25, alpha=0.5, label=ch, color=palette[ch])

axes[0, 0].set_title("CPA distribution by channel")
axes[0, 0].set_xlabel("CPA ($)")
axes[0, 0].legend(fontsize=8)
axes[0, 1].set_title("ROAS distribution by channel")
axes[0, 1].set_xlabel("ROAS (x)")
axes[0, 1].legend(fontsize=8)

df.boxplot(column="CPA", by="Marketing_Channel", ax=axes[1, 0])
axes[1, 0].set_title("CPA by channel (boxplot)")
axes[1, 0].set_xlabel("")
plt.sca(axes[1, 0])
plt.xticks(rotation=20)

df.boxplot(column="Conversion_Rate", by="Marketing_Channel", ax=axes[1, 1])
axes[1, 1].set_title("Conversion rate by channel (boxplot)")
axes[1, 1].set_xlabel("")
plt.sca(axes[1, 1])
plt.xticks(rotation=20)

plt.suptitle("")
plt.tight_layout()
plt.savefig("output/images/group_distributions.png", dpi=150)
plt.close()
print("Saved output/images/group_distributions.png")

print("\nPart 1 complete.")
