"""Prepare and explore the Hugging Face marketing-channel dataset."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-paola-stat-lab")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
SOURCE = DATA / "source_channel_performance.csv"
PREPARED = DATA / "marketing_data.csv"
COMPANY = "VectorFlow"


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = numerator.div(denominator.replace(0, np.nan))
    return result.replace([np.inf, -np.inf], np.nan)


def add_daily_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["ctr"] = safe_divide(frame["clicks"], frame["impressions"])
    frame["conversion_rate"] = safe_divide(frame["conversions"], frame["clicks"])
    frame["cpa"] = safe_divide(frame["cost"], frame["conversions"])
    frame["roas"] = safe_divide(frame["revenue_generated"], frame["cost"])
    frame["profit"] = frame["revenue_generated"] - frame["cost"]
    frame["profit_margin"] = safe_divide(frame["profit"], frame["revenue_generated"])
    return frame


def aggregate_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    summary = (
        frame.groupby("channel", as_index=False)
        .agg(
            observations=("date", "size"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            cost=("cost", "sum"),
            revenue=("revenue_generated", "sum"),
        )
    )
    summary["ctr"] = safe_divide(summary["clicks"], summary["impressions"])
    summary["conversion_rate"] = safe_divide(summary["conversions"], summary["clicks"])
    summary["cpa"] = safe_divide(summary["cost"], summary["conversions"])
    summary["roas"] = safe_divide(summary["revenue"], summary["cost"])
    summary["profit"] = summary["revenue"] - summary["cost"]
    summary["profit_margin"] = safe_divide(summary["profit"], summary["revenue"])
    return summary.sort_values("channel").reset_index(drop=True)


def validate_source(frame: pd.DataFrame) -> dict[str, object]:
    required = {
        "date",
        "company_id",
        "company_name",
        "channel",
        "impressions",
        "clicks",
        "conversions",
        "cost",
        "revenue_generated",
    }
    missing_columns = sorted(required - set(frame.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    numeric = ["impressions", "clicks", "conversions", "cost", "revenue_generated"]
    if frame[numeric].isna().any().any():
        raise ValueError("Required numeric fields contain missing values")
    if (frame[numeric] < 0).any().any():
        raise ValueError("Negative count, spend, or revenue found")
    funnel_errors = int(
        ((frame["impressions"] < frame["clicks"]) | (frame["clicks"] < frame["conversions"])).sum()
    )
    if funnel_errors:
        raise ValueError(f"Found {funnel_errors} rows violating impressions >= clicks >= conversions")
    return {
        "source_rows": int(len(frame)),
        "source_companies": int(frame["company_name"].nunique()),
        "source_channels": int(frame["channel"].nunique()),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_company_date_channel_rows": int(
            frame.duplicated(["company_name", "date", "channel"]).sum()
        ),
        "funnel_invariant_errors": funnel_errors,
    }


def plot_overview(summary: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    specs = [
        ("cpa", "CPA (USD, lower is better)", False),
        ("roas", "ROAS (x, higher is better)", False),
        ("conversion_rate", "Conversion rate", True),
        ("conversions", "Total conversions", False),
        ("cost", "Total cost (USD)", False),
        ("profit", "Profit (USD)", False),
    ]
    for ax, (metric, title, percent) in zip(axes.flat, specs):
        ordered = summary.sort_values(metric, ascending=True)
        sns.barplot(data=ordered, y="channel", x=metric, ax=ax, color="#4776E6")
        ax.set_title(title)
        ax.set_ylabel("")
        if percent:
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.1%}"))
        if metric == "profit":
            ax.axvline(0, color="black", linewidth=1)
    fig.suptitle(f"Marketing Channel Performance — {COMPANY} (90 days)", fontsize=16)
    fig.tight_layout()
    fig.savefig(FIGURES / "group_metrics_overview.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_distributions(frame: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    cpa = frame.dropna(subset=["cpa"])
    sns.boxplot(data=cpa, x="cpa", y="channel", ax=axes[0], color="#8E9AE6")
    axes[0].set_title("Daily CPA on conversion-positive days")
    axes[0].set_xlabel("CPA (USD)")
    axes[0].set_ylabel("")
    sns.boxplot(data=frame, x="roas", y="channel", ax=axes[1], color="#6CC4A1")
    axes[1].set_title("Daily ROAS distribution")
    axes[1].set_xlabel("ROAS (x)")
    axes[1].set_ylabel("")
    fig.suptitle("Within-channel variability and outliers", fontsize=16)
    fig.tight_layout()
    fig.savefig(FIGURES / "group_distributions.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    source = pd.read_csv(SOURCE, parse_dates=["date"])
    quality = validate_source(source)
    prepared = source.loc[source["company_name"].eq(COMPANY)].copy()
    if len(prepared) != 630 or prepared["channel"].nunique() != 7:
        raise ValueError("Expected exactly 90 days x 7 channels for VectorFlow")
    prepared = add_daily_metrics(prepared).sort_values(["date", "channel"])
    prepared.to_csv(PREPARED, index=False, date_format="%Y-%m-%d")

    summary = aggregate_metrics(prepared)
    summary.to_csv(OUTPUTS / "group_performance_summary.csv", index=False)
    quality.update(
        {
            "analysis_company": COMPANY,
            "prepared_rows": int(len(prepared)),
            "analysis_channels": int(prepared["channel"].nunique()),
            "date_min": prepared["date"].min().date().isoformat(),
            "date_max": prepared["date"].max().date().isoformat(),
            "days_per_channel": prepared.groupby("channel")["date"].nunique().to_dict(),
            "daily_cpa_non_null_by_channel": prepared.groupby("channel")["cpa"].count().to_dict(),
        }
    )
    (OUTPUTS / "data_quality_summary.json").write_text(
        json.dumps(quality, indent=2) + "\n", encoding="utf-8"
    )
    plot_overview(summary)
    plot_distributions(prepared)
    print("Prepared data:", PREPARED)
    print(summary.round(4).to_string(index=False))
    print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    main()

