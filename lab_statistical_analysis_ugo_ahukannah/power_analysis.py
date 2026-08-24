"""Part 4 - power analysis and sample-size planning (Step 7).

Answers three questions a marketer actually has:

  1. Given what we ran, what could we have detected?  (achieved power)
  2. How big does the next test need to be?           (required n for 80% power)
  3. Was this dataset adequate?                        (adequacy assessment)

Two power families, matching the two test families in statistical_analysis.py:
Cohen's d for the continuous cost metric, and the arcsine-transformed effect
size (Cohen's h) for conversion rates, which is what proportion power needs.

Run:  python power_analysis.py

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.power import NormalIndPower, TTestIndPower
from statsmodels.stats.proportion import proportion_effectsize

from marketing_data import (FIGURES, HERE, analysis_frame, group_summary, load_criteo)

ALPHA = 0.05
TARGET_POWER = 0.80
N_COMPARISONS = 15                       # 6 campaigns choose 2
ALPHA_CORRECTED = ALPHA / N_COMPARISONS  # Bonferroni-adjusted planning threshold


def achieved_power(sub: pd.DataFrame) -> pd.DataFrame:
    """Power we actually had, per campaign, for a range of true effect sizes."""
    an = TTestIndPower()
    g = group_summary(sub)
    rows = []
    for name, r in g.iterrows():
        n = int(r["impressions"])
        for d in (0.05, 0.1, 0.2, 0.5):
            rows.append({"group": name, "n": n, "effect_d": d,
                         "power_uncorrected": an.power(effect_size=d, nobs1=n, alpha=ALPHA, ratio=1.0),
                         "power_bonferroni": an.power(effect_size=d, nobs1=n,
                                                      alpha=ALPHA_CORRECTED, ratio=1.0)})
    return pd.DataFrame(rows)


def required_n_continuous() -> pd.DataFrame:
    an = TTestIndPower()
    rows = []
    for d in (0.05, 0.1, 0.2, 0.3, 0.5, 0.8):
        rows.append({
            "effect_d": d,
            "label": ("negligible" if d < 0.2 else "small" if d < 0.5 else
                      "medium" if d < 0.8 else "large"),
            "n_per_group_uncorrected": int(np.ceil(
                an.solve_power(effect_size=d, alpha=ALPHA, power=TARGET_POWER, ratio=1.0))),
            "n_per_group_bonferroni": int(np.ceil(
                an.solve_power(effect_size=d, alpha=ALPHA_CORRECTED, power=TARGET_POWER, ratio=1.0))),
        })
    return pd.DataFrame(rows)


def required_n_conversion(baseline_cvr: float) -> pd.DataFrame:
    """Impressions per arm to detect a relative lift on a baseline conversion rate."""
    an = NormalIndPower()
    rows = []
    for lift in (0.05, 0.10, 0.20, 0.30, 0.50, 1.00):
        p2 = baseline_cvr * (1 + lift)
        if p2 >= 1:
            continue
        h = proportion_effectsize(p2, baseline_cvr)
        rows.append({
            "relative_lift": f"+{lift:.0%}",
            "baseline_cvr_pct": baseline_cvr * 100,
            "target_cvr_pct": p2 * 100,
            "cohens_h": h,
            "n_per_arm_uncorrected": int(np.ceil(
                an.solve_power(effect_size=h, alpha=ALPHA, power=TARGET_POWER, ratio=1.0))),
            "n_per_arm_bonferroni": int(np.ceil(
                an.solve_power(effect_size=h, alpha=ALPHA_CORRECTED, power=TARGET_POWER, ratio=1.0))),
        })
    return pd.DataFrame(rows)


def adequacy(sub: pd.DataFrame, req: pd.DataFrame) -> None:
    g = group_summary(sub)
    smallest = int(g["impressions"].min())
    largest = int(g["impressions"].max())
    need_small = int(req.loc[req["effect_d"] == 0.2, "n_per_group_bonferroni"].iloc[0])
    need_negl = int(req.loc[req["effect_d"] == 0.1, "n_per_group_bonferroni"].iloc[0])

    print("\n" + "=" * 88)
    print("IS THE CURRENT DATA ADEQUATE?")
    print("=" * 88)
    print(f"  impressions per campaign      {smallest:,} (smallest) to {largest:,} (largest)")
    print(f"  needed for a SMALL effect     {need_small:,} per group "
          f"(d=0.2, 80% power, Bonferroni-adjusted alpha)")
    print(f"  needed for d=0.1              {need_negl:,} per group")
    verdict = "ADEQUATE" if smallest >= need_small else "UNDERPOWERED"
    print(f"\n  verdict for small effects:    {verdict}")
    print(f"  Every campaign clears the bar for detecting a small effect, and the")
    print(f"  largest clear it for d=0.1 as well. The constraint on this analysis is")
    print(f"  not sample size - it is that differences this easy to detect are not")
    print(f"  automatically differences worth acting on.")


def curves(baseline_cvr: float) -> None:
    an_t, an_p = TTestIndPower(), NormalIndPower()
    ns = np.unique(np.logspace(1.5, 5, 90).astype(int))

    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.8))
    for d in (0.05, 0.1, 0.2, 0.5):
        ax[0].plot(ns, [an_t.power(effect_size=d, nobs1=n, alpha=ALPHA, ratio=1.0) for n in ns],
                   label=f"d = {d}")
    ax[0].axhline(TARGET_POWER, ls="--", color="grey", lw=1)
    ax[0].text(ns[2], TARGET_POWER + 0.02, "80% power", fontsize=8, color="grey")
    ax[0].set_xscale("log"); ax[0].set_xlabel("impressions per campaign")
    ax[0].set_ylabel("power"); ax[0].set_ylim(0, 1.02)
    ax[0].set_title("Power to detect a cost difference (Welch's t-test)", fontweight="bold", fontsize=11)
    ax[0].legend(fontsize=8, frameon=False)

    for lift in (0.05, 0.10, 0.20, 0.50):
        p2 = baseline_cvr * (1 + lift)
        h = proportion_effectsize(p2, baseline_cvr)
        ax[1].plot(ns, [an_p.power(effect_size=h, nobs1=n, alpha=ALPHA, ratio=1.0) for n in ns],
                   label=f"+{lift:.0%} lift")
    ax[1].axhline(TARGET_POWER, ls="--", color="grey", lw=1)
    ax[1].set_xscale("log"); ax[1].set_xlabel("impressions per arm")
    ax[1].set_ylabel("power"); ax[1].set_ylim(0, 1.02)
    ax[1].set_title(f"Power to detect a conversion lift (baseline {baseline_cvr:.2%})",
                    fontweight="bold", fontsize=11)
    ax[1].legend(fontsize=8, frameon=False)
    for a in ax:
        a.spines[["top", "right"]].set_visible(False); a.grid(alpha=0.25)
    plt.tight_layout(); plt.savefig(FIGURES / "power_curves.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nfigure written: power_curves.png")


def main() -> int:
    sub = analysis_frame(load_criteo())
    g = group_summary(sub)
    baseline = float(g["conversions"].sum() / g["impressions"].sum())

    line = "=" * 88
    print(f"{line}\nPOWER ANALYSIS\n{line}")
    print(f"  alpha (uncorrected)           {ALPHA}")
    print(f"  alpha (Bonferroni, {N_COMPARISONS} tests)  {ALPHA_CORRECTED:.5f}")
    print(f"  target power                  {TARGET_POWER:.0%}")
    print(f"  pooled baseline conversion    {baseline:.4%}")

    print(f"\n{line}\nACHIEVED POWER AT THE SAMPLE SIZES WE HAVE\n{line}")
    ap = achieved_power(sub)
    piv = ap.pivot_table(index=["group", "n"], columns="effect_d",
                         values="power_bonferroni").round(3)
    print("  power at the Bonferroni-adjusted threshold, by true effect size:")
    print(piv.to_string())

    print(f"\n{line}\nSAMPLE SIZE NEEDED FOR 80% POWER - continuous metric\n{line}")
    req = required_n_continuous()
    print(req.to_string(index=False))

    print(f"\n{line}\nSAMPLE SIZE NEEDED FOR 80% POWER - conversion lift\n{line}")
    reqc = required_n_conversion(baseline)
    print(reqc.round(4).to_string(index=False))
    print("\n  Read this as the planning table for the next test: to call a 10% relative")
    print("  lift on a ~5% baseline, budget the 'n_per_arm_bonferroni' column if you")
    print("  intend to compare more than two arms.")

    adequacy(sub, req)
    curves(baseline)

    req.to_csv(HERE / "power_required_n_continuous.csv", index=False)
    reqc.to_csv(HERE / "power_required_n_conversion.csv", index=False)
    ap.to_csv(HERE / "power_achieved.csv", index=False)
    print("\nwritten: power_required_n_continuous.csv, power_required_n_conversion.csv, power_achieved.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
