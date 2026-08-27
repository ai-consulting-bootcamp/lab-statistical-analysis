"""Shared, deterministic helpers for the paid-search marketing lab."""

from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd


MONTH_ORDER = ["July", "August", "September", "October", "November"]
MATCH_ORDER = ["One-to-one", "Exact", "Phrase"]
DEVICE_ORDER = ["Desktop", "Mobile"]


def project_root(start: str | Path | None = None) -> Path:
    """Find the repository root from either the root or notebooks directory."""
    current = Path(start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "data" / "shopping_mall_paid_search.csv").exists():
            return candidate
    raise FileNotFoundError("Could not locate data/shopping_mall_paid_search.csv")


def safe_divide(numerator, denominator):
    """Divide while returning NaN for zero denominators."""
    numerator = pd.Series(numerator, copy=False, dtype="float64")
    denominator = pd.Series(denominator, copy=False, dtype="float64")
    return numerator.div(denominator.where(denominator.ne(0)))


def _intent_family(ad_group: str) -> str:
    term = ad_group.split(" - ")[-1].strip("[] ").lower()
    rules = [
        ("Black Friday / Cyber Monday", r"black friday|cyber monday"),
        ("Competitor", r"competitor"),
        ("Free Shipping", r"free shipping"),
        ("Coupon", r"coupon"),
        ("Discount", r"discount"),
        ("Promo", r"promo"),
        ("Offer", r"offer"),
        ("Sale", r"sale"),
    ]
    for label, pattern in rules:
        if re.search(pattern, term):
            return label
    return "Other"


def prepare_data(path: str | Path) -> pd.DataFrame:
    """Load the source file, normalize fields, parse structural groups, and recalculate KPIs."""
    raw = pd.read_csv(path)
    rename = {
        "Ad Group": "ad_group",
        "Month": "month",
        "Impressions": "impressions",
        "Clicks": "clicks",
        "CTR": "source_ctr",
        "Conversions": "conversions",
        "Conv Rate": "source_conversion_rate",
        "Cost": "cost",
        "CPC": "source_cpc",
        "Revenue": "revenue",
        "Sale Amount": "sale_amount",
        "P&L": "source_p_and_l",
    }
    df = raw.rename(columns=rename).copy()
    df["month"] = pd.Categorical(df["month"], MONTH_ORDER, ordered=True)
    df["device"] = np.select(
        [df["ad_group"].str.contains(" - Desk - "), df["ad_group"].str.contains(" - Mob - ")],
        ["Desktop", "Mobile"],
        default="Unknown",
    )
    df["match_type"] = np.select(
        [
            df["ad_group"].str.contains(" - 1:1 - ", regex=False),
            df["ad_group"].str.contains(" - Exact - ", regex=False),
            df["ad_group"].str.contains(" - Phrase - ", regex=False),
        ],
        MATCH_ORDER,
        default="Unknown",
    )
    df["intent_family"] = df["ad_group"].map(_intent_family)

    df["ctr"] = safe_divide(df["clicks"], df["impressions"])
    df["conversion_rate"] = safe_divide(df["conversions"], df["clicks"])
    df["cpc"] = safe_divide(df["cost"], df["clicks"])
    df["cpa"] = safe_divide(df["cost"], df["conversions"])
    df["roas"] = safe_divide(df["revenue"], df["cost"])
    df["profit"] = df["revenue"] - df["cost"]
    df["roi"] = safe_divide(df["profit"], df["cost"])
    df["profit_margin"] = safe_divide(df["profit"], df["revenue"])
    df["revenue_per_conversion"] = safe_divide(df["revenue"], df["conversions"])
    df["profit_per_conversion"] = safe_divide(df["profit"], df["conversions"])
    return df


