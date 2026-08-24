"""Step 1 - pull the two source datasets from Hugging Face.

Primary: criteo/criteo-attribution-dataset. Real ad-serving logs from Criteo's
production systems, 16.5M impressions over 30 days, ungated. Carries `campaign`,
`click`, `conversion` and `cost`, which is what makes CPA and conversion-rate
comparisons possible on genuine observational data. Streamed rather than
downloaded: the full file is ~800MB and the analysis needs a slice, not all of it.

Secondary: jason1966/alinaboulsi_digital-marketing-performance-dataset. Used for
one thing only - ROAS by platform - because it carries a `revenue` column and the
Criteo release does not. It is SYNTHETIC by its own documentation and is labelled
as such everywhere it appears.

Run:  python fetch_dataset.py [--rows 400000]

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import argparse
import itertools
import sys
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

CRITEO = "criteo/criteo-attribution-dataset"
SYNTH = "jason1966/alinaboulsi_digital-marketing-performance-dataset"
SYNTH_FILE = "digital_marketing_dataset_30k.csv"

KEEP = ["timestamp", "campaign", "conversion", "click", "cost", "cpo",
        "attribution", "click_pos", "click_nb"]


def fetch_criteo(n_rows: int) -> pd.DataFrame:
    from datasets import load_dataset

    print(f"streaming {n_rows:,} rows from {CRITEO} ...")
    ds = load_dataset(CRITEO, split="train", streaming=True)
    rows = list(itertools.islice(ds, n_rows))
    df = pd.DataFrame(rows)[KEEP]
    print(f"  got {len(df):,} rows x {df.shape[1]} columns")
    return df


def fetch_synthetic() -> pd.DataFrame:
    url = f"https://huggingface.co/datasets/{SYNTH}/resolve/main/{SYNTH_FILE}"
    out = DATA / "synthetic_platform_performance.csv"
    if not out.exists():
        print(f"downloading {SYNTH_FILE} ...")
        urllib.request.urlretrieve(url, out)
    df = pd.read_csv(out)
    print(f"  synthetic set: {len(df):,} rows x {df.shape[1]} columns")
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rows", type=int, default=400_000,
                    help="impressions to stream from the Criteo set")
    args = ap.parse_args()

    df = fetch_criteo(args.rows)

    # Cheap integrity checks before anything downstream trusts this.
    problems = []
    if df["conversion"].dropna().isin([0, 1]).all() is False:
        problems.append("conversion is not strictly binary")
    if (df["cost"] < 0).any():
        problems.append("negative cost values present")
    if df["campaign"].nunique() < 5:
        problems.append(f"only {df['campaign'].nunique()} campaigns in the slice")
    if problems:
        print("\nINTEGRITY PROBLEMS:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    out = DATA / "criteo_attribution_sample.csv"
    df.to_csv(out, index=False)
    print(f"\nwritten: {out.name}")
    print(f"  campaigns           {df['campaign'].nunique():,}")
    print(f"  impressions         {len(df):,}")
    print(f"  clicks              {int(df['click'].sum()):,}")
    print(f"  conversions         {int(df['conversion'].sum()):,}")
    print(f"  overall CVR         {df['conversion'].mean():.4%}")
    print(f"  cost column range   {df['cost'].min():.6g} to {df['cost'].max():.6g}")

    fetch_synthetic()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
