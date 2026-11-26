"""Parts 2-3: pairwise channel comparisons and multiple-comparisons correction.

Input:  data/marketing_data.csv (platform x week panel from data_exploration.py)
Run:    python statistical_analysis.py
Writes: results/cpa_ttests.csv, results/cvr_ttests.csv, results/cvr_fisher.csv,
        results/correction_summary.csv,
        figures/metric_comparison_heatmap.png, figures/rate_comparison.png,
        figures/correction_comparison.png

Test choices
- Weekly CPA is continuous -> independent two-sample t-test (scipy.stats.ttest_ind).
  I use Welch's version (equal_var=False): weekly CPA spread differs ~100x between
  Google Search and LinkedIn, so the equal-variance assumption is clearly false.
  With ~150 weeks per group the CLT makes the t-test robust to the right skew.
- Conversions out of clicks are binary outcomes -> Fisher's exact test on the pooled
  2x2 table [[conv_A, non_conv_A], [conv_B, non_conv_B]].
"""

from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import false_discovery_control, fisher_exact

HERE = Path(__file__).resolve().parent
RESULTS, FIGS = HERE / "results", HERE / "figures"
ALPHA = 0.05
sns.set_theme(style="whitegrid")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def section(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def effect_label(d):
    d = abs(d)
    return "negligible" if d < 0.2 else "small" if d < 0.5 else "medium" if d < 0.8 else "large"


df = pd.read_csv(HERE / "data" / "marketing_data.csv", parse_dates=["week"])


# --------------------------------------------------------------------------
# Step 4: t-tests on continuous weekly metrics
# --------------------------------------------------------------------------
def pairwise_ttests(data, metric, verbose=True):
    d = data.replace([np.inf, -np.inf], np.nan).dropna(subset=[metric])
    d = d[d[metric] > 0] if metric == "cpa" else d  # CPA <= 0 is impossible / undefined
    groups = sorted(d.platform.unique())
    rows = []
    for a, b in combinations(groups, 2):
        xa, xb = d.loc[d.platform == a, metric].values, d.loc[d.platform == b, metric].values
        t, p = stats.ttest_ind(xa, xb, equal_var=False)
        mean_a, mean_b = xa.mean(), xb.mean()
        diff = mean_b - mean_a
        pooled_sd = np.sqrt((xa.var(ddof=1) + xb.var(ddof=1)) / 2)
        d_ = diff / pooled_sd
        rows.append(dict(group_a=a, group_b=b, n_a=len(xa), n_b=len(xb), mean_a=mean_a, mean_b=mean_b,
                         difference=diff, pct_difference=diff / mean_a * 100, t_stat=t, p_value=p,
                         cohens_d=d_, effect_size=effect_label(d_), significant=p < ALPHA))
        if verbose:
            print(f"{a:>14} vs {b:<14} mean {mean_a:9.4f} -> {mean_b:9.4f}  diff {diff:+9.4f} "
                  f"({diff / mean_a * 100:+7.1f}%)  t={t:+7.2f}  p={p:.2e}  d={d_:+.2f} ({effect_label(d_)})")
    res = pd.DataFrame(rows)
    print(f"\n{metric}: {len(res)} comparisons, {res.significant.sum()} significant at alpha={ALPHA}")
    return res


section("STEP 4: WELCH t-TESTS ON WEEKLY CPA (difference = B - A)")
cpa = pairwise_ttests(df, "cpa")

section("STEP 4 (extra): t-TESTS ON WEEKLY CONVERSION RATE, to compare with Fisher")
cvr_t = pairwise_ttests(df, "conversion_rate")

# Heatmap of CPA p-values
groups = sorted(df.platform.unique())
mat = pd.DataFrame(1.0, index=groups, columns=groups)
for r in cpa.itertuples():
    mat.loc[r.group_a, r.group_b] = mat.loc[r.group_b, r.group_a] = r.p_value
annot = mat.map(lambda p: "1.0" if p == 1 else f"{p:.1e}" if p < 0.001 else f"{p:.3f}")
fig, ax = plt.subplots(figsize=(9, 7))
# The spec suggests 'RdYlGn_r' AND "red = significant"; those conflict (_r maps low p to green).
# I follow the stated meaning: plain 'RdYlGn' so low p-values are red.
sns.heatmap(mat, annot=annot, fmt="", cmap="RdYlGn", vmin=0, vmax=0.1, ax=ax,
            cbar_kws={"label": "p-value (Welch t-test; colour capped at 0.10)"}, linewidths=0.5)
ax.set_title("Weekly CPA: pairwise p-values (red = significant, green = not)", fontweight="bold")
fig.tight_layout()
fig.savefig(FIGS / "metric_comparison_heatmap.png", dpi=130)
plt.close(fig)

# --------------------------------------------------------------------------
# Step 5: Fisher's exact test on conversions / clicks
# --------------------------------------------------------------------------
section("STEP 5: FISHER'S EXACT TEST ON CONVERSIONS OUT OF CLICKS")
agg = df.groupby("platform")[["conversions", "clicks"]].sum()
agg["non_conversions"] = agg.clicks - agg.conversions
agg["rate"] = agg.conversions / agg.clicks
print(agg.rename(columns={"clicks": "total_attempts"}).to_string())
print()

rows = []
for a, b in combinations(groups, 2):
    ca, na = int(agg.loc[a, "conversions"]), int(agg.loc[a, "clicks"])
    cb, nb = int(agg.loc[b, "conversions"]), int(agg.loc[b, "clicks"])
    table = [[ca, na - ca], [cb, nb - cb]]
    odds, p = fisher_exact(table, alternative="two-sided")
    ra, rb = ca / na, cb / nb
    rows.append(dict(group_a=a, group_b=b, conv_a=ca, clicks_a=na, conv_b=cb, clicks_b=nb, rate_a=ra,
                     rate_b=rb, difference=rb - ra, pct_difference=(rb - ra) / ra * 100, odds_ratio=odds,
                     p_value=p, significant=p < ALPHA))
    print(f"{a:>14} vs {b:<14} {ra:.3%} vs {rb:.3%}  diff {rb - ra:+.3%} ({(rb - ra) / ra * 100:+6.1f}%)  "
          f"OR={odds:.3f}  p={p:.2e}")
fisher = pd.DataFrame(rows)
print(f"\nFisher: {len(fisher)} comparisons, {fisher.significant.sum()} significant at alpha={ALPHA}")

print("\nFisher vs t-test on conversion rate (same pairs):")
cmp_ = fisher[["group_a", "group_b", "p_value"]].merge(
    cvr_t[["group_a", "group_b", "p_value"]], on=["group_a", "group_b"], suffixes=("_fisher", "_ttest"))
print(cmp_.to_string(index=False, float_format=lambda x: f"{x:.2e}"))
print(
    "-> Fisher treats every click (~5M) as an independent trial, so even a 0.2pp gap gets p~1e-50.\n"
    "   The weekly t-test uses ~155 weekly rates per channel and keeps week-to-week noise, so its\n"
    "   p-values are much larger. Clicks within a week are not independent (same ads, audiences,\n"
    "   seasonality), so Fisher's p-values here are overconfident. Both agree on direction."
)

# Rate comparison bar chart
s = agg.sort_values("rate")
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(s.index, s.rate * 100, color=sns.color_palette("viridis", len(s)))
for bar, r, c in zip(bars, s.rate, s.conversions):
    ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f" {r:.2%}  ({c:,} conv)", va="center")
