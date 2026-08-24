import pandas as pd
import numpy as np
from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------

INPUT_PATH = Path("data/raw/digital_marketing_dataset_30k.csv")
OUTPUT_PATH = Path("data/processed/marketing_data_clean.csv")
SUMMARY_PATH = Path("results/tables/platform_summary.csv")


# --------------------------------------------------
# Load data
# --------------------------------------------------

print("Loading dataset...")

df = pd.read_csv(INPUT_PATH)

print(f"Loaded {len(df):,} rows.")


# --------------------------------------------------
# Date conversion
# --------------------------------------------------

df["date"] = pd.to_datetime(
    df["date"],
    dayfirst=True
)


# --------------------------------------------------
# Data quality
# --------------------------------------------------

print("\nDATA QUALITY")
print("=" * 60)

print("Shape:", df.shape)

print("\nMissing values:")
print(df.isna().sum().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())


# --------------------------------------------------
# Numerical summary
# --------------------------------------------------

numeric_columns = [
    "spend",
    "impressions",
    "reach",
    "clicks",
    "conversions",
    "revenue",
    "video_views"
]

print("\nNUMERICAL SUMMARY")
print("=" * 60)

print(df[numeric_columns].describe())


# --------------------------------------------------
# Platform distribution
# --------------------------------------------------

print("\nPLATFORM DISTRIBUTION")
print("=" * 60)

print(df["platform"].value_counts())


# --------------------------------------------------
# Calculate marketing metrics
# --------------------------------------------------

print("\nCALCULATING MARKETING METRICS")


# CTR
df["ctr"] = np.where(
    df["impressions"] > 0,
    df["clicks"] / df["impressions"],
    np.nan
)


# Conversion Rate
df["conversion_rate"] = np.where(
    df["clicks"] > 0,
    df["conversions"] / df["clicks"],
    np.nan
)


# CPA
df["cpa"] = np.where(
    df["conversions"] > 0,
    df["spend"] / df["conversions"],
    np.nan
)


# ROAS
df["roas"] = np.where(
    df["spend"] > 0,
    df["revenue"] / df["spend"],
    np.nan
)


# Profit
df["profit"] = df["revenue"] - df["spend"]


# Profit margin
df["profit_margin"] = np.where(
    df["revenue"] > 0,
    df["profit"] / df["revenue"],
    np.nan
)


# --------------------------------------------------
# Remove invalid infinite values
# --------------------------------------------------

metric_columns = [
    "ctr",
    "conversion_rate",
    "cpa",
    "roas",
    "profit_margin"
]

df[metric_columns] = df[metric_columns].replace(
    [np.inf, -np.inf],
    np.nan
)


# --------------------------------------------------
# Platform summary
# --------------------------------------------------

summary = (
    df.groupby("platform")
    .agg(
        observations=("platform", "size"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    )
    .reset_index()
)


# --------------------------------------------------
# Aggregate marketing metrics
# --------------------------------------------------

summary["ctr"] = (
    summary["clicks"] /
    summary["impressions"]
)

summary["conversion_rate"] = (
    summary["conversions"] /
    summary["clicks"]
)

summary["cpa"] = np.where(
    summary["conversions"] > 0,
    summary["spend"] / summary["conversions"],
    np.nan
)

summary["roas"] = np.where(
    summary["spend"] > 0,
    summary["revenue"] / summary["spend"],
    np.nan
)

summary["profit"] = (
    summary["revenue"] -
    summary["spend"]
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\nPLATFORM PERFORMANCE")
print("=" * 60)

print(
    summary.round(3).to_string(index=False)
)


# --------------------------------------------------
# Save processed dataset
# --------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

SUMMARY_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

summary.to_csv(
    SUMMARY_PATH,
    index=False
)


print("\nFILES SAVED")
print("=" * 60)

print(OUTPUT_PATH)
print(SUMMARY_PATH)