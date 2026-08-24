import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------

INPUT_PATH = Path("data/processed/marketing_data_clean.csv")
FIGURE_PATH = Path("results/figures")

FIGURE_PATH.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(INPUT_PATH)

print("Loaded processed dataset:", df.shape)


# --------------------------------------------------
# Platform summary
# --------------------------------------------------

summary = (
    df.groupby("platform")
    .agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    )
    .reset_index()
)

summary["ctr"] = summary["clicks"] / summary["impressions"]

summary["conversion_rate"] = (
    summary["conversions"] / summary["clicks"]
)

summary["cpa"] = (
    summary["spend"] / summary["conversions"]
)

summary["roas"] = (
    summary["revenue"] / summary["spend"]
)

summary["profit"] = (
    summary["revenue"] - summary["spend"]
)


# --------------------------------------------------
# Figure 1 — Group metrics overview
# --------------------------------------------------

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# CTR
axes[0, 0].barh(summary["platform"], summary["ctr"] * 100)
axes[0, 0].set_title("CTR by Platform")
axes[0, 0].set_xlabel("CTR (%)")

# Conversion rate
axes[0, 1].barh(
    summary["platform"],
    summary["conversion_rate"] * 100
)
axes[0, 1].set_title("Conversion Rate by Platform")
axes[0, 1].set_xlabel("Conversion Rate (%)")

# CPA
axes[0, 2].barh(summary["platform"], summary["cpa"])
axes[0, 2].set_title("CPA by Platform")
axes[0, 2].set_xlabel("CPA")

# ROAS
axes[1, 0].barh(summary["platform"], summary["roas"])
axes[1, 0].set_title("ROAS by Platform")
axes[1, 0].set_xlabel("ROAS")

# Conversions
axes[1, 1].barh(
    summary["platform"],
    summary["conversions"]
)
axes[1, 1].set_title("Conversions by Platform")
axes[1, 1].set_xlabel("Conversions")

# Profit
axes[1, 2].barh(
    summary["platform"],
    summary["profit"]
)
axes[1, 2].axvline(0, linewidth=1)
axes[1, 2].set_title("Profit by Platform")
axes[1, 2].set_xlabel("Profit")

plt.tight_layout()

output = FIGURE_PATH / "group_metrics_overview.png"

plt.savefig(output, dpi=150)
plt.close()

print("Saved:", output)


# --------------------------------------------------
# Figure 2 — Distribution of CPA
# --------------------------------------------------

platforms = summary["platform"].tolist()

distribution_data = []

for platform in platforms:
    values = df.loc[
        df["platform"] == platform,
        "cpa"
    ].dropna()

    # Remove extreme infinite/invalid values
    values = values[values > 0]

    distribution_data.append(values)


plt.figure(figsize=(14, 8))

plt.boxplot(
    distribution_data,
    tick_labels=platforms,
    showfliers=False
)

plt.title("CPA Distribution by Platform")
plt.ylabel("CPA")
plt.xticks(rotation=30)

plt.tight_layout()

output = FIGURE_PATH / "group_distributions.png"

plt.savefig(output, dpi=150)
plt.close()

print("Saved:", output)


print("\nVisualization creation completed successfully.")