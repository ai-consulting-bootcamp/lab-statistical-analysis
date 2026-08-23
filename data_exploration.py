from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Paths

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "KAG_conversion_data.csv"
)


# ---------------------------------------------------------
# Load raw data

df = pd.read_csv(DATA_FILE)


# ---------------------------------------------------------
# Basic structure


print("\n--- DATASET SHAPE ---")
print(df.shape)

print("\n--- COLUMNS ---")
print(df.columns.tolist())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- FIRST 5 ROWS ---")
print(df.head())


# ---------------------------------------------------------
# Missing values

print("\n--- MISSING VALUES ---")
print(df.isna().sum())


# ---------------------------------------------------------
# Duplicate rows

print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())


# ---------------------------------------------------------
# Campaign groups

if "xyz_campaign_id" in df.columns:

    print("\n--- CAMPAIGN GROUPS ---")

    print(
        df["xyz_campaign_id"]
        .value_counts()
        .sort_index()
    )

    print(
        "\nNumber of campaign groups:",
        df["xyz_campaign_id"].nunique(),
    )


# ---------------------------------------------------------
# Numeric summary

print("\n--- NUMERIC SUMMARY ---")

print(
    df.describe()
    .T
)


# ---------------------------------------------------------
# Important marketing columns

marketing_columns = [
    "Impressions",
    "Clicks",
    "Spent",
    "Total_Conversion",
    "Approved_Conversion",
]

available_marketing_columns = [
    column
    for column in marketing_columns
    if column in df.columns
]

print("\n--- AVAILABLE MARKETING METRICS ---")
print(available_marketing_columns)


# ---------------------------------------------------------
# Zero values relevant for later calculations

print("\n--- ZERO VALUES IN KEY METRICS ---")

for column in available_marketing_columns:

    zero_count = (
        df[column] == 0
    ).sum()

    print(
        f"{column}: {zero_count}"
    )


# ---------------------------------------------------------
# Prepare analysis dataset

prepared_df = df.copy()


# ---------------------------------------------------------
# Calculate derived marketing metrics

prepared_df["CTR"] = prepared_df["Clicks"] / prepared_df["Impressions"]

prepared_df["Purchase_Rate"] = np.where(
    prepared_df["Total_Conversion"] > 0,
    prepared_df["Approved_Conversion"] / prepared_df["Total_Conversion"],
    np.nan,
)

prepared_df["CPA"] = np.where(
    prepared_df["Approved_Conversion"] > 0,
    prepared_df["Spent"] / prepared_df["Approved_Conversion"],
    np.nan,
)


# ---------------------------------------------------------
# Inspect derived metrics

derived_metrics = ["CTR", "Purchase_Rate", "CPA"]

print("\n--- DERIVED METRICS ---")
print(prepared_df[derived_metrics].describe().T)

print("\n--- UNDEFINED DERIVED VALUES ---")
print(prepared_df[derived_metrics].isna().sum())


# ---------------------------------------------------------
# Save prepared dataset

OUTPUT_FILE = BASE_DIR / "data" / "marketing_data.csv"

prepared_df.to_csv(OUTPUT_FILE, index=False)

print(f"\nPrepared dataset saved to: {OUTPUT_FILE}")


# ---------------------------------------------------------
# Validate conversion relationship


print("\n--- CONVERSION RELATIONSHIP CHECK ---")
print("Approved > Total conversions:", (prepared_df["Approved_Conversion"] > prepared_df["Total_Conversion"]).sum())
print("Approved > Clicks:", (prepared_df["Approved_Conversion"] > prepared_df["Clicks"]).sum())


# ---------------------------------------------------------
# Aggregate campaign performance


campaign_summary = prepared_df.groupby("xyz_campaign_id").agg(
    ads=("ad_id", "count"),
    impressions=("Impressions", "sum"),
    clicks=("Clicks", "sum"),
    spent=("Spent", "sum"),
    total_conversions=("Total_Conversion", "sum"),
    approved_conversions=("Approved_Conversion", "sum"),
).reset_index()

campaign_summary["CTR"] = campaign_summary["clicks"] / campaign_summary["impressions"]
campaign_summary["Purchase_Rate"] = campaign_summary["approved_conversions"] / campaign_summary["total_conversions"]
campaign_summary["CPA"] = campaign_summary["spent"] / campaign_summary["approved_conversions"]


# ---------------------------------------------------------
# Display campaign summary


campaign_display = campaign_summary.copy()

campaign_display["CTR_pct"] = campaign_display["CTR"] * 100
campaign_display["Purchase_Rate_pct"] = campaign_display["Purchase_Rate"] * 100

display_columns = [
    "xyz_campaign_id",
    "ads",
    "impressions",
    "clicks",
    "spent",
    "total_conversions",
    "approved_conversions",
    "CTR_pct",
    "Purchase_Rate_pct",
    "CPA",
]

print("\n--- CAMPAIGN PERFORMANCE SUMMARY ---")
print(campaign_display[display_columns].round(2).to_string(index=False))


# ---------------------------------------------------------
# Save campaign summary


SUMMARY_FILE = BASE_DIR / "results" / "campaign_summary.csv"
SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)

campaign_summary.to_csv(SUMMARY_FILE, index=False)

print(f"\nCampaign summary saved to: {SUMMARY_FILE}")


