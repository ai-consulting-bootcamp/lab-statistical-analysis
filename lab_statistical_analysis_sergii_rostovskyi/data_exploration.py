from pathlib import Path
import argparse
from hashlib import file_digest
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TABLES = ROOT / "tables"
FIGURES = ROOT / "figures"
SECONDS_PER_DAY = 86_400
GROUP_COUNT = 7
COLORS = ["#287271", "#bd7950", "#4c658a", "#9c5a83", "#6f7e49", "#587f99", "#8d6c4a"]
SOURCE_COLUMNS = [
    "timestamp", "campaign", "conversion", "conversion_timestamp",
    "conversion_id", "attribution", "click", "cost",
]
SOURCE_SHA256 = "94ac7a465564349bc7ba008602211d5990a3c53cc133abc0aadef61ea2391a98"
COUNT_COLUMNS = ["impressions", "clicks", "conversions"]


def ratio(numerator, denominator):
    return numerator / denominator.where(denominator > 0)


def add_metrics(frame):
    return frame.assign(
        ctr=ratio(frame["clicks"], frame["impressions"]),
        conversion_rate=ratio(frame["conversions"], frame["clicks"]),
        cpa=ratio(frame["cost"], frame["conversions"]),
    )


def prepare_data(archive):
    days = []
    candidates = []
    with archive.open("rb") as stream:
        source_hash = file_digest(stream, "sha256").hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError("Source SHA-256 does not match the published Hugging Face archive.")
    header = pd.read_csv(archive, sep="\t", compression="gzip", nrows=0)
    audit = {
        "source_sha256": source_hash, "source_rows": 0, "source_columns": header.columns.tolist(),
        "selected_column_dtypes": {},
        "missing_by_column": dict.fromkeys(SOURCE_COLUMNS, 0),
        "binary_flag_violations": 0, "invalid_base_rows": 0,
        "attributed_clicked_rows_with_invalid_conversion_metadata": 0,
        "maximum_timestamp": 0,
    }
    for chunk in pd.read_csv(
        archive, sep="\t", compression="gzip", usecols=SOURCE_COLUMNS, chunksize=500_000
    ):
        if not audit["source_rows"]:
            audit["selected_column_dtypes"] = chunk.dtypes.astype(str).to_dict()
            print("Source preview\n", chunk.head().to_string(index=False), sep="")
        audit["source_rows"] += len(chunk)
        missing = chunk.isna().sum()
        for column in SOURCE_COLUMNS:
            audit["missing_by_column"][column] += int(missing[column])

        binary = chunk[["click", "conversion", "attribution"]].isin([0, 1]).all(axis=1)
        valid = binary & chunk["timestamp"].ge(0) & chunk["campaign"].ge(0)
        valid &= chunk["cost"].ge(0) & np.isfinite(chunk["cost"])
        audit["binary_flag_violations"] += int((~binary).sum())
        audit["invalid_base_rows"] += int((~valid).sum())
        chunk = chunk.loc[valid].copy()
        audit["maximum_timestamp"] = max(audit["maximum_timestamp"], int(chunk["timestamp"].max()))
        chunk["day"] = chunk["timestamp"] // SECONDS_PER_DAY
        days.append(chunk.groupby(["campaign", "day"]).agg(
            impressions=("click", "size"), clicks=("click", "sum"), cost=("cost", "sum")
        ))
        attributed_click = chunk["click"].eq(1) & chunk["attribution"].eq(1) & chunk["conversion"].eq(1)
        valid_metadata = chunk["conversion_id"].ge(0) & chunk["conversion_timestamp"].ge(chunk["timestamp"])
        audit["attributed_clicked_rows_with_invalid_conversion_metadata"] += int(
            (attributed_click & ~valid_metadata).sum()
        )
        candidates.append(chunk.loc[attributed_click & valid_metadata, [
            "conversion_id", "timestamp", "campaign", "day"
        ]])

    daily = pd.concat(days).groupby(level=["campaign", "day"]).sum()
    clicks = pd.concat(candidates, ignore_index=True)
    # Count each attributed conversion once, at the most recent eligible click.
    latest = clicks.loc[clicks["timestamp"].eq(clicks.groupby("conversion_id")["timestamp"].transform("max"))]
    ambiguous = latest.groupby("conversion_id")["campaign"].nunique().gt(1)
    credited = latest.loc[~latest["conversion_id"].isin(ambiguous[ambiguous].index)]
    credited = credited.drop_duplicates("conversion_id")
    daily["conversions"] = credited.groupby(["campaign", "day"]).size().reindex(daily.index, fill_value=0)
    daily = daily.reset_index()

    last_day, last_day_seconds = divmod(audit["maximum_timestamp"], SECONDS_PER_DAY)
    full_days = daily.loc[daily["day"].lt(last_day)].copy()
    coverage = full_days.groupby("campaign").agg(days=("day", "size"), impressions=("impressions", "sum"))
    campaigns = coverage.loc[coverage["days"].eq(last_day)].sort_values(
        "impressions", ascending=False, kind="stable"
    ).head(GROUP_COUNT).index
    if len(campaigns) != GROUP_COUNT:
        raise ValueError("The source has fewer than seven campaigns with full day coverage.")
    result = full_days.loc[full_days["campaign"].isin(campaigns)].reset_index(drop=True)
    result[["campaign", "day", *COUNT_COLUMNS]] = result[["campaign", "day", *COUNT_COLUMNS]].astype("int64")
    if not (result["conversions"].le(result["clicks"]) & result["clicks"].le(result["impressions"])).all():
        raise ValueError("Conversion and click counts must fit their denominators.")
    audit.update({
        "source_campaigns": int(daily["campaign"].nunique()),
        "eligible_attributed_clicked_rows": len(clicks),
        "unique_credited_conversions": len(credited),
        "ambiguous_conversion_ids_excluded": int(ambiguous.sum()),
        "excluded_final_day": last_day,
        "elapsed_seconds_in_final_day": last_day_seconds,
        "included_days": int(last_day),
        "selected_campaigns_by_impressions": campaigns.astype(int).tolist(),
        "aggregated_rows": len(result),
    })
    prepared = add_metrics(result)
    prepared.to_csv(DATA / "marketing_data.csv", index=False)
    (DATA / "data_quality.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return prepared


def save_plot(fig, filename):
    fig.savefig(FIGURES / filename, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_metrics(daily, summary):
    labels = summary["campaign"].astype(str)
    palette = dict(zip(labels, COLORS, strict=True))
    fig, axes = plt.subplots(2, 3, figsize=(13.6, 7.5), layout="constrained")
    specs = [
        ("cpa", 1, "Cost per acquisition", "Transformed cost units"),
        ("conversion_rate", 100, "Attributed post-click conversion rate", "% of clicks"),
        ("conversions", 1, "Credited conversions", "Conversions"),
        ("cost", 1, "Total display cost", "Transformed cost units"),
        ("ctr", 100, "Click-through rate", "% of impressions"),
        ("impressions", 1e-6, "Impressions", "Millions of impressions"),
    ]
    for ax, (column, scale, title, xlabel) in zip(axes.flat, specs, strict=True):
        ax.barh(labels, summary[column] * scale, color=[palette[label] for label in labels])
        ax.invert_yaxis()
        ax.set(title=title, xlabel=xlabel, ylabel="Campaign")
        ax.grid(axis="y", visible=False)
    fig.suptitle("Campaign totals and weighted performance", fontsize=16, fontweight="bold")
    save_plot(fig, "group_metrics_overview.png")

    plotted = daily.assign(campaign=daily["campaign"].astype(str), rate_pct=daily["conversion_rate"] * 100)
    fig, axes = plt.subplots(2, 2, figsize=(13.6, 8.4), layout="constrained")
    for row, (column, xlabel) in enumerate([
        ("cpa", "Daily CPA (transformed cost units)"), ("rate_pct", "Daily post-click conversion rate (%)")
    ]):
        sns.histplot(data=plotted, x=column, hue="campaign", hue_order=list(labels), palette=palette,
                     bins=25, element="step", fill=True, alpha=0.14, ax=axes[row, 0])
        sns.boxplot(data=plotted, x=column, y="campaign", hue="campaign", order=list(labels),
                    palette=palette, legend=False, ax=axes[row, 1], fliersize=3)
        axes[row, 0].set(xlabel=xlabel, ylabel="Campaign-days")
        axes[row, 1].set(xlabel=xlabel, ylabel="Campaign")
    fig.suptitle("Day-to-day variability by campaign", fontsize=16, fontweight="bold")
    save_plot(fig, "group_distributions.png")


def main():
    parser = argparse.ArgumentParser(description="Explore campaign performance and export daily summaries.")
    parser.add_argument("--raw", type=Path, help="Optional Criteo TSV.GZ archive for rebuilding the daily CSV.")
    args = parser.parse_args()
    for directory in [DATA, TABLES, FIGURES]:
        directory.mkdir(exist_ok=True)
    if args.raw:
        daily = prepare_data(args.raw)
    else:
        daily = pd.read_csv(DATA / "marketing_data.csv")
    print(f"Prepared shape: {daily.shape}; days {daily['day'].min()}–{daily['day'].max()}")
    print(daily.dtypes.to_string())
    print(daily.head().to_string(index=False))
    print("Missing values after preparation")
    print(daily.isna().sum().to_string())
    totals = daily.groupby("campaign").agg(
        days=("day", "size"), impressions=("impressions", "sum"), clicks=("clicks", "sum"),
        conversions=("conversions", "sum"), cost=("cost", "sum")
    )
    summary = add_metrics(totals).reset_index()
    summary.to_csv(TABLES / "group_metrics.csv", index=False)
    print("\nCampaign metrics (rates in %)")
    print(summary.assign(ctr=summary["ctr"] * 100,
                         conversion_rate=summary["conversion_rate"] * 100).round(2).to_string(index=False))
    variability = daily.groupby("campaign")[["cpa", "conversion_rate"]].agg([
        "count", "mean", "std", "median", "min", "max",
    ])
    variability.columns = ["_".join(col) for col in variability.columns]
    for metric in ["cpa", "conversion_rate"]:
        grouped = daily.groupby("campaign")[metric]
        q1, q3 = grouped.quantile(0.25), grouped.quantile(0.75)
        iqr = q3 - q1
        variability[f"{metric}_iqr"] = iqr
        lower = daily["campaign"].map(q1 - 1.5 * iqr)
        upper = daily["campaign"].map(q3 + 1.5 * iqr)
        flagged = ~daily[metric].between(lower, upper) & daily[metric].notna()
        variability[f"{metric}_tukey_outlier_days"] = flagged.groupby(daily["campaign"]).sum()
    variability.to_csv(TABLES / "group_variability.csv")
    print("\nDaily distributions\n", variability.round(4).to_string(), sep="")
    sns.set_theme(style="whitegrid", context="notebook")
    plot_metrics(daily, summary)


if __name__ == "__main__":
    main()
