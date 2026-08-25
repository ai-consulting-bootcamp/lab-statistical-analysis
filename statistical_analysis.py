"""
Parts 2 and 3: pairwise comparisons, effect sizes, multiple comparisons correction.

Primary unit of analysis: campaign (11 groups, 55 pairs).
Secondary robustness check: category (4 groups, 6 pairs).

Outputs:
  outputs/ttest_cpa_campaign.csv
  outputs/ttest_roas_campaign.csv
  outputs/ttest_cpa_category.csv
  outputs/fisher_convrate_campaign.csv
  outputs/overdispersion_check.csv
  outputs/correction_summary.csv
  figures/metric_comparison_heatmap.png
  figures/rate_comparison.png
  figures/correction_comparison.png
"""

from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import fisher_exact, false_discovery_control

sns.set_theme(style="whitegrid")
pd.set_option("display.width", 220)
ALPHA = 0.05

df = pd.read_csv("data/marketing_data.csv", parse_dates=["c_date"])


# ------------------------------------------------------------------ helpers
def cohens_d(a, b):
    """Pooled-SD Cohen's d, as specified in the lab instructions."""
    pooled = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return (np.mean(b) - np.mean(a)) / pooled if pooled > 0 else np.nan


def interpret_d(d):
    ad = abs(d)
    if np.isnan(ad):
        return "undefined"
    if ad < 0.2:
        return "negligible"
    if ad < 0.5:
        return "small"
    if ad < 0.8:
        return "medium"
    return "large"


def pairwise_ttests(frame, group_col, metric):
    """
    Welch t-test on daily values for every unordered pair of groups.

    Deviation from the lab template, stated deliberately: the template calls
    ttest_ind() with its default equal_var=True. Daily CPA variance differs by
    an order of magnitude across these campaigns, so Student's assumption of
    equal variances is violated. Welch is used instead and costs nothing when
    variances happen to be equal.
    """
    d = frame[[group_col, metric]].replace([np.inf, -np.inf], np.nan).dropna()
    d = d[d[metric] > 0] if metric in ("cpa",) else d
    rows = []
    for a, b in combinations(sorted(d[group_col].unique()), 2):
        va = d.loc[d[group_col] == a, metric].values
        vb = d.loc[d[group_col] == b, metric].values
        if len(va) < 3 or len(vb) < 3:
            continue
        t, p = stats.ttest_ind(va, vb, equal_var=False)
        diff = vb.mean() - va.mean()
        d_val = cohens_d(va, vb)
        rows.append(
            dict(
                group_a=a, group_b=b, n_a=len(va), n_b=len(vb),
                mean_a=va.mean(), mean_b=vb.mean(),
                difference=diff,
                pct_difference=100 * diff / va.mean() if va.mean() else np.nan,
                t_stat=t, p_value=p,
                cohens_d=d_val, effect_size=interpret_d(d_val),
                significant_raw=p < ALPHA,
            )
        )
    return pd.DataFrame(rows)


def apply_corrections(res, label):
    """Bonferroni and Benjamini and Hochberg FDR within one family of tests."""
    if res.empty:
        return res
    m = len(res)
    res = res.copy()
    res["alpha_bonferroni"] = ALPHA / m
    res["significant_bonferroni"] = res["p_value"] < ALPHA / m
    res["p_value_fdr"] = false_discovery_control(res["p_value"].values, method="bh")
    res["significant_fdr"] = res["p_value_fdr"] < ALPHA
    print(f"\n[{label}] family size m = {m}, Bonferroni alpha = {ALPHA/m:.6f}")
    print(f"  raw p<0.05        : {int(res.significant_raw.sum())}")
    print(f"  Bonferroni        : {int(res.significant_bonferroni.sum())}")
    print(f"  Benjamini Hochberg: {int(res.significant_fdr.sum())}")
    return res


# ------------------------------------------------------------- step 4: t-tests
print("=" * 72)
print("STEP 4  PAIRWISE t-TESTS ON DAILY METRICS (campaign level)")
print("=" * 72)