def quality_checks(raw: pd.DataFrame, prepared: pd.DataFrame) -> pd.DataFrame:
    """Return explicit data-quality and source-metric reconciliation checks."""
    numeric_nonnegative = [
        "impressions", "clicks", "conversions", "cost", "revenue", "sale_amount"
    ]
    checks = [
        ("rows", len(prepared), 190, len(prepared) == 190),
        ("columns_source", raw.shape[1], 12, raw.shape[1] == 12),
        ("missing_cells", int(raw.isna().sum().sum()), 0, not raw.isna().any().any()),
        ("exact_duplicate_rows", int(raw.duplicated().sum()), 0, not raw.duplicated().any()),
        (
            "duplicate_ad_group_month_keys",
            int(prepared.duplicated(["ad_group", "month"]).sum()),
            0,
            not prepared.duplicated(["ad_group", "month"]).any(),
        ),
        ("clicks_gt_impressions", int((prepared["clicks"] > prepared["impressions"]).sum()), 0,
         not (prepared["clicks"] > prepared["impressions"]).any()),
        ("conversions_gt_clicks", int((prepared["conversions"] > prepared["clicks"]).sum()), 0,
         not (prepared["conversions"] > prepared["clicks"]).any()),
        ("negative_input_values", int((prepared[numeric_nonnegative] < 0).sum().sum()), 0,
         not (prepared[numeric_nonnegative] < 0).any().any()),
        ("zero_impressions", int((prepared["impressions"] == 0).sum()), 0,
         not (prepared["impressions"] == 0).any()),
        ("zero_clicks", int((prepared["clicks"] == 0).sum()), 0,
         not (prepared["clicks"] == 0).any()),
        ("zero_conversions", int((prepared["conversions"] == 0).sum()), "allowed; ratio becomes NaN", True),
        ("zero_cost", int((prepared["cost"] == 0).sum()), 0,
         not (prepared["cost"] == 0).any()),
        ("zero_revenue", int((prepared["revenue"] == 0).sum()), "allowed; margin becomes NaN", True),
        ("unknown_device", int((prepared["device"] == "Unknown").sum()), 0,
         not (prepared["device"] == "Unknown").any()),
        ("unknown_match_type", int((prepared["match_type"] == "Unknown").sum()), 0,
         not (prepared["match_type"] == "Unknown").any()),
        (
            "source_ctr_diff_gt_0.0051",
            int(((prepared["source_ctr"] - prepared["ctr"]).abs() > 0.0051).sum()),
            0,
            int(((prepared["source_ctr"] - prepared["ctr"]).abs() > 0.0051).sum()) == 0,
        ),
        (
            "source_conversion_rate_diff_gt_0.0051",
            int(((prepared["source_conversion_rate"] - prepared["conversion_rate"]).abs() > 0.0051).sum()),
            0,
            int(((prepared["source_conversion_rate"] - prepared["conversion_rate"]).abs() > 0.0051).sum()) == 0,
        ),
        (
            "source_cpc_diff_gt_0.011",
            int(((prepared["source_cpc"] - prepared["cpc"]).abs() > 0.011).sum()),
            0,
            int(((prepared["source_cpc"] - prepared["cpc"]).abs() > 0.011).sum()) == 0,
        ),
        (
            "source_p_and_l_diff_gt_0.51",
            int(((prepared["source_p_and_l"] - prepared["profit"]).abs() > 0.51).sum()),
            0,
            int(((prepared["source_p_and_l"] - prepared["profit"]).abs() > 0.51).sum()) == 0,
        ),
    ]
    return pd.DataFrame(checks, columns=["check", "observed", "expected", "passed"])


