"""Part 1 · Dataset discovery & exploration (Steps 1-3).

Dataset: "Marketing Campaign Performance Dataset" (Kaggle, manishabhatt22)
https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset

Usage:  python data_exploration.py <path to the downloaded CSV>
Output: marketing_data.csv (one row per campaign, cleaned + derived metrics),
        daily_channel_metrics.csv (one row per day x channel), group_metrics_summary.csv,
        figures/group_metrics_overview.png, figures/group_distributions.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid")


def money(series):
    """'$16,174.00' -> 16174.0"""
    return pd.to_numeric(series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")


def load_and_clean(path):
    raw = pd.read_csv(path)
    print("=== Raw data ===")
    print("Shape:", raw.shape)
    print("Columns:", list(raw.columns))
    print(raw.head(3).to_string())
    print("\nMissing values per column:\n", raw.isna().sum().to_string())

    df = raw.copy()
    df["Acquisition_Cost"] = money(df["Acquisition_Cost"])
    for col in ["Conversion_Rate", "ROI", "Clicks", "Impressions", "Engagement_Score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Channel"] = df["Channel_Used"].astype(str).str.strip()

    before = len(df)
    df = df.dropna(subset=["Channel", "Acquisition_Cost", "Conversion_Rate", "ROI", "Clicks", "Impressions", "Date"])
    df = df[(df["Clicks"] > 0) & (df["Impressions"] > 0) & (df["Acquisition_Cost"] > 0)]
    df = df[(df["Conversion_Rate"] >= 0) & (df["Conversion_Rate"] <= 1)]
    print(f"\nRows removed in cleaning: {before - len(df)} of {before}")

    # Derived per-campaign quantities (documented assumptions in README):
    #  - Acquisition_Cost is treated as the campaign's total spend.
    #  - Conversions = Conversion_Rate x Clicks (the dataset gives the rate, not the count).
    #  - Revenue = Cost x (1 + ROI), because ROI = (Revenue - Cost) / Cost.
    df["Cost"] = df["Acquisition_Cost"]
    df["Conversions"] = (df["Conversion_Rate"] * df["Clicks"]).round().astype(int)
    df["Revenue"] = df["Cost"] * (1 + df["ROI"])
    df["CTR"] = df["Clicks"] / df["Impressions"]
    df["CPA"] = (df["Cost"] / df["Conversions"]).replace([np.inf, -np.inf], np.nan)
    df["ROAS"] = (df["Revenue"] / df["Cost"]).replace([np.inf, -np.inf], np.nan)
    return df


def main(path):
    df = load_and_clean(path)
    keep = ["Campaign_ID", "Date", "Channel", "Campaign_Type", "Customer_Segment", "Location", "Impressions",
            "Clicks", "Conversions", "Conversion_Rate", "Cost", "Revenue", "ROI", "CTR", "CPA", "ROAS"]
    df[[c for c in keep if c in df.columns]].to_csv(HERE / "marketing_data.csv", index=False)

    print("\n=== Structure ===")
    print("Groups (channels):", sorted(df["Channel"].unique()))
    print("Campaigns per channel:\n", df["Channel"].value_counts().to_string())
    print("Date range:", df["Date"].min().date(), "to", df["Date"].max().date(),
          f"({df['Date'].nunique()} distinct days)")

    # Step 3 · aggregate metrics by channel
    g = df.groupby("Channel").agg(Impressions=("Impressions", "sum"), Clicks=("Clicks", "sum"),
                                  Conversions=("Conversions", "sum"), Cost=("Cost", "sum"),
                                  Revenue=("Revenue", "sum"), Campaigns=("Campaign_ID", "count"))
    g["CTR"] = g["Clicks"] / g["Impressions"]
    g["Conversion_Rate"] = g["Conversions"] / g["Clicks"]
    g["CPA"] = (g["Cost"] / g["Conversions"]).replace([np.inf, -np.inf], np.nan)
    g["ROAS"] = (g["Revenue"] / g["Cost"]).replace([np.inf, -np.inf], np.nan)
    g["Profit"] = g["Revenue"] - g["Cost"]
    g["Profit_Margin"] = g["Profit"] / g["Revenue"]
    g = g.sort_values("CPA")
    g.round(4).to_csv(HERE / "group_metrics_summary.csv")
    print("\n=== Channel summary ===")
    print(g.round(2).to_string())

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    plots = [("CPA", "CPA ($ per conversion, lower is better)"), ("ROAS", "ROAS (revenue / cost)"),
             ("Conversion_Rate", "Conversion rate (conversions / clicks)"), ("Conversions", "Total conversions"),
             ("Cost", "Total cost ($)"), ("Profit", "Profit ($)")]
    for ax, (col, title) in zip(axes.flat, plots):
        g[col].sort_values().plot.barh(ax=ax, color="#2C5F2D")
        ax.set_title(title)
        ax.set_ylabel("")
        if col == "Profit":
            ax.axvline(0, color="black", lw=1)
    fig.suptitle("Marketing channels: aggregate metrics", fontsize=14)
    fig.tight_layout()
    fig.savefig(FIG / "group_metrics_overview.png", dpi=120)
    plt.close(fig)

    # Per-day metrics (one value per channel per day) -> the unit of analysis for the t-tests
    d = df.groupby(["Date", "Channel"]).agg(Cost=("Cost", "sum"), Conversions=("Conversions", "sum"),
                                             Clicks=("Clicks", "sum"), Revenue=("Revenue", "sum")).reset_index()
    d["CPA"] = (d["Cost"] / d["Conversions"]).replace([np.inf, -np.inf], np.nan)
    d["Conversion_Rate"] = d["Conversions"] / d["Clicks"]
    d["ROAS"] = d["Revenue"] / d["Cost"]
    d.to_csv(HERE / "daily_channel_metrics.csv", index=False)
    print("\nDaily rows per channel:\n", d["Channel"].value_counts().to_string())

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ch, sub in d.groupby("Channel"):
        axes[0].hist(sub["CPA"].dropna(), bins=40, alpha=0.4, label=ch)
    axes[0].set_title("Daily CPA by channel (histogram overlay)")
    axes[0].set_xlabel("Daily CPA ($)")
    axes[0].legend()
    sns.boxplot(data=d, x="Channel", y="CPA", ax=axes[1], color="#97BC62")
    axes[1].set_title("Daily CPA by channel (box plot)")
    axes[1].tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(FIG / "group_distributions.png", dpi=120)
    plt.close(fig)
    print("\nSaved marketing_data.csv, daily_channel_metrics.csv, group_metrics_summary.csv and figures/.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python data_exploration.py <path to the Kaggle CSV>")
    main(sys.argv[1])
