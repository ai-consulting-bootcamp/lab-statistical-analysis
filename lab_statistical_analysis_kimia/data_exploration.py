"""
Data Exploration — Marketing Channel ROI Comparison Lab
=========================================================

Dataset: Marketing Campaign Performance Dataset
Source: Kaggle
Author: Manisha B
URL: https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset
Why chosen: ~200,000 rows of campaign-level marketing data with a clear grouping
variable (Channel_Used — 5 channels: Display, Influencer, Search, Email, Social Media)
and performance metrics (Conversion_Rate, Acquisition_Cost, ROI, Clicks, Impressions,
Engagement_Score). This gives enough groups and enough sample size per group for
pairwise statistical comparison, multiple-comparisons correction, and power analysis.

NOTE ON HONESTY: this script expects the raw CSV downloaded directly from Kaggle
at data/marketing_campaign_dataset.csv (or similar). I have not personally inspected
the raw file's exact column names — this script inspects and prints them first,
and the COLUMN_MAP below should be corrected if the real headers differ.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid") if "seaborn-v0_8-whitegrid" in plt.style.available else None

RAW_PATH_CANDIDATES = [
    "data/marketing_campaign_dataset.csv",
    "data/marketing_campaign_performance_dataset.csv",
    "data/raw_dataset.csv",
]

# Expected columns per the dataset's public description. If the actual file's
# headers differ, update this map (key = what this script expects internally,
# value = actual column name in the CSV).
COLUMN_MAP = {
    "channel": "Channel_Used",
    "campaign_type": "Campaign_Type",
    "company": "Company",
    "conversion_rate": "Conversion_Rate",
    "acquisition_cost": "Acquisition_Cost",
    "roi": "ROI",
    "clicks": "Clicks",
    "impressions": "Impressions",
    "engagement_score": "Engagement_Score",
    "date": "Date",
    "duration": "Duration",
    "target_audience": "Target_Audience",
    "customer_segment": "Customer_Segment",
    "location": "Location",
}


def find_raw_file():
    import os
    for p in RAW_PATH_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "No raw dataset found. Download the CSV from Kaggle "
        "(manishabhatt22/marketing-campaign-performance-dataset), unzip it, "
        "and place it at data/marketing_campaign_dataset.csv"
    )


def load_raw():
    path = find_raw_file()
    df = pd.read_csv(path)
    print(f"Loaded raw file: {path}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(df.head())
    print(df.dtypes)
    return df


def reconcile_columns(df):
    """Check COLUMN_MAP against actual headers; warn on mismatches."""
    missing = [v for v in COLUMN_MAP.values() if v not in df.columns]
    if missing:
        print("\n*** WARNING: These expected columns were not found in the raw file:")
        for m in missing:
            print(f"  - {m}")
        print("Actual columns available:", list(df.columns))
        print("Update COLUMN_MAP at the top of this script to match, then re-run.\n")
    return missing


def clean_and_prepare(df):
    cm = COLUMN_MAP
    df = df.copy()

    # Acquisition_Cost sometimes ships as a currency string (e.g. "$1,234.56")
    if cm["acquisition_cost"] in df.columns and not pd.api.types.is_numeric_dtype(df[cm["acquisition_cost"]]):
        df[cm["acquisition_cost"]] = (
            df[cm["acquisition_cost"]].astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .astype(float)
        )

    # Conversion_Rate: strip % if stored as string
    if cm["conversion_rate"] in df.columns and not pd.api.types.is_numeric_dtype(df[cm["conversion_rate"]]):
        df[cm["conversion_rate"]] = (
            df[cm["conversion_rate"]].astype(str).str.replace("%", "", regex=False).astype(float)
        )

    numeric_cols = [cm[k] for k in
                    ["conversion_rate", "acquisition_cost", "roi", "clicks", "impressions", "engagement_score"]
                    if cm[k] in df.columns]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if cm["date"] in df.columns:
        df[cm["date"]] = pd.to_datetime(df[cm["date"]], errors="coerce")

    before = len(df)
    df = df.dropna(subset=[c for c in [cm["channel"]] + numeric_cols if c in df.columns])
    after = len(df)
    print(f"\nDropped {before - after} rows with missing key values ({before} -> {after})")

    # Derived metrics this lab needs downstream.
    # Approximate "conversions" as clicks * conversion_rate, and "cost" per
    # campaign row as Acquisition_Cost (already a per-conversion or per-campaign
    # cost figure in this dataset — documented in the README once confirmed).
    if cm["clicks"] in df.columns and cm["conversion_rate"] in df.columns:
        cr = df[cm["conversion_rate"]]
        # Handle both 0-1 and 0-100 scale conversion rates
        cr_frac = cr / 100 if cr.max() > 1.5 else cr
        df["conversions_est"] = (df[cm["clicks"]] * cr_frac).round()

    # CTR = Clicks / Impressions (Step 3 requirement — computable from this dataset)
    if cm["clicks"] in df.columns and cm["impressions"] in df.columns:
        df["ctr"] = df[cm["clicks"]] / df[cm["impressions"]]

    return df


def channel_summary(df):
    cm = COLUMN_MAP
    ch = cm["channel"]
    metrics = [c for c in
               [cm["conversion_rate"], cm["acquisition_cost"], cm["roi"],
                cm["clicks"], cm["impressions"], cm["engagement_score"],
                "ctr"]
               if c in df.columns or c == "ctr"]

    summary = df.groupby(ch)[metrics].agg(["mean", "median", "std", "count"]).round(2)
    print("\n=== Channel Summary (Step 3: Key Marketing Metrics) ===")
    print(summary)

    n_by_channel = df[ch].value_counts()
    print("\n=== Sample size per channel ===")
    print(n_by_channel)

    date_range = None
    if cm["date"] in df.columns:
        date_range = (df[cm["date"]].min(), df[cm["date"]].max())
        print(f"\nDate range: {date_range[0]} to {date_range[1]}")

    print(
        "\n*** NOTE on ROAS / Profit / Profit Margin ***\n"
        "This dataset (Kaggle: manishabhatt22/marketing-campaign-performance-dataset)\n"
        "has no Revenue column, only Acquisition_Cost and ROI (already a computed ratio).\n"
        "ROAS = Revenue / Cost and Profit = Revenue - Cost both require a Revenue figure\n"
        "that isn't present in the raw data, so they cannot be honestly computed here.\n"
        "ROI is reported instead as the closest available proxy for return performance.\n"
        "This is a documented dataset limitation, not an oversight — see README.md.\n"
    )

    return summary, n_by_channel, date_range


def plot_distributions(df, outdir="outputs"):
    import os
    os.makedirs(outdir, exist_ok=True)
    cm = COLUMN_MAP
    ch = cm["channel"]
    metrics = [c for c in [cm["conversion_rate"], cm["acquisition_cost"], cm["roi"]] if c in df.columns]

    fig, axes = plt.subplots(1, len(metrics), figsize=(6 * len(metrics), 5))
    if len(metrics) == 1:
        axes = [axes]
    for ax, metric in zip(axes, metrics):
        for channel, sub in df.groupby(ch):
            ax.hist(sub[metric].dropna(), bins=30, alpha=0.5, label=str(channel))
        ax.set_title(f"{metric} distribution by channel")
        ax.set_xlabel(metric)
        ax.set_ylabel("Count")
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{outdir}/group_distributions.png", dpi=150)
    print(f"\nSaved {outdir}/group_distributions.png")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    df.boxplot(column=cm["conversion_rate"] if cm["conversion_rate"] in df.columns else metrics[0],
               by=ch, ax=ax)
    ax.set_title("Conversion rate by channel")
    plt.suptitle("")
    plt.tight_layout()
    plt.savefig(f"{outdir}/group_boxplot.png", dpi=150)
    print(f"Saved {outdir}/group_boxplot.png")
    plt.close()


def plot_metrics_overview(df, outdir="outputs"):
    """Step 3 required chart: CPA, ROAS, conversion rate, total conversions,
    total cost, profit — one panel each where computable. ROAS and Profit
    panels are replaced with an explicit 'not available' note since this
    dataset has no Revenue column (see channel_summary() note printed above)."""
    import os
    os.makedirs(outdir, exist_ok=True)
    cm = COLUMN_MAP
    ch = cm["channel"]

    means = df.groupby(ch)[[cm["acquisition_cost"], cm["roi"], cm["conversion_rate"], "ctr"]].mean()

    # conversions_est total and cost total, computed directly for clarity
    if "conversions_est" in df.columns:
        total_conversions = df.groupby(ch)["conversions_est"].sum()
    else:
        total_conversions = df.groupby(ch)[cm["clicks"]].count()
    total_cost = df.groupby(ch)[cm["acquisition_cost"]].sum()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    means[cm["acquisition_cost"]].sort_values().plot.barh(ax=axes[0], color="steelblue")
    axes[0].set_title("CPA (Acquisition Cost) by channel")

    axes[1].text(0.5, 0.5, "ROAS not available:\nno Revenue column in this dataset\n(see note in console output)",
                 ha="center", va="center", fontsize=11, wrap=True)
    axes[1].set_title("ROAS by channel")
    axes[1].axis("off")

    means[cm["conversion_rate"]].sort_values(ascending=False).plot.barh(ax=axes[2], color="seagreen")
    axes[2].set_title("Conversion rate by channel")

    total_conversions.sort_values(ascending=False).plot.barh(ax=axes[3], color="darkorange")
    axes[3].set_title("Total conversions by channel")

    total_cost.sort_values(ascending=False).plot.barh(ax=axes[4], color="indianred")
    axes[4].set_title("Total cost by channel")

    axes[5].text(0.5, 0.5, "Profit not available:\nno Revenue column in this dataset\n(ROI reported instead — see table above)",
                 ha="center", va="center", fontsize=11, wrap=True)
    axes[5].set_title("Profit by channel")
    axes[5].axis("off")

    plt.tight_layout()
    plt.savefig(f"{outdir}/group_metrics_overview.png", dpi=150)
    print(f"Saved {outdir}/group_metrics_overview.png")
    plt.close()


def main():
    print("=" * 70)
    print("PART 1: DATASET DISCOVERY & EXPLORATION")
    print("STEP 1: Dataset selected — see README.md for name/source/URL/rationale")
    print("STEP 2: Load and Explore Your Dataset")
    print("=" * 70)
    df_raw = load_raw()
    missing = reconcile_columns(df_raw)
    df = clean_and_prepare(df_raw)
    print("\n" + "=" * 70)
    print("STEP 3: Calculate Key Marketing Metrics")
    print("=" * 70)
    summary, n_by_channel, date_range = channel_summary(df)

    # Mean-only view kept for reference; plot_metrics_overview now takes df directly
    cm = COLUMN_MAP
    plot_metrics_overview(df)
    plot_distributions(df)

    out_path = "data/marketing_data_clean.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved cleaned dataset to {out_path} ({df.shape[0]} rows, {df.shape[1]} cols)")

    print("\n=== Data exploration complete ===")


if __name__ == "__main__":
    main()