cpa_res = apply_corrections(pairwise_ttests(df, "campaign_name", "cpa"), "CPA campaign")
roas_res = apply_corrections(pairwise_ttests(df, "campaign_name", "roas"), "ROAS campaign")
cat_res = apply_corrections(pairwise_ttests(df, "category", "cpa"), "CPA category")

print("\nTop 10 CPA comparisons by adjusted significance:")
cols = ["group_a", "group_b", "mean_a", "mean_b", "pct_difference",
        "p_value", "p_value_fdr", "cohens_d", "effect_size", "significant_fdr"]
print(cpa_res.sort_values("p_value")[cols].head(10).round(4).to_string(index=False))

print("\nROAS comparisons surviving FDR:")
sig_roas = roas_res[roas_res.significant_fdr].sort_values("p_value")
print(sig_roas[cols].round(4).to_string(index=False) if len(sig_roas) else "  none")

cpa_res.to_csv("outputs/ttest_cpa_campaign.csv", index=False)
roas_res.to_csv("outputs/ttest_roas_campaign.csv", index=False)
cat_res.to_csv("outputs/ttest_cpa_category.csv", index=False)

# heatmap of raw CPA p-values
groups = sorted(set(cpa_res.group_a) | set(cpa_res.group_b))
mat = pd.DataFrame(np.eye(len(groups)), index=groups, columns=groups)
for _, r in cpa_res.iterrows():
    mat.loc[r.group_a, r.group_b] = r.p_value
    mat.loc[r.group_b, r.group_a] = r.p_value
fig, ax = plt.subplots(figsize=(11, 9))
sns.heatmap(mat, annot=True, fmt=".3f", cmap="RdYlGn", vmin=0, vmax=0.2,
            cbar_kws={"label": "raw p value (red = small)"}, ax=ax,
            annot_kws={"size": 7})
ax.set_title("Pairwise daily CPA comparisons, raw p values\n"
             "(Bonferroni threshold for this family is 0.00091)", fontsize=12)
fig.tight_layout()
fig.savefig("figures/metric_comparison_heatmap.png", dpi=150)
plt.close(fig)

# ------------------------------------------------- step 5: Fisher's exact test
print("\n" + "=" * 72)
print("STEP 5  FISHER'S EXACT TEST ON ORDERS PER CLICK (pooled counts)")
print("=" * 72)

agg = df.groupby("campaign_name").agg(orders=("orders", "sum"),
                                      clicks=("clicks", "sum"))
agg["non_orders"] = agg["clicks"] - agg["orders"]
agg["rate"] = agg["orders"] / agg["clicks"]
print(agg.sort_values("rate", ascending=False).round(5).to_string())

rows = []
for a, b in combinations(sorted(agg.index), 2):
    table = [[int(agg.loc[a, "orders"]), int(agg.loc[a, "non_orders"])],
             [int(agg.loc[b, "orders"]), int(agg.loc[b, "non_orders"])]]
    odds, p = fisher_exact(table, alternative="two-sided")
    ra, rb = agg.loc[a, "rate"], agg.loc[b, "rate"]
    rows.append(dict(group_a=a, group_b=b,
                     orders_a=table[0][0], clicks_a=int(agg.loc[a, "clicks"]),
                     orders_b=table[1][0], clicks_b=int(agg.loc[b, "clicks"]),
                     rate_a=ra, rate_b=rb, difference=rb - ra,
                     pct_difference=100 * (rb - ra) / ra if ra else np.nan,
                     odds_ratio=odds, p_value=p, significant_raw=p < ALPHA))
fisher_res = apply_corrections(pd.DataFrame(rows), "Fisher order rate campaign")
fisher_res.to_csv("outputs/fisher_convrate_campaign.csv", index=False)

# ---- overdispersion diagnostic (the reason not to trust the line above)
print("\n" + "-" * 72)
print("OVERDISPERSION CHECK: pooled Fisher vs a test that respects daily variation")
print("-" * 72)
print("Fisher on pooled clicks assumes every click is an independent Bernoulli\n"
      "draw with a fixed per-campaign rate. Daily order rates are overdispersed,\n"
      "so pooling inflates the effective sample size and shrinks p values.\n"
      "Below: the same pairs tested on 28 daily order rates instead.")