ax.set_xlabel("Conversion rate (conversions / clicks, %)")
ax.set_title("Pooled conversion rate by platform, Sales campaigns 2023-2025", fontweight="bold")
ax.margins(x=0.3)
fig.tight_layout()
fig.savefig(FIGS / "rate_comparison.png", dpi=130)
plt.close(fig)

# --------------------------------------------------------------------------
# Step 6: multiple comparisons
# --------------------------------------------------------------------------
section("STEP 6.1: THE MULTIPLE-COMPARISONS PROBLEM")
total = len(cpa) + len(fisher)
print(f"Primary family: {len(cpa)} CPA t-tests + {len(fisher)} conversion-rate Fisher tests = {total}")
print(f"Expected false positives at alpha=0.05 if every null were true: {total} x 0.05 = {total * ALPHA:.1f}")
print(f"P(at least one false positive) if all nulls true: 1 - 0.95^{total} = {1 - (1 - ALPHA) ** total:.0%}")
print("So some 'significant' results in an uncorrected table are expected to be noise.")


def correct(res, name):
    m = len(res)
    a_bonf = ALPHA / m
    res["alpha_bonferroni"] = a_bonf
    res["significant_bonferroni"] = res.p_value < a_bonf
    res["p_value_fdr"] = false_discovery_control(res.p_value.values, method="bh")
    res["significant_fdr"] = res.p_value_fdr < ALPHA
    print(f"\n{name}: m={m}, Bonferroni alpha = 0.05/{m} = {a_bonf:.5f}")
    print(f"  uncorrected: {res.significant.sum()}  Bonferroni: {res.significant_bonferroni.sum()}  "
          f"FDR (BH): {res.significant_fdr.sum()}")
    lost = res[res.significant & ~res.significant_bonferroni]
    cols = ["group_a", "group_b", "p_value", "p_value_fdr", "significant_bonferroni", "significant_fdr"]
    if "cohens_d" in res:
        cols.insert(4, "cohens_d")
    print("  Significant after FDR:")
    print(res.loc[res.significant_fdr, cols].to_string(index=False, float_format=lambda x: f"{x:.3g}"))
    ns = res.loc[~res.significant_fdr, cols]
    print("  NOT significant after FDR:")
    print(ns.to_string(index=False, float_format=lambda x: f"{x:.3g}") if len(ns) else "    (none)")
    if len(lost):
        print("  Lost significance under Bonferroni:")
        print(lost[cols].to_string(index=False, float_format=lambda x: f"{x:.3g}"))
    return res


