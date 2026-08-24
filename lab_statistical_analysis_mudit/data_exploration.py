"""
Step 2: Load and Explore the Dataset
=====================================
Loads ../data/nykaa_campaign_data.csv, inspects structure/quality, cleans it, and saves
a prepared copy to data/marketing_data.csv for downstream steps.

See dataset_selection.md for the dataset choice and why Campaign_Type is used as the
channel grouping variable.
"""
import os

import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

RAW_PATH = "../data/nykaa_campaign_data.csv"
CLEAN_PATH = "data/marketing_data.csv"
SUMMARY_PATH = "results/data_exploration_summary.csv"

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

# 1. Load ---------------------------------------------------------------
df = pd.read_csv(RAW_PATH)

EXPECTED_COLUMNS = {
    "Campaign_ID", "Campaign_Type", "Target_Audience", "Duration", "Channel_Used",
    "Impressions", "Clicks", "Leads", "Conversions", "Revenue", "Acquisition_Cost",
    "ROI", "Language", "Engagement_Score", "Customer_Segment", "Date",
}
missing = EXPECTED_COLUMNS - set(df.columns)
assert not missing, (
    f"Expected column(s) missing from {RAW_PATH}: {sorted(missing)} — "
    "downstream steps assume these exact source names are present."
)

print("=" * 70)
print("RAW DATA — shape, columns, dtypes")
print("=" * 70)
print("Shape:", df.shape)
print(df.dtypes)
print()
print(df.head())

# 2. Explore structure ----------------------------------------------------
print()
print("=" * 70)
print("DATA QUALITY")
print("=" * 70)
print("Missing values per column:")
print(df.isnull().sum())
print()
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate campaign ids:", df["Campaign_ID"].duplicated().sum())

print()
print("Campaign_Type value counts (grouping variable):")
print(df["Campaign_Type"].value_counts())
print()
print("Target_Audience value counts:")
print(df["Target_Audience"].value_counts())
print()
print("Customer_Segment value counts:")
print(df["Customer_Segment"].value_counts())
print()
print("Channel_Used — top 10 raw values (multi-channel campaigns are comma-separated, "
      "156 distinct combinations; too granular/messy to use as the primary grouping "
      "variable, so Campaign_Type is used instead — see dataset_selection.md):")
print(df["Channel_Used"].value_counts().head(10))

print()
print("Funnel field summaries:")
for col in ["Impressions", "Clicks", "Leads", "Conversions", "Revenue", "Acquisition_Cost", "ROI"]:
    print(f"  {col}: min={df[col].min():,.2f} median={df[col].median():,.2f} max={df[col].max():,.2f}")

# Funnel columns should be monotonically non-increasing per campaign
# (Impressions >= Clicks >= Leads >= Conversions); confirm no rows violate that.
funnel_violations = (
    (df["Clicks"] > df["Impressions"]) | (df["Leads"] > df["Clicks"]) | (df["Conversions"] > df["Leads"])
).sum()
print(f"\nFunnel consistency violations (Conversions <= Leads <= Clicks <= Impressions): {funnel_violations}")

# 3. Clean ------------------------------------------------------------------
# Parse Date (DD-MM-YYYY in the source file).
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

for col in ["Impressions", "Clicks", "Leads", "Conversions", "Revenue", "Acquisition_Cost"]:
    assert (df[col] >= 0).all(), f"Found negative {col} — unexpected."

# Acquisition_Cost is cost-per-acquisition, not a total campaign spend figure — confirmed by
# recomputing ROI as (Revenue - Acquisition_Cost*Conversions) / (Acquisition_Cost*Conversions):
# it matches the source ROI column for 98.6% of rows exactly (2dp) and is within 0.02 for the
# rest (residual rounding, since Acquisition_Cost itself is stored rounded to cents).
# Derive total campaign cost from it so group-level CPA/ROAS/Profit can be computed correctly in key_metrics.py.
df["Total_Cost"] = df["Acquisition_Cost"] * df["Conversions"]

# 4. Summarize prepared data -------------------------------------------------
print()
print("=" * 70)
print("PREPARED DATA SUMMARY")
print("=" * 70)
print("Rows:", len(df))
print("Grouping variable: Campaign_Type —", df["Campaign_Type"].nunique(), "groups")
print(df["Campaign_Type"].value_counts().sort_index())
print()
print("Continuous metrics available: CPA (Acquisition_Cost), CTR, Conversion Rate, ROAS, Profit, Profit Margin")
print("Binary outcome: Conversions (per Click, aggregated by group for Fisher's exact test)")
print()
print("Date range:", df["Date"].min().date(), "to", df["Date"].max().date())
print("Overall conversion rate (conversions / clicks): {:.4%}".format(df["Conversions"].sum() / df["Clicks"].sum()))

# 5. Save quality-check summary -----------------------------------------------
summary_df = pd.DataFrame(
    {
        "check": [
            "rows",
            "missing_values_total",
            "duplicate_rows",
            "duplicate_campaign_ids",
            "funnel_violations",
            "date_range",
            "overall_conversion_rate",
        ],
        "value": [
            len(df),
            int(df.isnull().sum().sum()),
            int(df.duplicated().sum()),
            int(df["Campaign_ID"].duplicated().sum()),
            int(funnel_violations),
            f"{df['Date'].min().date()} to {df['Date'].max().date()}",
            f"{df['Conversions'].sum() / df['Clicks'].sum():.4%}",
        ],
    }
)
group_counts = df["Campaign_Type"].value_counts().sort_index().rename_axis("check").reset_index(name="value")
group_counts["check"] = "group_count_" + group_counts["check"].astype(str)
summary_df = pd.concat([summary_df, group_counts], ignore_index=True)
summary_df.to_csv(SUMMARY_PATH, index=False)
print(f"Saved exploration summary to {SUMMARY_PATH}")

# 6. Save cleaned dataset -------------------------------------------------
df.to_csv(CLEAN_PATH, index=False)
print()
print(f"Saved cleaned dataset to {CLEAN_PATH} ({len(df):,} rows)")