def aggregate_performance(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """Aggregate counts first, then calculate weighted funnel and unit-economics KPIs."""
    summary = (
        df.groupby(group, observed=True)
        .agg(
            observations=("ad_group", "size"),
            ad_groups=("ad_group", "nunique"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            cost=("cost", "sum"),
            revenue=("revenue", "sum"),
            sale_amount=("sale_amount", "sum"),
        )
        .reset_index()
    )
    summary["ctr"] = safe_divide(summary["clicks"], summary["impressions"])
    summary["conversion_rate"] = safe_divide(summary["conversions"], summary["clicks"])
    summary["cpc"] = safe_divide(summary["cost"], summary["clicks"])
    summary["cpa"] = safe_divide(summary["cost"], summary["conversions"])
    summary["revenue_per_conversion"] = safe_divide(summary["revenue"], summary["conversions"])
    summary["profit"] = summary["revenue"] - summary["cost"]
    summary["profit_per_conversion"] = safe_divide(summary["profit"], summary["conversions"])
    summary["roas"] = safe_divide(summary["revenue"], summary["cost"])
    summary["roi"] = safe_divide(summary["profit"], summary["cost"])
    summary["profit_margin"] = safe_divide(summary["profit"], summary["revenue"])
    if group == "match_type":
        summary[group] = pd.Categorical(summary[group], MATCH_ORDER, ordered=True)
        summary = summary.sort_values(group).reset_index(drop=True)
    if group == "device":
        summary[group] = pd.Categorical(summary[group], DEVICE_ORDER, ordered=True)
        summary = summary.sort_values(group).reset_index(drop=True)
    return summary


def benjamini_hochberg(p_values) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values in original order."""
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * len(p) / np.arange(1, len(p) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    result = np.empty_like(adjusted)
    result[order] = np.clip(adjusted, 0, 1)
    return result


def bounded_allocation(raw_weights, lower=0.20, upper=0.40) -> np.ndarray:
    """Project positive weights to a simplex with lower/upper concentration guards."""
    weights = np.asarray(raw_weights, dtype=float)
    weights = weights / weights.sum()
    for _ in range(100):
        low = weights < lower
        high = weights > upper
        if not (low.any() or high.any()):
            break
        weights[low] = lower
        weights[high] = upper
        free = ~(low | high)
        remaining = 1 - weights[~free].sum()
        if free.any():
            base = weights[free]
            weights[free] = remaining * base / base.sum()
    return weights / weights.sum()


def budget_recommendation(summary: pd.DataFrame, budget: int = 500_000) -> pd.DataFrame:
    """Create a score-based, guardrailed historical allocation scenario."""
    s = summary.copy()
    # Efficiency and profitability dominate; volume contributes confidence but cannot dominate allocation.
    efficiency = 1 - s["cpa"].rank(method="average", pct=True) + 1 / len(s)
    profitability = s["roas"].rank(method="average", pct=True)
    reliability = np.sqrt(s["conversions"]) / np.sqrt(s["conversions"]).sum()
    raw_score = 0.40 * efficiency + 0.40 * profitability + 0.20 * reliability
    shares = bounded_allocation(raw_score.to_numpy(), lower=0.20, upper=0.40)
    dollars = np.round(shares * budget / 1000) * 1000
    remainder = int(budget - dollars.sum())
    if remainder:
        capacity = upper * budget - dollars
        eligible = np.where(capacity >= remainder)[0]
        target = eligible[np.argmax(shares[eligible])] if len(eligible) else np.argmax(capacity)
        dollars[target] += remainder
    s["allocation"] = dollars.astype(int)
    s["allocation_pct"] = s["allocation"] / budget
    s["historical_cost_share"] = s["cost"] / s["cost"].sum()
    s["projected_clicks_base"] = s["allocation"] / s["cpc"]
    s["projected_conversions_base"] = s["projected_clicks_base"] * s["conversion_rate"]
    s["projected_revenue_base"] = s["projected_conversions_base"] * s["revenue_per_conversion"]
    s["projected_profit_base"] = s["projected_revenue_base"] - s["allocation"]
    s["justification"] = np.select(
        [s["match_type"] == "One-to-one", s["match_type"] == "Exact"],
        [
            "Best historical CPA/ROAS and largest evidence base; capped because historical ROI is negative.",
            "Middle efficiency with diversified query coverage; fund controlled optimisation rather than expansion.",
        ],
        default="Weakest historical CPA/ROAS; retain a guarded learning budget while reducing exposure.",
    )
    s["principal_risk"] = "All groups had negative historical ROI; observational ratios may not persist."
    return s


def sensitivity_scenarios(allocation: pd.DataFrame) -> pd.DataFrame:
    """Apply transparent CPC/CVR/revenue-per-conversion sensitivity multipliers."""
    scenarios = [
        ("Downside", 1.10, 0.90, 0.90),
        ("Base", 1.00, 1.00, 1.00),
        ("Upside", 0.90, 1.10, 1.10),
    ]
    rows = []
    for name, cpc_mult, cvr_mult, rpc_mult in scenarios:
        spend = allocation["allocation"].sum()
        clicks = (allocation["allocation"] / (allocation["cpc"] * cpc_mult)).sum()
        conversions = (
            allocation["allocation"] / (allocation["cpc"] * cpc_mult)
            * allocation["conversion_rate"] * cvr_mult
        ).sum()
        revenue = (
            allocation["allocation"] / (allocation["cpc"] * cpc_mult)
            * allocation["conversion_rate"] * cvr_mult
            * allocation["revenue_per_conversion"] * rpc_mult
        ).sum()
        rows.append(
            {
                "scenario": name,
                "cpc_multiplier": cpc_mult,
                "conversion_rate_multiplier": cvr_mult,
                "revenue_per_conversion_multiplier": rpc_mult,
                "budget": spend,
                "estimated_clicks": clicks,
                "estimated_conversions": conversions,
                "estimated_revenue": revenue,
                "estimated_profit": revenue - spend,
                "estimated_roas": revenue / spend,
            }
        )
    return pd.DataFrame(rows)