daily_rate_res = pairwise_ttests(df, "campaign_name", "conv_rate")
merged = fisher_res.merge(
    daily_rate_res[["group_a", "group_b", "p_value", "cohens_d"]],
    on=["group_a", "group_b"], suffixes=("_fisher", "_daily"))
merged["fisher_sig_raw"] = merged["p_value_fisher"] < ALPHA
merged["daily_sig_raw"] = merged["p_value_daily"] < ALPHA
flips = merged[merged.fisher_sig_raw & ~merged.daily_sig_raw]
print(f"\npairs significant under pooled Fisher : {int(merged.fisher_sig_raw.sum())} of {len(merged)}")
print(f"pairs significant on daily rates      : {int(merged.daily_sig_raw.sum())} of {len(merged)}")
print(f"pairs Fisher calls significant that daily-rate testing does not: {len(flips)}")
merged.to_csv("outputs/overdispersion_check.csv", index=False)

# rate comparison chart
fig, ax = plt.subplots(figsize=(10, 6))
s = agg["rate"].sort_values()
ax.barh(s.index, s.values * 100, color="#2e86c1")
for i, v in enumerate(s.values * 100):
    ax.text(v + 0.005, i, f"{v:.2f}%", va="center", fontsize=9)
ax.set_xlabel("orders per click (%)")
ax.set_title("Order rate per click by campaign (pooled over 28 days)")
fig.tight_layout()
fig.savefig("figures/rate_comparison.png", dpi=150)
plt.close(fig)

# --------------------------------------------- step 6: correction comparison
print("\n" + "=" * 72)
print("STEP 6  MULTIPLE COMPARISONS SUMMARY")
print("=" * 72)
total = len(cpa_res) + len(fisher_res) + len(roas_res)
print(f"total tests run across families: {total}")
print(f"expected false positives at alpha=0.05 with no correction: {total * ALPHA:.1f}")

summary = pd.DataFrame([
    dict(family="CPA (t-test, daily)", n_tests=len(cpa_res),
         uncorrected=int(cpa_res.significant_raw.sum()),
         bonferroni=int(cpa_res.significant_bonferroni.sum()),
         fdr_bh=int(cpa_res.significant_fdr.sum())),
    dict(family="ROAS (t-test, daily)", n_tests=len(roas_res),
         uncorrected=int(roas_res.significant_raw.sum()),
         bonferroni=int(roas_res.significant_bonferroni.sum()),
         fdr_bh=int(roas_res.significant_fdr.sum())),
    dict(family="Order rate (Fisher, pooled)", n_tests=len(fisher_res),
         uncorrected=int(fisher_res.significant_raw.sum()),
         bonferroni=int(fisher_res.significant_bonferroni.sum()),
         fdr_bh=int(fisher_res.significant_fdr.sum())),
])
print("\n" + summary.to_string(index=False))
summary.to_csv("outputs/correction_summary.csv", index=False)

x = np.arange(len(summary))
w = 0.26
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - w, summary.uncorrected, w, label="uncorrected", color="#c0392b")
ax.bar(x, summary.fdr_bh, w, label="Benjamini Hochberg FDR", color="#e67e22")
ax.bar(x + w, summary.bonferroni, w, label="Bonferroni", color="#27ae60")
ax.set_xticks(x)
ax.set_xticklabels(summary.family, fontsize=9)
ax.set_ylabel("significant comparisons")
ax.set_title("Effect of multiple comparisons correction")
ax.legend()
for i, r in summary.iterrows():
    ax.text(i - w, r.uncorrected + 0.3, str(r.uncorrected), ha="center", fontsize=9)
    ax.text(i, r.fdr_bh + 0.3, str(r.fdr_bh), ha="center", fontsize=9)
    ax.text(i + w, r.bonferroni + 0.3, str(r.bonferroni), ha="center", fontsize=9)
fig.tight_layout()
fig.savefig("figures/correction_comparison.png", dpi=150)
plt.close(fig)

print("\nParts 2 and 3 complete.")
