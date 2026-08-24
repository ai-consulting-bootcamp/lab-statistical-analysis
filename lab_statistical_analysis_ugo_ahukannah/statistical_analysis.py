"""Parts 2 and 3 - pairwise comparisons, effect sizes, multiple-comparisons correction.

Steps 4, 5 and 6.

Two families of tests, because the two metrics are different kinds of thing:

  cost per impression   continuous, heavily right-skewed  -> Welch's t-test + Cohen's d
  conversion             binary                            -> Fisher's exact test on a 2x2

Both families get Bonferroni and Benjamini-Hochberg correction, applied WITHIN
each family. Correcting across both together would be wrong: they answer
different questions and a marketer acts on them separately.

A note on what is deliberately NOT tested. The release also carries `cpo`
(cost per order), which looks like an attractive continuous outcome. It is not
used, because within a single campaign it takes only 8 to 510 distinct values
across thousands of rows - it is a campaign-period attribute repeated down the
rows, not an independent per-impression measurement. Running a t-test on it
would treat a few dozen real observations as tens of thousands and manufacture
significance. `cost` genuinely varies per impression (4,000-10,000 distinct
values per campaign) and is used instead.

Run:  python statistical_analysis.py

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import itertools
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from marketing_data import (FIGURES, HERE, analysis_frame, cohens_d, group_summary,
                            interpret_d, load_criteo, wilson_ci)

ALPHA = 0.05


def ttest_pairs(sub: pd.DataFrame) -> pd.DataFrame:
    """Welch's t-test on cost per impression, every campaign pair."""
    groups = sorted(sub["group"].unique())
    rows = []
    for a, b in itertools.combinations(groups, 2):
        xa = sub.loc[sub["group"] == a, "cost"].values
        xb = sub.loc[sub["group"] == b, "cost"].values
        t, p = stats.ttest_ind(xa, xb, equal_var=False)   # Welch: unequal variances
        d = cohens_d(xa, xb)
        rows.append({
            "group_a": a, "group_b": b,
            "n_a": len(xa), "n_b": len(xb),
            "mean_a": xa.mean(), "mean_b": xb.mean(),
            "diff": xa.mean() - xb.mean(),
            "pct_diff": (xa.mean() - xb.mean()) / xb.mean() * 100 if xb.mean() else np.nan,
            "t_stat": t, "p_raw": p,
            "cohens_d": d, "effect": interpret_d(d),
        })
    return pd.DataFrame(rows)


def fisher_pairs(sub: pd.DataFrame) -> pd.DataFrame:
    """Fisher's exact test on conversion, every campaign pair."""
    groups = sorted(sub["group"].unique())
    rows = []
    for a, b in itertools.combinations(groups, 2):
        sa = sub[sub["group"] == a]; sb = sub[sub["group"] == b]
        ca, na = int(sa["conversion"].sum()), len(sa)
        cb, nb = int(sb["conversion"].sum()), len(sb)
        table = [[ca, na - ca], [cb, nb - cb]]
        odds, p = stats.fisher_exact(table)
        lo_a, hi_a = wilson_ci(ca, na)
        lo_b, hi_b = wilson_ci(cb, nb)
        rows.append({
            "group_a": a, "group_b": b,
            "conv_a": ca, "n_a": na, "cvr_a_pct": ca / na * 100,
            "conv_b": cb, "n_b": nb, "cvr_b_pct": cb / nb * 100,
            "cvr_a_ci": f"[{lo_a*100:.2f}, {hi_a*100:.2f}]",
            "cvr_b_ci": f"[{lo_b*100:.2f}, {hi_b*100:.2f}]",
            "abs_diff_pp": (ca / na - cb / nb) * 100,
            "relative_lift_pct": ((ca / na) / (cb / nb) - 1) * 100 if cb else np.nan,
            "odds_ratio": odds, "p_raw": p,
        })
    return pd.DataFrame(rows)


