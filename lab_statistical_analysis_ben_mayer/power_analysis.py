"""Part 4: power analysis and sample-size planning for CPA comparisons.

Input:  data/marketing_data.csv, results/cpa_ttests.csv (from statistical_analysis.py)
Run:    python power_analysis.py
Writes: results/power_grid.csv, results/min_sample_size.csv, results/power_adequacy.csv,
        figures/power_analysis_cpa.png

Unit note: the lab spec counts samples in days ("n_days", "current data = 90 days").
This dataset's unit of analysis is the platform-week (see data_exploration.py), so one
sample = one week here. `n_periods` below is the spec's `n_days`. Two "current data"
benchmarks are checked: the full panel (~155 weeks) and a quarterly review (13 weeks,
about the spec's 90 days).

Noise note: the spec simulates CPA with std = 15% of the mean. The observed weekly CPA
coefficient of variation in this data is ~0.40 (Part 1). Power falls with the square of
noise, so I run both: the spec's 0.15 and the observed CV.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

HERE = Path(__file__).resolve().parent
RESULTS, FIGS = HERE / "results", HERE / "figures"
ALPHA, TARGET = 0.05, 0.80
RNG = np.random.default_rng(42)
sns.set_theme(style="whitegrid")
pd.set_option("display.width", 160)


def section(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def empirical_power_cpa(true_diff_pct, base_cpa, n_periods, n_sim=1000, alpha=ALPHA, cv=0.15, rng=RNG):
    """Share of simulated A/B comparisons where a Welch t-test rejects H0.

    A ~ Normal(base, base*cv), B ~ Normal(base*(1+diff), base*cv), both floored at 50% of
    base (the spec's 'cap at 50% of base': CPA cannot go to zero or negative).
    Vectorised: n_sim experiments are rows of one matrix.
    """
    sd = base_cpa * cv
    floor = 0.5 * base_cpa
    a = np.maximum(rng.normal(base_cpa, sd, (n_sim, n_periods)), floor)
    b = np.maximum(rng.normal(base_cpa * (1 + true_diff_pct), sd, (n_sim, n_periods)), floor)
    p = stats.ttest_ind(a, b, axis=1, equal_var=False).pvalue
    return float((p < alpha).mean())


df = pd.read_csv(HERE / "data" / "marketing_data.csv", parse_dates=["week"])
cpa = pd.read_csv(RESULTS / "cpa_ttests.csv")
w = df.dropna(subset=["cpa"])
cv_by_platform = w.groupby("platform").cpa.agg(lambda s: s.std() / s.mean())
OBS_CV = round(float(cv_by_platform.median()), 2)
BASE = round(float(w.loc[w.platform == "Meta", "cpa"].mean()), 2)  # reference channel: best social CPA
CURRENT_FULL = int(w.groupby("platform").size().median())
CURRENT_Q = 13

section("SETUP")
print(f"Base CPA (Meta mean weekly CPA): ${BASE}")
print(f"Noise scenarios: spec CV = 0.15, observed median weekly CPA CV = {OBS_CV}")
print(f"Current data: full panel = {CURRENT_FULL} weeks per channel; quarterly review = {CURRENT_Q} weeks")

# --------------------------------------------------------------------------
# Step 7.1: power grid
# --------------------------------------------------------------------------
section("STEP 7.1: EMPIRICAL POWER (1,000 simulations per cell)")
effects = [0.05, 0.10, 0.15, 0.20]
sizes = [13, 30, 60, 90, 120, 180]  # spec grid + 13 weeks (one quarter, ~the spec's 90 days)
rows = [dict(cv=cv, effect_size_pct=int(e * 100), n_periods=n, power=empirical_power_cpa(e, BASE, n, cv=cv))
        for cv in (0.15, OBS_CV) for e in effects for n in sizes]
grid = pd.DataFrame(rows)
grid.to_csv(RESULTS / "power_grid.csv", index=False)
for cv in (0.15, OBS_CV):
    t = grid[grid.cv == cv].pivot(index="effect_size_pct", columns="n_periods", values="power")
    t.index = [f"{i}% diff" for i in t.index]
    print(f"\nPower table, CV = {cv} (rows: true CPA difference, cols: weeks per channel)")
    print(t.map(lambda x: f"{x:.0%}").to_string())

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
for ax, cv, label in zip(axes, (0.15, OBS_CV), ("Spec assumption: CV = 0.15", f"Observed noise: CV = {OBS_CV}")):
    for e in effects:
        s = grid[(grid.cv == cv) & (grid.effect_size_pct == int(e * 100))]
        ax.plot(s.n_periods, s.power, marker="o", label=f"{int(e * 100)}% CPA difference")
    ax.axhline(TARGET, color="red", ls="--", lw=1.2, label="80% power target")
    ax.axvline(CURRENT_Q, color="grey", ls=":", lw=1)
    ax.text(CURRENT_Q + 2, 0.03, "13 wk\n(quarter)", color="grey", fontsize=8)
    ax.axvline(CURRENT_FULL, color="grey", ls=":", lw=1)
    ax.text(CURRENT_FULL + 2, 0.03, f"{CURRENT_FULL} wk\n(full data)", color="grey", fontsize=8)
    ax.set_title(label, fontweight="bold")
    ax.set_xlabel("Sample size (weeks per channel)")
    ax.set_ylim(0, 1.03)
    ax.legend(fontsize=8, loc="center right")
axes[0].set_ylabel("Power (P(detect | real difference))")
fig.suptitle(f"Power to detect a CPA difference vs a ${BASE} baseline (Welch t-test, alpha = 0.05)", fontsize=13)
fig.tight_layout()
fig.savefig(FIGS / "power_analysis_cpa.png", dpi=130)
plt.close(fig)


# --------------------------------------------------------------------------
# Step 7.2: minimum sample size for 80% power
# --------------------------------------------------------------------------
def min_n_for_power(diff, cv, base=BASE, target=TARGET, n_max=2000):
    """Smallest n with simulated power >= target (2,000 sims per step).

    The analytic normal approximation brackets the search; steps are ~2.5% of the bracket,
    so the simulated minimum is accurate to a few percent, which is enough for planning.
    """
    d = diff / cv  # standardised effect (same sd both arms)
    approx = int(np.ceil(2 * (stats.norm.ppf(1 - ALPHA / 2) + stats.norm.ppf(target)) ** 2 / d ** 2))
    lo, hi = max(2, int(approx * 0.6)), min(n_max, int(approx * 1.5) + 5)
    if approx > n_max:
        return approx, approx
    for n in range(lo, hi + 1, max(1, (hi - lo) // 40)):
        if empirical_power_cpa(diff, base, n, n_sim=2000, cv=cv) >= target:
            return n, approx
    return hi, approx


section("STEP 7.2: MINIMUM WEEKS PER CHANNEL FOR 80% POWER")
mins = []
for cv in (0.15, OBS_CV):
    for e in effects:
        n, approx = min_n_for_power(e, cv)
        mins.append(dict(cv=cv, effect_size_pct=int(e * 100), min_weeks_simulated=n, min_weeks_analytic=approx,
                         quarter_13wk="sufficient" if n <= CURRENT_Q else "insufficient",
                         full_data=("sufficient" if n <= CURRENT_FULL else "insufficient")))
mins = pd.DataFrame(mins)
mins.to_csv(RESULTS / "min_sample_size.csv", index=False)
print(mins.to_string(index=False))
print("(analytic = normal-approximation n = 2(z_0.975 + z_0.8)^2 / d^2, a cross-check on the simulation)")

# --------------------------------------------------------------------------
# Step 7.3: adequacy of current data for each FDR-significant pair
# --------------------------------------------------------------------------
section("STEP 7.3: DATA ADEQUACY FOR FDR-SIGNIFICANT CPA PAIRS")
print("Observed difference uses the smaller mean as baseline; noise = the pair's average observed CV.")
print("Caveat: power computed at the observed effect is 'post-hoc power'; it is used here only to ask\n"
      "whether a quarterly (13-week) review could see the same gap, not to re-judge the 3-year test.\n")
adequacy = []
for r in cpa[cpa.significant_fdr].itertuples():
    lo_mean, hi_mean = sorted([r.mean_a, r.mean_b])
    diff = hi_mean / lo_mean - 1
    cv = float(cv_by_platform[[r.group_a, r.group_b]].mean())
    n_now = int(min(r.n_a, r.n_b))
    p_full = empirical_power_cpa(diff, lo_mean, n_now, cv=cv)
    p_q = empirical_power_cpa(diff, lo_mean, CURRENT_Q, cv=cv)
    need = None if p_q >= TARGET else min_n_for_power(diff, cv, base=lo_mean)[0]
    adequacy.append(dict(pair=f"{r.group_a} vs {r.group_b}", observed_diff_pct=round(diff * 100, 1), pair_cv=round(cv, 2),
                         weeks_available=n_now, power_full=p_full, power_13wk=p_q, weeks_needed_for_80=need))
adequacy = pd.DataFrame(adequacy).sort_values("observed_diff_pct")
adequacy.to_csv(RESULTS / "power_adequacy.csv", index=False)
show = adequacy.copy()
show["power_full"] = show.power_full.map("{:.0%}".format)
show["power_13wk"] = show.power_13wk.map("{:.0%}".format)
show["weeks_needed_for_80"] = show.weeks_needed_for_80.map(lambda x: "-" if pd.isna(x) else f"{int(x)}")
print(show.to_string(index=False))

section("KEY ANSWERS")
row = lambda cv, e: mins[(mins.cv == cv) & (mins.effect_size_pct == e)].iloc[0]  # noqa: E731
print(f"- Enough data? For the full panel, yes: every significant pair has ~100% power at {CURRENT_FULL} weeks.")
print(f"- Under the spec's 15% noise, 13 weeks detects only large gaps; a 10% CPA gap needs "
      f"{row(0.15, 10).min_weeks_simulated} weeks.")
print(f"- Under real noise (CV {OBS_CV}), a 10% gap needs {row(OBS_CV, 10).min_weeks_simulated} weeks and a 5% gap "
      f"{row(OBS_CV, 5).min_weeks_simulated} weeks per channel; even the full 3 years cannot resolve 5%.")
print(f"- The spec's 15% noise assumption understates required sample size by ~(CV_obs/0.15)^2 = "
      f"{(OBS_CV / 0.15) ** 2:.1f}x. Plan tests on measured variance, not a textbook default.")
mid = adequacy[adequacy.weeks_needed_for_80.notna()]
if len(mid):
    print("- Pairs a 13-week review would likely miss: "
          + "; ".join(f"{r.pair} ({r.observed_diff_pct:.0f}% gap, {r.power_13wk:.0%} power, needs "
                      f"{int(r.weeks_needed_for_80)} wk)" for r in mid.itertuples()) + ".")
print("\nSaved figures/power_analysis_cpa.png and results/power_*.csv, results/min_sample_size.csv")
