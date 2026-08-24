"""
Step 3: Calculate Key Marketing Metrics
=========================================
Aggregates the cleaned dataset by group (most_ads_day) and by the primary
experiment arm (test_group), computes the metrics that are actually available
in this dataset (conversion rate, ad exposure), and visualizes them.

No CPA / ROAS / CTR here — this dataset has no cost, revenue, or impression
data (see dataset_selection.md).
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)

df = pd.read_csv("data/marketing_data.csv")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df["most_ads_day"] = pd.Categorical(df["most_ads_day"], categories=day_order, ordered=True)

# 1. Aggregate metrics by group (most_ads_day) -------------------------------
group_summary = df.groupby("most_ads_day", observed=True).agg(
    users=("user_id", "count"),
    conversions=("converted", "sum"),
    total_ads_sum=("total_ads", "sum"),
    total_ads_mean=("total_ads", "mean"),
    total_ads_median=("total_ads", "median"),
    total_ads_std=("total_ads", "std"),
)
group_summary["conversion_rate"] = group_summary["conversions"] / group_summary["users"]
group_summary = group_summary.round(2)

print("=" * 70)
print("GROUP SUMMARY — by most_ads_day (7 groups)")
print("=" * 70)
print(group_summary)

# 2. Aggregate metrics by test_group (the actual A/B experiment) -------------
arm_summary = df.groupby("test_group", observed=True).agg(
    users=("user_id", "count"),
    conversions=("converted", "sum"),
    total_ads_mean=("total_ads", "mean"),
)
arm_summary["conversion_rate"] = arm_summary["conversions"] / arm_summary["users"]
arm_summary = arm_summary.round(4)

print()
print("=" * 70)
print("ARM SUMMARY — by test_group (ad vs. psa)")
print("=" * 70)
print(arm_summary)

group_summary.to_csv("results/group_summary_by_day.csv")
arm_summary.to_csv("results/arm_summary_ad_vs_psa.csv")

# 3. Visualize key metrics ----------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

order = group_summary.sort_values("conversion_rate").index
axes[0, 0].barh(order.astype(str), group_summary.loc[order, "conversion_rate"] * 100, color="#2E86AB")
axes[0, 0].set_xlabel("Conversion rate (%)")
axes[0, 0].set_title("Conversion rate by most_ads_day")

order2 = group_summary.sort_values("total_ads_mean").index
axes[0, 1].barh(order2.astype(str), group_summary.loc[order2, "total_ads_mean"], color="#A23B72")
axes[0, 1].set_xlabel("Mean total ads shown")
axes[0, 1].set_title("Mean ad exposure by most_ads_day")

order3 = group_summary.sort_values("conversions").index
axes[1, 0].barh(order3.astype(str), group_summary.loc[order3, "conversions"], color="#F18F01")
axes[1, 0].set_xlabel("Total conversions")
axes[1, 0].set_title("Total conversions by most_ads_day")

order4 = group_summary.sort_values("users").index
axes[1, 1].barh(order4.astype(str), group_summary.loc[order4, "users"], color="#6A994E")
axes[1, 1].set_xlabel("Number of users")
axes[1, 1].set_title("Sample size by most_ads_day")

for ax in axes.flat:
    ax.grid(axis="x", alpha=0.3)

fig.suptitle("Group Metrics Overview — most_ads_day", fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/group_metrics_overview.png", dpi=150)
plt.close(fig)
print("\nSaved figures/group_metrics_overview.png")

# 4. Examine distributions -----------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for day in day_order:
    subset = df.loc[df["most_ads_day"] == day, "total_ads"]
    axes[0].hist(np.log1p(subset), bins=40, alpha=0.35, label=day, density=True)
axes[0].set_xlabel("log(1 + total_ads)")
axes[0].set_ylabel("Density")
axes[0].set_title("Distribution of ad exposure by group\n(log-scaled: total_ads is heavily right-skewed)")
axes[0].legend(fontsize=8)

box_data = [df.loc[df["most_ads_day"] == day, "total_ads"] for day in day_order]
axes[1].boxplot(box_data, tick_labels=day_order, showfliers=False)
axes[1].set_ylabel("total_ads (outliers hidden for readability)")
axes[1].set_title("total_ads by group (box plot)")
axes[1].tick_params(axis="x", rotation=45)

fig.tight_layout()
fig.savefig("figures/group_distributions.png", dpi=150)
plt.close(fig)
print("Saved figures/group_distributions.png")

print()
print("=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
best_conv = group_summary["conversion_rate"].idxmax()
worst_conv = group_summary["conversion_rate"].idxmin()
print(f"Highest conversion rate: {best_conv} ({group_summary.loc[best_conv, 'conversion_rate']:.2%})")
print(f"Lowest conversion rate:  {worst_conv} ({group_summary.loc[worst_conv, 'conversion_rate']:.2%})")
print(f"total_ads is heavily right-skewed (mean {df['total_ads'].mean():.1f} vs. median {df['total_ads'].median():.1f}, "
      f"max {df['total_ads'].max()}) — a small number of users see very many ads.")
print("Sample sizes per most_ads_day group are large (77k-93k), and with n this large the t-test's "
      "reliance on the CLT for the sampling distribution of the mean holds even though the raw "
      "distribution is skewed.")
