"""
Step 4: Compare Groups Using t-tests
=======================================
Pairwise independent t-tests on CPA (Acquisition_Cost, the primary cost-efficiency
metric) across the 5 Campaign_Type groups, with Cohen's d effect sizes.
"""
import itertools
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)

os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)

df = pd.read_csv("data/marketing_data.csv")

METRIC = "Acquisition_Cost"  # CPA, per campaign

# 1. Prepare data: no NaN/inf possible here (CPA is a plain cost figure), but
#    filter defensively anyway per the lab's instructions.
clean = df[["Campaign_Type", METRIC]].replace([np.inf, -np.inf], np.nan).dropna()
groups = sorted(clean["Campaign_Type"].unique())

def cohens_d(a, b):
    pooled_std = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return (b.mean() - a.mean()) / pooled_std

def interpret_effect(d):
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    elif ad < 0.5:
        return "small"
    elif ad < 0.8:
        return "medium"
    return "large"

results = []
for group_a, group_b in itertools.combinations(groups, 2):
    a = clean.loc[clean["Campaign_Type"] == group_a, METRIC]
    b = clean.loc[clean["Campaign_Type"] == group_b, METRIC]

    t_stat, p_value = ttest_ind(a, b)
    mean_a, mean_b = a.mean(), b.mean()
    diff = mean_b - mean_a
    pct_diff = (diff / mean_a) * 100
    d = cohens_d(a, b)
    effect = interpret_effect(d)

    results.append(
        {
            "group_a": group_a,
            "group_b": group_b,
            "mean_a": mean_a,
            "mean_b": mean_b,
            "difference": diff,
            "pct_difference": pct_diff,
            "t_statistic": t_stat,
            "p_value": p_value,
            "cohens_d": d,
            "effect_size": effect,
            "significant_uncorrected": p_value < 0.05,
        }
    )
    print(
        f"{group_a:>12} vs {group_b:<12} | mean_a={mean_a:7.2f} mean_b={mean_b:7.2f} "
        f"diff={diff:+7.2f} ({pct_diff:+6.2f}%) | t={t_stat:+7.3f} p={p_value:.4e} | "
        f"d={d:+.3f} ({effect})"
    )

ttest_df = pd.DataFrame(results)
ttest_df.to_csv("results/ttest_results.csv", index=False)

n_sig = ttest_df["significant_uncorrected"].sum()
print()
print(f"Total comparisons: {len(ttest_df)} | Significant at alpha=0.05 (uncorrected): {n_sig}")

# 2. Heatmap of p-values ------------------------------------------------------
n = len(groups)
p_matrix = pd.DataFrame(np.ones((n, n)), index=groups, columns=groups)
for _, row in ttest_df.iterrows():
    p_matrix.loc[row["group_a"], row["group_b"]] = row["p_value"]
    p_matrix.loc[row["group_b"], row["group_a"]] = row["p_value"]
np.fill_diagonal(p_matrix.values, 1.0)

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(p_matrix.values, cmap="RdYlGn_r", vmin=0, vmax=0.05 * 3)
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(groups, rotation=45, ha="right")
ax.set_yticklabels(groups)
for i in range(n):
    for j in range(n):
        val = p_matrix.values[i, j]
        text = f"{val:.3f}" if val >= 0.001 else f"{val:.1e}"
        ax.text(j, i, text, ha="center", va="center", fontsize=8,
                 color="white" if val < 0.05 else "black")
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("p-value (red = significant at p<0.05)")
ax.set_title("Pairwise t-test p-values: CPA by Campaign_Type")
fig.tight_layout()
fig.savefig("figures/metric_comparison_heatmap.png", dpi=150)
plt.close(fig)
print("Saved figures/metric_comparison_heatmap.png")
