from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "marketing_data.csv"
RESULTS_DIR = BASE_DIR / "results"


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

df = pd.read_csv(DATA_FILE)
campaign_ids = sorted(df["xyz_campaign_id"].unique())


# ---------------------------------------------------------
# Bootstrap confidence interval
# ---------------------------------------------------------

def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    values = np.asarray(data)
    bootstrap_means = []

    for _ in range(n_bootstrap):
        sample = np.random.choice(values, size=len(values), replace=True)
        bootstrap_means.append(sample.mean())

    alpha = 1 - ci_level

    lower = np.percentile(bootstrap_means, 100 * alpha / 2)
    upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))

    return lower, upper


# ---------------------------------------------------------
# CPA confidence intervals
# ---------------------------------------------------------

np.random.seed(42)

ci_results = []

for campaign_id in campaign_ids:
    cpa_values = df.loc[
        (df["xyz_campaign_id"] == campaign_id) & df["CPA"].notna(),
        "CPA",
    ]

    lower, upper = bootstrap_ci(cpa_values)

    ci_results.append({
        "campaign": campaign_id,
        "n_cpa_observations": len(cpa_values),
        "mean_cpa": cpa_values.mean(),
        "median_cpa": cpa_values.median(),
        "ci_95_lower": lower,
        "ci_95_upper": upper,
    })

ci_df = pd.DataFrame(ci_results)

print("\n--- CPA CONFIDENCE INTERVALS ---")
print(ci_df.round(2).to_string(index=False))


# ---------------------------------------------------------
# Save confidence intervals
# ---------------------------------------------------------

CI_FILE = RESULTS_DIR / "cpa_confidence_intervals.csv"
ci_df.to_csv(CI_FILE, index=False)

print(f"\nCPA confidence intervals saved to: {CI_FILE}")


# ---------------------------------------------------------
# Load campaign performance
# ---------------------------------------------------------

CAMPAIGN_SUMMARY_FILE = RESULTS_DIR / "campaign_summary.csv"
campaign_summary = pd.read_csv(CAMPAIGN_SUMMARY_FILE)


# ---------------------------------------------------------
# Rank campaigns
# ---------------------------------------------------------

campaign_summary["CPA_rank"] = campaign_summary["CPA"].rank(method="min", ascending=True)
campaign_summary["Purchase_Rate_rank"] = campaign_summary["Purchase_Rate"].rank(method="min", ascending=False)

number_of_campaigns = len(campaign_summary)

campaign_summary["CPA_score"] = number_of_campaigns + 1 - campaign_summary["CPA_rank"]
campaign_summary["Purchase_Rate_score"] = number_of_campaigns + 1 - campaign_summary["Purchase_Rate_rank"]

campaign_summary["composite_score"] = (
    0.7 * campaign_summary["CPA_score"]
    + 0.3 * campaign_summary["Purchase_Rate_score"]
)

# ---------------------------------------------------------
# Initial budget allocation
# ---------------------------------------------------------

MONTHLY_BUDGET = 500_000

campaign_summary["allocation_share"] = (
    campaign_summary["composite_score"]
    / campaign_summary["composite_score"].sum()
)

campaign_summary["allocation_amount"] = (
    campaign_summary["allocation_share"]
    * MONTHLY_BUDGET
)


# ---------------------------------------------------------
# Apply allocation constraint
# ---------------------------------------------------------

MAX_SHARE = 0.45

campaign_summary["final_share"] = campaign_summary["allocation_share"].clip(upper=MAX_SHARE)

remaining_share = 1 - campaign_summary["final_share"].sum()

if remaining_share > 0:
    eligible = campaign_summary["final_share"] < MAX_SHARE
    eligible_scores = campaign_summary.loc[eligible, "composite_score"]

    campaign_summary.loc[eligible, "final_share"] += (
        remaining_share
        * eligible_scores
        / eligible_scores.sum()
    )

campaign_summary["final_budget"] = campaign_summary["final_share"] * MONTHLY_BUDGET


# ---------------------------------------------------------
# Display budget recommendation
# ---------------------------------------------------------

allocation_display = campaign_summary[
    [
        "xyz_campaign_id",
        "CPA",
        "Purchase_Rate",
        "composite_score",
        "final_share",
        "final_budget",
    ]
].copy()

allocation_display["Purchase_Rate"] *= 100
allocation_display["final_share"] *= 100

print("\n--- BUDGET ALLOCATION RECOMMENDATION ---")
print(allocation_display.round(2).to_string(index=False))

print(f"\nTotal allocated: ${campaign_summary['final_budget'].sum():,.2f}")


# ---------------------------------------------------------
# Save budget recommendation
# ---------------------------------------------------------

ALLOCATION_FILE = RESULTS_DIR / "budget_allocation.csv"
campaign_summary.to_csv(ALLOCATION_FILE, index=False)

print(f"\nBudget allocation saved to: {ALLOCATION_FILE}")


# ---------------------------------------------------------
# Evidence-based budget allocation
# ---------------------------------------------------------

MONTHLY_BUDGET = 500_000

recommended_shares = {
    916: 0.35,
    936: 0.45,
    1178: 0.20,
}

campaign_summary["recommended_share"] = campaign_summary["xyz_campaign_id"].map(recommended_shares)
campaign_summary["recommended_budget"] = campaign_summary["recommended_share"] * MONTHLY_BUDGET


# ---------------------------------------------------------
# Display budget recommendation
# ---------------------------------------------------------

allocation_display = campaign_summary[
    ["xyz_campaign_id", "CPA", "Purchase_Rate", "recommended_share", "recommended_budget"]
].copy()

allocation_display["Purchase_Rate"] *= 100
allocation_display["recommended_share"] *= 100

print("\n--- BUDGET ALLOCATION RECOMMENDATION ---")
print(allocation_display.round(2).to_string(index=False))

print(f"\nTotal allocated: ${campaign_summary['recommended_budget'].sum():,.2f}")


# ---------------------------------------------------------
# Save budget recommendation
# ---------------------------------------------------------

ALLOCATION_FILE = RESULTS_DIR / "budget_allocation.csv"
allocation_display.to_csv(ALLOCATION_FILE, index=False)

print(f"\nBudget allocation saved to: {ALLOCATION_FILE}")