def correct(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Bonferroni and Benjamini-Hochberg, applied within one family."""
    p = df["p_raw"].values
    bonf_rej, bonf_p, _, _ = multipletests(p, alpha=ALPHA, method="bonferroni")
    bh_rej, bh_p, _, _ = multipletests(p, alpha=ALPHA, method="fdr_bh")
    out = df.copy()
    out["sig_raw"] = p < ALPHA
    out["p_bonferroni"] = bonf_p
    out["sig_bonferroni"] = bonf_rej
    out["p_bh"] = bh_p
    out["sig_bh"] = bh_rej
    print(f"\n{label}: {len(p)} comparisons at alpha={ALPHA}")
    print(f"  significant uncorrected      {out['sig_raw'].sum():>3}/{len(p)}")
    print(f"  significant after Bonferroni {out['sig_bonferroni'].sum():>3}/{len(p)}"
          f"   (threshold {ALPHA/len(p):.5f})")
    print(f"  significant after BH (FDR)   {out['sig_bh'].sum():>3}/{len(p)}")
    lost_b = int(out["sig_raw"].sum() - out["sig_bonferroni"].sum())
    lost_h = int(out["sig_raw"].sum() - out["sig_bh"].sum())
    print(f"  results withdrawn by Bonferroni {lost_b}, by BH {lost_h}")
    return out


def heatmap(res: pd.DataFrame, value: str, title: str, fname: str,
            fmt: str = "{:.3f}", cmap: str = "RdYlGn_r") -> None:
    groups = sorted(set(res["group_a"]) | set(res["group_b"]))
    m = pd.DataFrame(np.nan, index=groups, columns=groups)
    for r in res.itertuples():
        m.loc[r.group_a, r.group_b] = getattr(r, value)
        m.loc[r.group_b, r.group_a] = getattr(r, value)
    fig, ax = plt.subplots(figsize=(7.6, 6))
    im = ax.imshow(m.values.astype(float), cmap=cmap)
    ax.set_xticks(range(len(groups))); ax.set_xticklabels([g.replace("Campaign ", "") for g in groups])
    ax.set_yticks(range(len(groups))); ax.set_yticklabels([g.replace("Campaign ", "") for g in groups])
    for i in range(len(groups)):
        for j in range(len(groups)):
            v = m.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=8.5)
    ax.set_title(title, fontweight="bold", fontsize=11)
    fig.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout(); plt.savefig(FIGURES / fname, dpi=150, bbox_inches="tight"); plt.close()


def correction_chart(tt: pd.DataFrame, fi: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    labels = ["uncorrected", "Benjamini-Hochberg", "Bonferroni"]
    tvals = [tt["sig_raw"].sum(), tt["sig_bh"].sum(), tt["sig_bonferroni"].sum()]
    fvals = [fi["sig_raw"].sum(), fi["sig_bh"].sum(), fi["sig_bonferroni"].sum()]
    x = np.arange(len(labels)); w = 0.36
    ax.bar(x - w/2, tvals, w, label=f"cost per impression (t-test, n={len(tt)})", color="#1565c0")
    ax.bar(x + w/2, fvals, w, label=f"conversion (Fisher, n={len(fi)})", color="#2e7d32")
    for i, (a, b) in enumerate(zip(tvals, fvals)):
        ax.text(i - w/2, a + 0.15, str(a), ha="center", fontsize=9)
        ax.text(i + w/2, b + 0.15, str(b), ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("significant comparisons")
    ax.set_title("What multiple-comparisons correction removes", fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig(FIGURES / "correction_effect.png", dpi=150, bbox_inches="tight"); plt.close()




# --------------------------------------------------------------------------
# CPA - compared by bootstrap, because it is a ratio of totals
# --------------------------------------------------------------------------

def _cpa_bootstrap(cost: np.ndarray, conv: np.ndarray, b: int, rng) -> np.ndarray:
    """Sampling distribution of CPA = total cost / total conversions.

    CPA has no per-impression value - most impressions convert zero times - so
    there is nothing to feed a t-test. Resampling impressions within a campaign
    and recomputing the ratio each time gives its sampling distribution directly,
    which is the standard way to put an interval on a ratio of totals.
    """
    n = len(cost)
    out = np.empty(b)
    for i in range(b):
        idx = rng.integers(0, n, n)
        c = conv[idx].sum()
        out[i] = cost[idx].sum() / c if c > 0 else np.nan
    return out


def cpa_pairs(sub: pd.DataFrame, b: int = 2000, seed: int = 11) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-campaign CPA with a bootstrap interval, and all pairwise differences."""
    rng = np.random.default_rng(seed)
    groups = sorted(sub["group"].unique())

    dists, per_group = {}, []
    for g in groups:
        d = sub[sub["group"] == g]
        cost, conv = d["cost"].to_numpy(), d["conversion"].to_numpy()
        boot = _cpa_bootstrap(cost, conv, b, rng)
        dists[g] = boot
        point = cost.sum() / conv.sum()
        per_group.append({
            "group": g, "cpa": point,
            "cpa_ci_low": np.nanpercentile(boot, 2.5),
            "cpa_ci_high": np.nanpercentile(boot, 97.5),
            "conversions": int(conv.sum()), "impressions": len(d),
        })

    rows = []
    for a, bb in itertools.combinations(groups, 2):
        diff = dists[a] - dists[bb]
        diff = diff[~np.isnan(diff)]
        # Two-sided bootstrap p-value: how much of the difference distribution
        # sits on the wrong side of zero.
        p = 2 * min((diff <= 0).mean(), (diff >= 0).mean())
        p = min(max(p, 1.0 / len(diff)), 1.0)   # cannot resolve below 1/B
        ca = sub.loc[sub["group"] == a, "cost"].sum() / sub.loc[sub["group"] == a, "conversion"].sum()
        cb = sub.loc[sub["group"] == bb, "cost"].sum() / sub.loc[sub["group"] == bb, "conversion"].sum()
        rows.append({
            "group_a": a, "group_b": bb, "cpa_a": ca, "cpa_b": cb,
            "diff": ca - cb, "ratio": ca / cb,
            "diff_ci_low": np.percentile(diff, 2.5),
            "diff_ci_high": np.percentile(diff, 97.5),
            "p_raw": p,
        })
    return pd.DataFrame(per_group).set_index("group"), pd.DataFrame(rows)


def correction_bites_demo(sub: pd.DataFrame, seed: int = 7) -> pd.DataFrame:
    """Show the correction actually withdrawing results.

    On the full slice neither Bonferroni nor BH removes anything, because the
    p-values sit at machine zero - correction only matters when p-values are
    near the threshold. That is a true statement about this dataset, not a
    reason to skip the step, so this repeats the conversion tests on a
    subsample of 400 impressions per campaign, which is the sample size a
    realistic two-week pilot would produce. There the correction bites.
    """
    n_each = 400
    parts = [d.sample(min(n_each, len(d)), random_state=seed + i)
             for i, (_, d) in enumerate(sub.groupby("group"))]
    small = pd.concat(parts, ignore_index=True)
    fi = fisher_pairs(small)
    p = fi["p_raw"].values
    bonf_rej, bonf_p, _, _ = multipletests(p, alpha=ALPHA, method="bonferroni")
    bh_rej, bh_p, _, _ = multipletests(p, alpha=ALPHA, method="fdr_bh")
    fi["sig_raw"] = p < ALPHA
    fi["sig_bonferroni"] = bonf_rej
    fi["sig_bh"] = bh_rej

    line = "=" * 92
    print(f"\n{line}\nDOES THE CORRECTION EVER BITE? - same tests, 400 impressions per campaign"
          f"\n{line}")
    print(f"  subsample size               {len(small):,} impressions "
          f"({small['group'].nunique()} campaigns x 400)")
    print(f"  significant uncorrected      {fi['sig_raw'].sum():>3}/{len(p)}")
    print(f"  significant after BH         {fi['sig_bh'].sum():>3}/{len(p)}")
    print(f"  significant after Bonferroni {fi['sig_bonferroni'].sum():>3}/{len(p)}")
    withdrawn = fi[fi["sig_raw"] & ~fi["sig_bonferroni"]]
    print(f"  withdrawn by Bonferroni      {len(withdrawn)}")
    for r in withdrawn.itertuples():
        print(f"      {r.group_a} vs {r.group_b}: p={r.p_raw:.4f} -> "
              f"not significant at the corrected threshold {ALPHA/len(p):.5f}")
    print("\n  This is what the correction is for: at pilot scale several pairs look")
    print("  significant on their own and stop looking significant once you account")
    print("  for having asked the question fifteen times.")
    return fi


def main() -> int:
    sub = analysis_frame(load_criteo())
    g = group_summary(sub)
    line = "=" * 92
    print(f"{line}\nPAIRWISE COMPARISONS - {sub['group'].nunique()} campaigns, "
          f"{len(sub):,} impressions\n{line}")

    tt = correct(ttest_pairs(sub), "Cost per impression (Welch's t-test)")
    fi = correct(fisher_pairs(sub), "Conversion rate (Fisher's exact test)")
    cpa_g, cpa_p = cpa_pairs(sub)
    cpa_p = correct(cpa_p, "CPA (bootstrap, 2,000 resamples)")

    print(f"\n{line}\nCOST PER IMPRESSION - all pairs\n{line}")
    print(tt[["group_a", "group_b", "mean_a", "mean_b", "pct_diff", "p_raw",
              "p_bonferroni", "p_bh", "cohens_d", "effect", "sig_bh"]]
          .round(6).to_string(index=False))

    print(f"\n{line}\nCPA BY CAMPAIGN - point estimate with 95% bootstrap interval\n{line}")
    print(cpa_g.round(5).to_string())
    print(f"\n{line}\nCPA - all pairs (bootstrap)\n{line}")
    print(cpa_p[["group_a", "group_b", "cpa_a", "cpa_b", "ratio", "diff_ci_low",
                 "diff_ci_high", "p_raw", "p_bonferroni", "p_bh", "sig_bh"]]
          .round(5).to_string(index=False))

    print(f"\n{line}\nCONVERSION RATE - all pairs\n{line}")
    print(fi[["group_a", "group_b", "cvr_a_pct", "cvr_b_pct", "abs_diff_pp",
              "relative_lift_pct", "odds_ratio", "p_raw", "p_bonferroni", "p_bh", "sig_bh"]]
          .round(5).to_string(index=False))

    # The lesson this lab exists to teach.
    big = tt[(tt["sig_bh"]) & (tt["cohens_d"].abs() < 0.2)]
    print(f"\n{line}\nSTATISTICAL VERSUS PRACTICAL SIGNIFICANCE\n{line}")
    print(f"  t-test pairs significant after BH but with a NEGLIGIBLE effect size: "
          f"{len(big)}/{int(tt['sig_bh'].sum())}")
    if len(big):
        print("  With 6,000-22,000 impressions a group, a difference far too small to")
        print("  act on still clears p<0.05. The effect size is the column that decides.")
    print(f"  largest |Cohen's d| observed: {tt['cohens_d'].abs().max():.3f} "
          f"({interpret_d(tt['cohens_d'].abs().max())})")

    demo = correction_bites_demo(sub)
    demo.to_csv(HERE / "results_correction_subsample_demo.csv", index=False)

    heatmap(tt, "cohens_d", "Cohen's d - cost per impression (row minus column)",
            "heatmap_cohens_d.png", "{:+.2f}", "RdBu_r")
    heatmap(fi, "p_bh", "Conversion rate: BH-adjusted p-value", "heatmap_conversion_p.png",
            "{:.3f}")
    correction_chart(tt, fi)

    cpa_g.to_csv(HERE / "results_cpa_by_campaign.csv")
    cpa_p.to_csv(HERE / "results_cpa_pairs.csv", index=False)
    tt.to_csv(HERE / "results_ttest_cost.csv", index=False)
    fi.to_csv(HERE / "results_fisher_conversion.csv", index=False)
    print(f"\nwritten: results_ttest_cost.csv, results_fisher_conversion.csv")
    print(f"figures: heatmap_cohens_d.png, heatmap_conversion_p.png, correction_effect.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
