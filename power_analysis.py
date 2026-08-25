"""
Part 4: power analysis and sample size planning.

The lab template hard-codes the simulated CPA standard deviation at 15% of the
mean. That would make the sample-size answer an artefact of an assumption. Here
the coefficient of variation is measured from the data first and then used. It
happens to land at 0.144, close to the template's 0.15, but it is verified
rather than assumed, and the sensitivity of the answer to that choice is shown.

Outputs:
  outputs/power_grid.csv
  outputs/mde_table.csv
  outputs/power_adequacy_significant_pairs.csv
  figures/power_analysis_cpa.png
"""

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(42)
ALPHA = 0.05
TARGET_POWER = 0.80
N_SIM = 1000
CURRENT_DAYS = 28  # this dataset, not the 90 the template assumes

df = pd.read_csv("data/marketing_data.csv")
cpa = df.dropna(subset=["cpa"])

# ------------------------------------------------- measured variability
per_campaign = cpa.groupby("campaign_name")["cpa"].agg(["count", "mean", "std"])
per_campaign["cv"] = per_campaign["std"] / per_campaign["mean"]
OBSERVED_CV = float(per_campaign["cv"].median())
BASE_CPA = float(per_campaign["mean"].median())

print("=" * 72)
print("OBSERVED DAILY CPA VARIABILITY (input to the simulation)")
print("=" * 72)
print(per_campaign.round(3).to_string())
print(f"\nmedian coefficient of variation: {OBSERVED_CV:.3f}")
print(f"median campaign CPA (simulation baseline): {BASE_CPA:,.0f}")
print(f"template assumption was 0.150; measured value is used instead")
print(f"note: usable days per campaign range "
      f"{int(per_campaign['count'].min())} to {int(per_campaign['count'].max())} "
      f"because zero-order days drop out")


def empirical_power_cpa(true_diff_pct, base_cpa=BASE_CPA, n_days=CURRENT_DAYS,
                        cv=OBSERVED_CV, n_sim=N_SIM, alpha=ALPHA):
    """Proportion of simulated experiments that reject H0 at alpha."""
    sd = base_cpa * cv
    mean_b = base_cpa * (1 + true_diff_pct)
    a = np.clip(rng.normal(base_cpa, sd, (n_sim, n_days)), base_cpa * 0.5, None)
    b = np.clip(rng.normal(mean_b, sd, (n_sim, n_days)), mean_b * 0.5, None)
    _, p = stats.ttest_ind(a, b, axis=1, equal_var=False)
    return float((p < alpha).mean())


# ------------------------------------------------------------- power grid
effects = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [14, 28, 60, 90, 120, 180]
rows = []
for e in effects:
    for n in sample_sizes:
        rows.append(dict(effect_size_pct=int(e * 100), n_days=n,
                         power=empirical_power_cpa(e, n_days=n)))
grid = pd.DataFrame(rows)
grid.to_csv("outputs/power_grid.csv", index=False)

print("\n" + "=" * 72)
print("POWER TO DETECT A CPA DIFFERENCE (simulated, measured variability)")
print("=" * 72)
print(grid.pivot(index="n_days", columns="effect_size_pct", values="power")
      .round(3).to_string())

# sensitivity: what if variability were higher than the median campaign
print("\nsensitivity of power at 28 days to the assumed CV:")
for cv in [0.11, OBSERVED_CV, 0.20, 0.30]:
    p10 = empirical_power_cpa(0.10, cv=cv, n_days=CURRENT_DAYS)
    p20 = empirical_power_cpa(0.20, cv=cv, n_days=CURRENT_DAYS)
    print(f"  CV {cv:.3f}: power at 10% diff = {p10:.2f}, at 20% diff = {p20:.2f}")

# ------------------------------------------------------- minimum sample size
print("\n" + "=" * 72)
print(f"MINIMUM DAYS FOR {TARGET_POWER:.0%} POWER")
print("=" * 72)
mde_rows = []
for e in effects:
    need = None
    for n in range(5, 401, 5):
        if empirical_power_cpa(e, n_days=n, n_sim=400) >= TARGET_POWER:
            need = n
            break
    mde_rows.append(dict(effect_size_pct=int(e * 100), min_days_for_80pct=need,
                         current_days=CURRENT_DAYS,
                         status="sufficient" if need and need <= CURRENT_DAYS
                         else "insufficient"))
mde = pd.DataFrame(mde_rows)
mde.to_csv("outputs/mde_table.csv", index=False)
print(mde.to_string(index=False))

# smallest detectable difference at 28 days
detectable = None
for e in np.arange(0.02, 0.51, 0.01):
    if empirical_power_cpa(float(e), n_days=CURRENT_DAYS, n_sim=600) >= TARGET_POWER:
        detectable = e
        break
print(f"\nsmallest CPA difference detectable at 80% power with "
      f"{CURRENT_DAYS} days: about {detectable:.0%}")

# ------------------------------------------------------------- power curves
fig, ax = plt.subplots(figsize=(10, 6))
for e in effects:
    sub = grid[grid.effect_size_pct == int(e * 100)]
    ax.plot(sub.n_days, sub.power, marker="o", label=f"{int(e*100)}% CPA difference")
ax.axhline(0.80, color="red", ls="--", lw=1, label="80% power target")
ax.axvline(CURRENT_DAYS, color="grey", ls=":", lw=1.5,
           label=f"this dataset ({CURRENT_DAYS} days)")
ax.set_xlabel("days of data per campaign")
ax.set_ylabel("statistical power")
ax.set_title(f"Power to detect CPA differences\n"
             f"(simulated with measured CV = {OBSERVED_CV:.3f}, alpha = 0.05)")
ax.set_ylim(0, 1.02)
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("figures/power_analysis_cpa.png", dpi=150)
plt.close(fig)

# --------------------------------- adequacy for the pairs we called significant
print("\n" + "=" * 72)
print("ADEQUACY CHECK ON PAIRS THAT SURVIVED FDR CORRECTION")
print("=" * 72)
res = pd.read_csv("outputs/ttest_cpa_campaign.csv")
sig = res[res.significant_fdr].copy()
rows = []
for _, r in sig.iterrows():
    base = min(r.mean_a, r.mean_b)
    obs_pct = abs(r.mean_b - r.mean_a) / base
    pw = empirical_power_cpa(float(obs_pct), base_cpa=base,
                             n_days=CURRENT_DAYS, n_sim=500)
    need = None
    if pw < TARGET_POWER:
        for n in range(5, 401, 5):
            if empirical_power_cpa(float(obs_pct), base_cpa=base,
                                   n_days=n, n_sim=300) >= TARGET_POWER:
                need = n
                break
    rows.append(dict(group_a=r.group_a, group_b=r.group_b,
                     observed_pct_diff=round(100 * obs_pct, 1),
                     cohens_d=round(r.cohens_d, 2),
                     power_at_28_days=round(pw, 3),
                     days_needed_for_80pct=need))
adequacy = pd.DataFrame(rows).sort_values("power_at_28_days")
adequacy.to_csv("outputs/power_adequacy_significant_pairs.csv", index=False)
print(f"{len(sig)} pairs survived FDR. Underpowered pairs shown first:")
print(adequacy.head(15).to_string(index=False))
n_under = int((adequacy.power_at_28_days < TARGET_POWER).sum())
print(f"\npairs with power below {TARGET_POWER:.0%} despite being 'significant': {n_under}")
print("\nPart 4 complete.")