section("STEP 6.2-6.3: BONFERRONI AND BENJAMINI-HOCHBERG")
cpa = correct(cpa, "CPA (Welch t-test)")
fisher = correct(fisher, "Conversion rate (Fisher)")
cvr_t = correct(cvr_t, "Conversion rate (weekly t-test, supplementary)")

section("STEP 6 (extra): QUARTERLY LENS, last 13 weeks (~90 days) of CPA only")
print(
    "Three years of data make almost every gap obvious, so correction has little to remove.\n"
    "A CMO usually reviews the last quarter. Re-running the CPA family on the final 13 weeks\n"
    "shows what correction does when samples are small and p-values sit near the threshold."
)
recent = df[df.week > df.week.max() - pd.Timedelta(weeks=13)]
cpa_q = pairwise_ttests(recent, "cpa", verbose=False)
cpa_q = correct(cpa_q, "CPA, last 13 weeks (Welch t-test)")
cpa_q.to_csv(RESULTS / "cpa_ttests_last13weeks.csv", index=False)
print("\nPairs significant on 3 years but NOT on the last quarter (after FDR):")
lost_q = cpa.loc[cpa.significant_fdr, ["group_a", "group_b"]].merge(
    cpa_q.loc[~cpa_q.significant_fdr, ["group_a", "group_b", "n_a", "n_b", "p_value", "p_value_fdr"]])
print(lost_q.to_string(index=False, float_format=lambda x: f"{x:.3g}"))
print("-> Meta's CPA lead over Snapchat/TikTok (~20-28%) is real on 155 weeks but invisible in a\n"
      "   13-week review: an underpowered test, not evidence of 'no difference'. See power_analysis.py.")

section("STEP 6.4: SUMMARY OF CORRECTION METHODS")
summary = pd.DataFrame({
    "comparisons": [len(cpa), len(fisher), len(cvr_t), len(cpa_q)],
    "uncorrected": [cpa.significant.sum(), fisher.significant.sum(), cvr_t.significant.sum(),
                    cpa_q.significant.sum()],
    "bonferroni": [cpa.significant_bonferroni.sum(), fisher.significant_bonferroni.sum(),
                   cvr_t.significant_bonferroni.sum(), cpa_q.significant_bonferroni.sum()],
    "fdr_bh": [cpa.significant_fdr.sum(), fisher.significant_fdr.sum(), cvr_t.significant_fdr.sum(),
               cpa_q.significant_fdr.sum()],
}, index=["CPA (t-test)", "Conversion rate (Fisher)", "Conversion rate (weekly t-test)",
          "CPA, last 13 weeks (t-test)"])
print(summary.to_string())
summary.to_csv(RESULTS / "correction_summary.csv")

fig, ax = plt.subplots(figsize=(10, 5))
summary[["uncorrected", "bonferroni", "fdr_bh"]].plot.bar(ax=ax, color=["#d62728", "#1f77b4", "#2ca02c"],
                                                           rot=0, width=0.75)
ax.set_xticklabels([t.get_text().replace(" (", "\n(") for t in ax.get_xticklabels()])
ax.axhline(15, color="grey", ls="--", lw=1)
ax.text(3.45, 15.2, "15 pairs tested per family", ha="right", color="grey")
for c in ax.containers:
    ax.bar_label(c)
ax.set_ylabel("Significant pairs (of 15)")
ax.set_ylim(0, 17)
ax.set_title("Effect of multiple-comparisons correction", fontweight="bold")
ax.legend(ax.containers, ["Uncorrected (alpha=0.05)", "Bonferroni", "Benjamini-Hochberg FDR"], loc="lower left")
fig.tight_layout()
fig.savefig(FIGS / "correction_comparison.png", dpi=130)
plt.close(fig)

cpa.to_csv(RESULTS / "cpa_ttests.csv", index=False)
cvr_t.to_csv(RESULTS / "cvr_ttests.csv", index=False)
fisher.to_csv(RESULTS / "cvr_fisher.csv", index=False)

section("KEY INSIGHTS")
ns = cpa[~cpa.significant_fdr]
print(f"- {cpa.significant_fdr.sum()}/15 CPA gaps survive FDR; exceptions: "
      + ("; ".join(f"{r.group_a} vs {r.group_b} (p_fdr={r.p_value_fdr:.2f}, d={r.cohens_d:+.2f})"
                   for r in ns.itertuples()) or "none") + ".")
print("- These channels differ by multiples, not percentages, so correction barely changes the picture.")
print("  Its value shows up exactly at the margin: the near-tied mid-tier pairs.")
print("- FDR is the better default for a budget review (we accept a few false leads to keep power);")
print("  Bonferroni fits when a single false positive is costly, e.g. killing a channel outright.")
print("\nSaved results/*.csv and figures/metric_comparison_heatmap.png, rate_comparison.png, "
      "correction_comparison.png")
