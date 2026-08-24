"""Shared loading, cleaning and metric definitions.

One definition of the groups and the metrics, imported by every script, so the
exploration, the tests and the power analysis cannot drift apart.

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGURES = HERE / "figures"
FIGURES.mkdir(exist_ok=True)

CRITEO_CSV = DATA / "criteo_attribution_sample.csv"
SYNTH_CSV = DATA / "synthetic_platform_performance.csv"

# Campaigns are anonymised integers in the Criteo release. Readable labels keep
# the charts and the memo legible without inventing anything about them.
N_GROUPS = 6


def load_criteo() -> pd.DataFrame:
    if not CRITEO_CSV.exists():
        raise SystemExit(f"{CRITEO_CSV.name} missing - run fetch_dataset.py first")
    df = pd.read_csv(CRITEO_CSV)

    # Cleaning. The release uses -1 as a null marker on the click/conversion
    # position fields; the columns this analysis uses carry no such marker.
    before = len(df)
    df = df.dropna(subset=["campaign", "conversion", "click", "cost"])
    df = df[(df["cost"] >= 0) & df["conversion"].isin([0, 1]) & df["click"].isin([0, 1])]
    dropped = before - len(df)
    df.attrs["rows_dropped"] = dropped
    return df


def top_campaigns(df: pd.DataFrame, n: int = N_GROUPS) -> list:
    return df["campaign"].value_counts().head(n).index.tolist()


def label_map(campaigns: list) -> dict:
    return {c: f"Campaign {chr(65 + i)}" for i, c in enumerate(campaigns)}


def analysis_frame(df: pd.DataFrame, n: int = N_GROUPS) -> pd.DataFrame:
    """The rows used for every comparison: the n largest campaigns, labelled."""
    camps = top_campaigns(df, n)
    out = df[df["campaign"].isin(camps)].copy()
    out["group"] = out["campaign"].map(label_map(camps))
    return out


def group_summary(sub: pd.DataFrame) -> pd.DataFrame:
    """Per-campaign performance table.

    CPA and CTR/CVR are ratios of totals, which is how a marketer reads them.
    `cost_per_impression` is the per-row measurement the t-tests use.
    """
    g = sub.groupby("group").agg(
        impressions=("conversion", "size"),
        clicks=("click", "sum"),
        conversions=("conversion", "sum"),
        total_cost=("cost", "sum"),
        cost_per_impression=("cost", "mean"),
    )
    g["ctr_pct"] = g["clicks"] / g["impressions"] * 100
    g["cvr_pct"] = g["conversions"] / g["impressions"] * 100
    g["cpa"] = np.where(g["conversions"] > 0, g["total_cost"] / g["conversions"], np.nan)
    return g.sort_values("impressions", ascending=False)


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion.

    Used rather than the normal approximation because conversion rates here are
    a few percent, where the normal interval misbehaves.
    """
    if n == 0:
        return (np.nan, np.nan)
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's d with a pooled standard deviation."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return np.nan
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    return (a.mean() - b.mean()) / pooled if pooled > 0 else np.nan


def interpret_d(d: float) -> str:
    a = abs(d)
    if np.isnan(a):
        return "n/a"
    if a < 0.2:
        return "negligible"
    if a < 0.5:
        return "small"
    if a < 0.8:
        return "medium"
    return "large"


def load_synthetic() -> pd.DataFrame:
    """The secondary, SYNTHETIC set. Used only for ROAS, which the Criteo
    release cannot support because it carries no revenue column."""
    if not SYNTH_CSV.exists():
        raise SystemExit(f"{SYNTH_CSV.name} missing - run fetch_dataset.py first")
    df = pd.read_csv(SYNTH_CSV)
    df = df[(df["spend"] > 0)]
    return df
