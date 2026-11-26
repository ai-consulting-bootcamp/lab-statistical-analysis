"""Part 5: significant findings, bootstrap confidence intervals, composite ranking, budget.

Input:  data/marketing_data.csv, results/group_metrics.csv, results/cpa_ttests.csv,
        results/cvr_fisher.csv
Run:    python recommendations.py
Writes: results/significant_findings.csv, results/cpa_confidence_intervals.csv,
        results/budget_allocation.csv, figures/budget_allocation.png
The numbers printed here feed executive_memo.md.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).resolve().parent
RESULTS, FIGS = HERE / "results", HERE / "figures"
BUDGET = 500_000
MIN_SHARE, MAX_SHARE = 0.05, 0.35
RNG = np.random.default_rng(7)
sns.set_theme(style="whitegrid")
pd.set_option("display.width", 160)


def section(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


df = pd.read_csv(HERE / "data" / "marketing_data.csv", parse_dates=["week"])
metrics = pd.read_csv(RESULTS / "group_metrics.csv", index_col="platform")
cpa = pd.read_csv(RESULTS / "cpa_ttests.csv")
fisher = pd.read_csv(RESULTS / "cvr_fisher.csv")

# --------------------------------------------------------------------------
# Step 8.1: significant findings (FDR-corrected)
# --------------------------------------------------------------------------
section("STEP 8.1: SIGNIFICANT FINDINGS AFTER BENJAMINI-HOCHBERG FDR")
rows = []
for r in cpa[cpa.significant_fdr].itertuples():
    better, worse = (r.group_a, r.group_b) if r.mean_a < r.mean_b else (r.group_b, r.group_a)
    rows.append(dict(metric="CPA (weekly mean)", better=better, worse=worse, abs_difference=abs(r.difference),
                     p_value_fdr=r.p_value_fdr, cohens_d=abs(r.cohens_d), effect=r.effect_size))
for r in fisher[fisher.significant_fdr].itertuples():
    better, worse = (r.group_a, r.group_b) if r.rate_a > r.rate_b else (r.group_b, r.group_a)
    rows.append(dict(metric="Conversion rate", better=better, worse=worse, abs_difference=abs(r.difference),
                     p_value_fdr=r.p_value_fdr, cohens_d=np.nan, effect="-"))
findings = pd.DataFrame(rows)
findings.to_csv(RESULTS / "significant_findings.csv", index=False)
for r in findings.itertuples():
    diff = f"${r.abs_difference:,.2f} lower CPA" if r.metric.startswith("CPA") else f"{r.abs_difference:.2%} higher CVR"
    d = f", d={r.cohens_d:.2f} ({r.effect})" if r.metric.startswith("CPA") else ""
    print(f"  [{r.metric:<17}] {r.better:>14} beats {r.worse:<14} {diff:>22}  p_fdr={r.p_value_fdr:.1e}{d}")
print(f"\n{len(findings)} significant findings ({(findings.metric != 'Conversion rate').sum()} CPA, "
      f"{(findings.metric == 'Conversion rate').sum()} conversion rate).")
print("Not significant: Snapchat vs TikTok on CPA -> treated as a tie below.")


# --------------------------------------------------------------------------
# Step 8.2: bootstrap CIs
# --------------------------------------------------------------------------
def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95, rng=RNG):
    data = np.asarray(data)
    means = rng.choice(data, size=(n_bootstrap, len(data)), replace=True).mean(axis=1)
    a = 1 - ci_level
    return np.percentile(means, 100 * a / 2), np.percentile(means, 100 * (1 - a / 2))


section("STEP 8.2: 95% BOOTSTRAP CONFIDENCE INTERVALS FOR MEAN WEEKLY CPA")
w = df.dropna(subset=["cpa"])
recent = w[w.week > w.week.max() - pd.Timedelta(weeks=13)]
ci_rows = []
for p, s in w.groupby("platform").cpa:
    lo, hi = bootstrap_ci(s)
    rs = recent.loc[recent.platform == p, "cpa"]
    qlo, qhi = bootstrap_ci(rs)
    ci_rows.append(dict(channel=p, weeks=len(s), mean_cpa=s.mean(), ci_lower=lo, ci_upper=hi,
                        ci_width_pct=(hi - lo) / s.mean() * 100, last13_mean=rs.mean(), last13_ci_lower=qlo,
                        last13_ci_upper=qhi, last13_width_pct=(qhi - qlo) / rs.mean() * 100))
ci = pd.DataFrame(ci_rows).sort_values("mean_cpa")
ci.to_csv(RESULTS / "cpa_confidence_intervals.csv", index=False)
print(ci.round(2).to_string(index=False))
print("-> Full-period CIs are tight (+/-5-8%) and only Snapchat and TikTok overlap. On the last 13 weeks the\n"
      "   intervals are 2-3.5x wider and Meta/Snapchat/TikTok all overlap: a quarterly review can't rank them.\n"
      "   The last-13-week means are ~35% lower because that window is Q4 (seasonal CPA dip, see Part 1).")

# --------------------------------------------------------------------------
# Step 8.3: composite score and allocation
# --------------------------------------------------------------------------
section("STEP 8.3: COMPOSITE SCORE (50% CPA rank, 50% ROAS rank)")
m = metrics[["cpa", "roas", "conversion_rate", "cost"]].copy()
# rank 1 = worst ... 6 = best; lower CPA is better so ascending=False on CPA
m["cpa_rank"] = m.cpa.rank(ascending=False)
m["roas_rank"] = m.roas.rank(ascending=True)
# Statistical tie: Snapchat vs TikTok CPA not significant after FDR -> share the average rank
ties = cpa[~cpa.significant_fdr]
for r in ties.itertuples():
    avg = m.loc[[r.group_a, r.group_b], "cpa_rank"].mean()
    m.loc[[r.group_a, r.group_b], "cpa_rank"] = avg
    print(f"CPA tie applied: {r.group_a} = {r.group_b} = rank {avg} (p_fdr = {r.p_value_fdr:.2f})")
m["composite"] = 0.5 * m.cpa_rank + 0.5 * m.roas_rank
m = m.sort_values("composite", ascending=False)


def constrained_shares(score, lo=MIN_SHARE, hi=MAX_SHARE):
    """Proportional to score, then iteratively clip to [lo, hi] and re-spread the remainder."""
    share = score / score.sum()
    fixed = pd.Series(False, index=share.index)
    for _ in range(20):
        over, under = (share > hi + 1e-12) & ~fixed, (share < lo - 1e-12) & ~fixed
        if not (over.any() or under.any()):
            break
        share[over], share[under] = hi, lo
        fixed |= over | under
        free = ~fixed
        share[free] = score[free] / score[free].sum() * (1 - share[fixed].sum())
    return share


m["current_share"] = m.cost / m.cost.sum()
m["recommended_share"] = constrained_shares(m.composite)
m["recommended_budget"] = m.recommended_share * BUDGET
m["current_budget_equiv"] = m.current_share * BUDGET
m["change"] = m.recommended_budget - m.current_budget_equiv
# naive projection: conversions = budget / historical pooled CPA (upper bound, ignores saturation)
m["naive_conv_current"] = m.current_budget_equiv / m.cpa
m["naive_conv_recommended"] = m.recommended_budget / m.cpa
m.to_csv(RESULTS / "budget_allocation.csv")

cols = ["cpa", "roas", "cpa_rank", "roas_rank", "composite"]
print(m[cols].round(2).to_string())

section(f"BUDGET ALLOCATION: ${BUDGET:,}/month, floor {MIN_SHARE:.0%}, cap {MAX_SHARE:.0%}")
out = m[["current_share", "current_budget_equiv", "recommended_share", "recommended_budget", "change"]].copy()
out.loc["TOTAL"] = out.sum()
fmt = out.copy()
for c in ("current_share", "recommended_share"):
    fmt[c] = out[c].map("{:.1%}".format)
for c in ("current_budget_equiv", "recommended_budget", "change"):
    fmt[c] = out[c].map((lambda v: f"{'+' if v > -50 else '-'}${abs(v) / 1000:,.1f}K") if c == "change"
                        else (lambda v: f"${v / 1000:,.1f}K"))
print(fmt.to_string())
nc, nr = m.naive_conv_current.sum(), m.naive_conv_recommended.sum()
print(f"\nNaive monthly conversions at historical CPA: current mix {nc:,.0f} -> recommended {nr:,.0f} "
      f"({nr / nc - 1:+.0%}).\nUpper bound only: assumes average CPA = marginal CPA. Search demand is finite, so "
      "extra Search spend will buy\nconversions at a worse CPA than its history. Validate with a geo-split test.")
print("Why floor 5%: keeps every channel measurable (and LinkedIn as a monitored test cell, not zero).")
print("Why cap 35%: concentration risk + diminishing returns on Search.")

fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(m))
ax.barh(x + 0.2, m.current_budget_equiv / 1000, height=0.4, label="Current mix (historical spend share)", color="#bbbbbb")
ax.barh(x - 0.2, m.recommended_budget / 1000, height=0.4, label="Recommended", color="#1f77b4")
for i, (c, r) in enumerate(zip(m.current_budget_equiv, m.recommended_budget)):
    ax.text(r / 1000, i - 0.2, rf" \${r / 1000:.0f}K", va="center", fontsize=9)
ax.set_yticks(x, m.index)
ax.invert_yaxis()
ax.set_xlabel(r"Monthly budget (\$K of \$500K)")
ax.set_title("Budget reallocation by composite score (50% CPA rank, 50% ROAS rank)", fontweight="bold")
ax.legend(loc="lower right")
ax.margins(x=0.15)
fig.tight_layout()
fig.savefig(FIGS / "budget_allocation.png", dpi=130)
plt.close(fig)

section("PRIORITISATION")
print("Invest:      Google Search (best on every metric; scale until marginal CPA rises), Meta (clear #2).")
print("Hold/grow:   TikTok and Snapchat (statistically tied on CPA; keep at a mid share, test creative).")
print("Hold flat:   Google Display (profitable but thin: CPA 2.3x Meta, ROAS 1.21; first to cut if Search saturates).")
print("Restructure: LinkedIn (ROAS 0.44 = loses $0.56 per $1; cut to the 5% floor, rebuild as a B2B/test cell).")
print("\nSaved results/significant_findings.csv, cpa_confidence_intervals.csv, budget_allocation.csv, "
      "figures/budget_allocation.png")
