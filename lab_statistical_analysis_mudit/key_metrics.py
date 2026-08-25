"""
Step 3: Calculate Key Marketing Metrics
=========================================
Aggregates the cleaned dataset by Campaign_Type (the channel grouping variable) and
computes CTR, Conversion Rate, CPA, ROAS, Profit, and Profit Margin, then visualizes them.
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)

os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)

df = pd.read_csv("data/marketing_data.csv")

# 1. Aggregate metrics by group (Campaign_Type) -------------------------------
group_summary = df.groupby("Campaign_Type", observed=True).agg(
    campaigns=("Campaign_ID", "count"),
    impressions=("Impressions", "sum"),
    clicks=("Clicks", "sum"),
    leads=("Leads", "sum"),
    conversions=("Conversions", "sum"),
    revenue=("Revenue", "sum"),
    cost=("Total_Cost", "sum"),
)
group_summary["ctr"] = group_summary["clicks"] / group_summary["impressions"]
group_summary["conversion_rate"] = group_summary["conversions"] / group_summary["clicks"]
group_summary["cpa"] = group_summary["cost"] / group_summary["conversions"]
group_summary["roas"] = group_summary["revenue"] / group_summary["cost"]
group_summary["profit"] = group_summary["revenue"] - group_summary["cost"]
group_summary["profit_margin"] = group_summary["profit"] / group_summary["revenue"]
group_summary = group_summary.replace([np.inf, -np.inf], np.nan).round(2)

print("=" * 70)
print("GROUP SUMMARY — by Campaign_Type (5 groups)")
print("=" * 70)
print(group_summary)

group_summary.to_csv("results/group_summary_by_campaign_type.csv")

# 2. Visualize key metrics ----------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(17, 10))

order = group_summary.sort_values("cpa").index
axes[0, 0].barh(order.astype(str), group_summary.loc[order, "cpa"], color="#2E86AB")
axes[0, 0].set_xlabel("CPA ($)")
axes[0, 0].set_title("CPA by Campaign_Type (lower is better)")

order2 = group_summary.sort_values("roas").index
axes[0, 1].barh(order2.astype(str), group_summary.loc[order2, "roas"], color="#A23B72")
axes[0, 1].set_xlabel("ROAS (revenue / cost)")
axes[0, 1].set_title("ROAS by Campaign_Type")

order3 = group_summary.sort_values("conversion_rate").index
axes[0, 2].barh(order3.astype(str), group_summary.loc[order3, "conversion_rate"] * 100, color="#F18F01")
axes[0, 2].set_xlabel("Conversion rate (%) [conversions / clicks]")
axes[0, 2].set_title("Conversion rate by Campaign_Type")

order4 = group_summary.sort_values("conversions").index
axes[1, 0].barh(order4.astype(str), group_summary.loc[order4, "conversions"], color="#6A994E")
axes[1, 0].set_xlabel("Total conversions")
axes[1, 0].set_title("Total conversions by Campaign_Type")

order5 = group_summary.sort_values("cost").index
axes[1, 1].barh(order5.astype(str), group_summary.loc[order5, "cost"], color="#BC4B51")
axes[1, 1].set_xlabel("Total cost ($)")
axes[1, 1].set_title("Total cost by Campaign_Type")

order6 = group_summary.sort_values("profit").index
axes[1, 2].barh(order6.astype(str), group_summary.loc[order6, "profit"], color="#5B85AA")
axes[1, 2].axvline(0, color="black", linewidth=0.8)
axes[1, 2].set_xlabel("Profit ($) [revenue - cost]")
axes[1, 2].set_title("Profit by Campaign_Type")

for ax in axes.flat:
    ax.grid(axis="x", alpha=0.3)

fig.suptitle("Group Metrics Overview — Campaign_Type", fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/group_metrics_overview.png", dpi=150)
plt.close(fig)
print("\nSaved figures/group_metrics_overview.png")

# 3. Examine distributions -----------------------------------------------------
# Per-campaign CPA (Acquisition_Cost) is the continuous metric used for the Step 4 t-tests,
# so its distribution by group is what matters for checking t-test assumptions.
groups = sorted(df["Campaign_Type"].unique())
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for g in groups:
    subset = df.loc[df["Campaign_Type"] == g, "Acquisition_Cost"]
    axes[0].hist(np.log1p(subset), bins=40, alpha=0.4, label=g, density=True)
axes[0].set_xlabel("log(1 + CPA)")
axes[0].set_ylabel("Density")
axes[0].set_title("Distribution of CPA by group\n(log-scaled: CPA is right-skewed)")
axes[0].legend(fontsize=8)

box_data = [df.loc[df["Campaign_Type"] == g, "Acquisition_Cost"] for g in groups]
axes[1].boxplot(box_data, tick_labels=groups, showfliers=False)
axes[1].set_ylabel("CPA ($) (outliers hidden for readability)")
axes[1].set_title("CPA by group (box plot)")
axes[1].tick_params(axis="x", rotation=30)

fig.tight_layout()
fig.savefig("figures/group_distributions.png", dpi=150)
plt.close(fig)
print("Saved figures/group_distributions.png")

print()
print("=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
print("Note: conversion_rate here is conversions/clicks (per the lab's formula), separate "
      "from CPA/ROAS which are the primary cost-efficiency metrics for this dataset.")
best_cpa = group_summary["cpa"].idxmin()
worst_cpa = group_summary["cpa"].idxmax()
best_roas = group_summary["roas"].idxmax()
worst_roas = group_summary["roas"].idxmin()
print(f"Lowest (best) CPA: {best_cpa} (${group_summary.loc[best_cpa, 'cpa']:.2f})")
print(f"Highest (worst) CPA: {worst_cpa} (${group_summary.loc[worst_cpa, 'cpa']:.2f})")
print(f"Highest ROAS: {best_roas} ({group_summary.loc[best_roas, 'roas']:.2f}x)")
print(f"Lowest ROAS: {worst_roas} ({group_summary.loc[worst_roas, 'roas']:.2f}x)")
print(f"CPA is right-skewed (mean {df['Acquisition_Cost'].mean():.1f} vs. median {df['Acquisition_Cost'].median():.1f}, "
      f"max {df['Acquisition_Cost'].max():.1f}) — a small number of campaigns have very high per-acquisition cost.")
print("Sample sizes per Campaign_Type group are large (~11,000), and with n this large the t-test's "
      "reliance on the CLT for the sampling distribution of the mean holds even though the raw "
      "distribution is skewed.")