'''
At campaign level:

CTR — which campaign gets clicks most efficiently from impressions?
Purchase Rate — which campaign converts recorded enquiries/conversions into approved purchases most successfully?
CPA — which campaign spends the least for each approved purchase? Lower is better.
Approved conversions — which campaign generates the largest absolute number of successful outcomes?
Spend — how much budget was required to generate those outcomes?
'''

# ---------------------------------------------------------
# Visualize campaign performance
# ---------------------------------------------------------

campaign_labels = campaign_summary["xyz_campaign_id"].astype(str)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].bar(campaign_labels, campaign_summary["CTR"] * 100)
axes[0].set_title("CTR by Campaign")
axes[0].set_xlabel("Campaign")
axes[0].set_ylabel("CTR (%)")

axes[1].bar(campaign_labels, campaign_summary["Purchase_Rate"] * 100)
axes[1].set_title("Purchase Rate by Campaign")
axes[1].set_xlabel("Campaign")
axes[1].set_ylabel("Purchase Rate (%)")

axes[2].bar(campaign_labels, campaign_summary["CPA"])
axes[2].set_title("CPA by Campaign")
axes[2].set_xlabel("Campaign")
axes[2].set_ylabel("Cost per Approved Conversion")

plt.tight_layout()

OVERVIEW_FILE = BASE_DIR / "results" / "group_metrics_overview.png"
plt.savefig(OVERVIEW_FILE, dpi=150, bbox_inches="tight")
plt.close()

print(f"\nCampaign overview saved to: {OVERVIEW_FILE}")


# ---------------------------------------------------------
# Prepare distribution data
# ---------------------------------------------------------
# exclude NaN when plotting

campaign_ids = sorted(prepared_df["xyz_campaign_id"].unique())

cpa_data = [
    prepared_df.loc[
        (prepared_df["xyz_campaign_id"] == campaign_id) & prepared_df["CPA"].notna(),
        "CPA",
    ]
    for campaign_id in campaign_ids
]

purchase_rate_data = [
    prepared_df.loc[
        (prepared_df["xyz_campaign_id"] == campaign_id) & prepared_df["Purchase_Rate"].notna(),
        "Purchase_Rate",
    ]
    for campaign_id in campaign_ids
]

# ---------------------------------------------------------
# Visualize metric distributions
# ---------------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for campaign_id in campaign_ids:
    values = prepared_df.loc[
        (prepared_df["xyz_campaign_id"] == campaign_id) & prepared_df["CPA"].notna(),
        "CPA",
    ]

    axes[0, 0].hist(values, bins=25, alpha=0.5, label=str(campaign_id))

axes[0, 0].set_title("CPA Distribution")
axes[0, 0].set_xlabel("CPA")
axes[0, 0].set_ylabel("Number of Ads")
axes[0, 0].legend(title="Campaign")

axes[0, 1].boxplot(cpa_data, tick_labels=[str(x) for x in campaign_ids])
axes[0, 1].set_title("CPA by Campaign")
axes[0, 1].set_xlabel("Campaign")
axes[0, 1].set_ylabel("CPA")

for campaign_id in campaign_ids:
    values = prepared_df.loc[
        (prepared_df["xyz_campaign_id"] == campaign_id) & prepared_df["Purchase_Rate"].notna(),
        "Purchase_Rate",
    ]

    axes[1, 0].hist(values, bins=20, alpha=0.5, label=str(campaign_id))

axes[1, 0].set_title("Purchase Rate Distribution")
axes[1, 0].set_xlabel("Purchase Rate")
axes[1, 0].set_ylabel("Number of Ads")
axes[1, 0].legend(title="Campaign")

axes[1, 1].boxplot(purchase_rate_data, tick_labels=[str(x) for x in campaign_ids])
axes[1, 1].set_title("Purchase Rate by Campaign")
axes[1, 1].set_xlabel("Campaign")
axes[1, 1].set_ylabel("Purchase Rate")

plt.tight_layout()

DISTRIBUTION_FILE = BASE_DIR / "results" / "group_distributions.png"
plt.savefig(DISTRIBUTION_FILE, dpi=150, bbox_inches="tight")
plt.close()

print(f"\nGroup distributions saved to: {DISTRIBUTION_FILE}")

# ---------------------------------------------------------
# Distribution sample sizes
# ---------------------------------------------------------

print("\n--- METRIC SAMPLE SIZES BY CAMPAIGN ---")

for campaign_id in campaign_ids:
    campaign_data = prepared_df[prepared_df["xyz_campaign_id"] == campaign_id]

    print(
        f"Campaign {campaign_id}: "
        f"ads={len(campaign_data)}, "
        f"CPA observations={campaign_data['CPA'].notna().sum()}, "
        f"Purchase Rate observations={campaign_data['Purchase_Rate'].notna().sum()}"
    )

# ---------------------------------------------------------
# Distribution diagnostics
# ---------------------------------------------------------

print("\n--- CPA DISTRIBUTION DIAGNOSTICS ---")

for campaign_id in campaign_ids:
    values = prepared_df.loc[
        (prepared_df["xyz_campaign_id"] == campaign_id) & prepared_df["CPA"].notna(),
        "CPA",
    ]

    print(
        f"Campaign {campaign_id}: "
        f"n={len(values)}, "
        f"mean={values.mean():.2f}, "
        f"median={values.median():.2f}, "
        f"std={values.std():.2f}, "
        f"skew={values.skew():.2f}"
    )