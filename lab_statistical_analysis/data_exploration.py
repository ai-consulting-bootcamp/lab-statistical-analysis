from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "marketing_campaign_source.csv"
OUTPUT = HERE / "marketing_data.csv"


def main():
    df = pd.read_csv(SOURCE)
    print("Dataset shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Acquisition_Cost"] = (
        df["Acquisition_Cost"].astype(str).str.replace(r"[$,]", "", regex=True).astype(float)
    )
    df["Conversion_Rate"] = pd.to_numeric(df["Conversion_Rate"], errors="coerce")
    df["Clicks"] = pd.to_numeric(df["Clicks"], errors="coerce")
    df["Impressions"] = pd.to_numeric(df["Impressions"], errors="coerce")
    df["ROI"] = pd.to_numeric(df["ROI"], errors="coerce")
    df["Conversions"] = (df["Clicks"] * df["Conversion_Rate"]).round().clip(lower=0).astype("Int64")
    df["Conversions"] = df["Conversions"].where(df["Conversions"] <= df["Clicks"])
    df["Revenue"] = df["Acquisition_Cost"] * (1 + df["ROI"])
    df["CTR"] = df["Clicks"] / df["Impressions"].replace(0, np.nan)
    df["CPA"] = df["Acquisition_Cost"] / df["Conversions"].replace(0, np.nan)
    df["ROAS"] = df["Revenue"] / df["Acquisition_Cost"].replace(0, np.nan)
    df["Profit"] = df["Revenue"] - df["Acquisition_Cost"]
    df["Profit_Margin"] = df["Profit"] / df["Revenue"].replace(0, np.nan)

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["Channel_Used", "Date", "Acquisition_Cost", "Clicks", "Conversions"])
    df.to_csv(OUTPUT, index=False)

    print("\nMissing values after cleaning:")
    print(df.isna().sum().loc[lambda s: s > 0].to_string())
    print("\nGroups:", df["Channel_Used"].nunique())
    print(df["Channel_Used"].value_counts().sort_index().to_string())
    print("\nDate range:", df["Date"].min().date(), "to", df["Date"].max().date())

    daily = df.groupby(["Date", "Channel_Used"], as_index=False).agg(
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
        Conversions=("Conversions", "sum"),
        Cost=("Acquisition_Cost", "sum"),
        Revenue=("Revenue", "sum"),
    )
    daily["CTR"] = daily["Clicks"] / daily["Impressions"].replace(0, np.nan)
    daily["Conversion_Rate"] = daily["Conversions"] / daily["Clicks"].replace(0, np.nan)
    daily["CPA"] = daily["Cost"] / daily["Conversions"].replace(0, np.nan)
    daily["ROAS"] = daily["Revenue"] / daily["Cost"].replace(0, np.nan)
    daily["Profit"] = daily["Revenue"] - daily["Cost"]
    daily["Profit_Margin"] = daily["Profit"] / daily["Revenue"].replace(0, np.nan)
    daily = daily.replace([np.inf, -np.inf], np.nan)

    channel = df.groupby("Channel_Used", as_index=False).agg(
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
        Conversions=("Conversions", "sum"),
        Cost=("Acquisition_Cost", "sum"),
        Revenue=("Revenue", "sum"),
    )
    channel["CTR"] = channel["Clicks"] / channel["Impressions"]
    channel["Conversion_Rate"] = channel["Conversions"] / channel["Clicks"]
    channel["CPA"] = channel["Cost"] / channel["Conversions"]
    channel["ROAS"] = channel["Revenue"] / channel["Cost"]
    channel["Profit"] = channel["Revenue"] - channel["Cost"]
    channel["Profit_Margin"] = channel["Profit"] / channel["Revenue"]
    channel.to_csv(HERE / "channel_summary.csv", index=False, float_format="%.6f")
    print("\nChannel summary:")
    print(channel.round(4).to_string(index=False))

    sns.set_theme(style="whitegrid")
    metrics = [
        ("CPA", "CPA by Channel"),
        ("ROAS", "ROAS by Channel"),
        ("Conversion_Rate", "Conversion Rate by Channel"),
        ("Conversions", "Total Conversions by Channel"),
        ("Cost", "Total Cost by Channel"),
        ("Profit", "Profit by Channel"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, (metric, title) in zip(axes.flat, metrics):
        plot_data = channel.sort_values(metric, ascending=metric not in ("ROAS", "Conversions", "Profit"))
        sns.barplot(data=plot_data, x=metric, y="Channel_Used", ax=ax)
        ax.set_title(title)
        ax.set_ylabel("")
        ax.ticklabel_format(axis="x", style="plain")
        if metric == "Profit":
            ax.axvline(0, color="black", linewidth=1)
    fig.tight_layout()
    fig.savefig(HERE / "group_metrics_overview.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, metric in zip(axes.flat, ["CPA", "Conversion_Rate", "ROAS", "Profit"]):
        for channel_name in sorted(daily["Channel_Used"].dropna().unique()):
            values = daily.loc[daily["Channel_Used"] == channel_name, metric].dropna()
            ax.hist(values, bins=30, alpha=0.35, label=channel_name)
        ax.set_title(f"{metric} Distribution")
        ax.set_xlabel(metric)
        ax.set_ylabel("Frequency")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(HERE / "group_distributions.png", dpi=150)
    plt.close(fig)

    daily.to_csv(HERE / "daily_channel_metrics.csv", index=False, float_format="%.6f")


if __name__ == "__main__":
    main()
