from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datasets import load_dataset

DATASET_ID = "solsticestudioai/saas-growth-pack"
CONFIG = "channel_performance"

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def safe_divide(numerator, denominator):
    return np.where(denominator > 0, numerator / denominator, np.nan)


def add_metrics(df):
    df = df.copy()
    df["ctr"] = safe_divide(df["clicks"], df["impressions"])
    df["conversion_rate_calc"] = safe_divide(df["conversions"], df["clicks"])
    df["cpa"] = safe_divide(df["cost"], df["conversions"])
    df["roas"] = safe_divide(df["revenue_generated"], df["cost"])
    df["profit"] = df["revenue_generated"] - df["cost"]
    df["profit_margin"] = safe_divide(df["profit"], df["revenue_generated"])
    return df


def main():
    print("Loading public Hugging Face dataset...")
    dataset = load_dataset(DATASET_ID, CONFIG, split="train")
    df = dataset.to_pandas()

    print("Raw shape:", df.shape)
    print("Columns:", list(df.columns))
    print("\nFirst rows:")
    print(df.head())

    required = [
        "date", "company_name", "channel", "impressions", "clicks",
        "conversions", "cost", "revenue_generated"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    numeric_cols = [
        "impressions", "clicks", "conversions", "cost", "revenue_generated"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.drop_duplicates()
    df = df.dropna(subset=required)

    valid = (
        (df["impressions"] >= 0)
        & (df["clicks"] >= 0)
        & (df["conversions"] >= 0)
        & (df["cost"] >= 0)
        & (df["revenue_generated"] >= 0)
        & (df["impressions"] >= df["clicks"])
        & (df["clicks"] >= df["conversions"])
    )
    df = df.loc[valid].copy()
    removed = before - len(df)

    df = add_metrics(df)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.to_csv(ROOT / "marketing_data.csv", index=False)

    # Daily channel totals across the six companies.
    daily = (
        df.groupby(["date", "channel"], as_index=False)[
            ["impressions", "clicks", "conversions", "cost", "revenue_generated"]
        ]
        .sum()
    )
    daily = add_metrics(daily)
    daily = daily.replace([np.inf, -np.inf], np.nan)
    daily.to_csv(ROOT / "daily_channel_metrics.csv", index=False)

    # Full-period channel summary.
    summary = (
        df.groupby("channel", as_index=False)[
            ["impressions", "clicks", "conversions", "cost", "revenue_generated"]
        ]
        .sum()
    )
    summary = add_metrics(summary)
    summary = summary.sort_values("cpa", na_position="last")
    summary.to_csv(ROOT / "channel_summary.csv", index=False)

    print("\nCleaning summary")
    print("Rows removed:", removed)
    print("Clean rows:", len(df))
    print("Companies:", df["company_name"].nunique())
    print("Channels:", df["channel"].nunique())
    print("Channel names:", ", ".join(sorted(df["channel"].unique())))
    print("Date range:", df["date"].min().date(), "to", df["date"].max().date())
    print("\nRows per channel:")
    print(df["channel"].value_counts().sort_index())
    print("\nChannel performance summary:")
    display_cols = [
        "channel", "impressions", "clicks", "conversions", "cost",
        "revenue_generated", "ctr", "conversion_rate_calc",
        "cpa", "roas", "profit", "profit_margin"
    ]
    print(summary[display_cols].round(3).to_string(index=False))

    # Required group metrics overview.
    metrics = [
        ("cpa", "CPA (lower is better)"),
        ("roas", "ROAS (higher is better)"),
        ("conversion_rate_calc", "Conversion rate"),
        ("conversions", "Total conversions"),
        ("cost", "Total cost"),
        ("profit", "Profit"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for ax, (metric, title) in zip(axes.flat, metrics):
        plot_df = summary.sort_values(metric)
        ax.barh(plot_df["channel"], plot_df[metric])
        ax.set_title(title)
        ax.set_xlabel(metric)
        if metric == "profit":
            ax.axvline(0, linewidth=1)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "group_metrics_overview.png", dpi=160)
    plt.close(fig)

    # Required distribution view: histogram and box plot of daily CPA.
    cpa_daily = daily.dropna(subset=["cpa"])
    channels = sorted(cpa_daily["channel"].unique())

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for channel in channels:
        values = cpa_daily.loc[cpa_daily["channel"] == channel, "cpa"]
        axes[0].hist(values, bins=18, alpha=0.35, label=channel)
    axes[0].set_title("Daily CPA distributions by channel")
    axes[0].set_xlabel("Daily CPA")
    axes[0].set_ylabel("Frequency")
    axes[0].legend(fontsize=8)

    box_data = [
        cpa_daily.loc[cpa_daily["channel"] == channel, "cpa"].values
        for channel in channels
    ]
    axes[1].boxplot(box_data, tick_labels=channels, showfliers=True)
    axes[1].set_title("Daily CPA variability by channel")
    axes[1].set_ylabel("Daily CPA")
    axes[1].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "group_distributions.png", dpi=160)
    plt.close(fig)

    print("\nSaved:")
    print("- marketing_data.csv")
    print("- daily_channel_metrics.csv")
    print("- channel_summary.csv")
    print("- outputs/group_metrics_overview.png")
    print("- outputs/group_distributions.png")


if __name__ == "__main__":
    main()
