"""
Step 2: Load and Explore the Dataset
=====================================
Loads ../data/marketing_AB.csv, inspects structure/quality, cleans it, and saves
a prepared copy to data/marketing_data.csv for downstream steps.

See dataset_selection.md for why this dataset has no cost/revenue/CTR
fields and how the grouping variable / metrics were adapted.
"""
import os

import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

RAW_PATH = "../data/marketing_AB.csv"
CLEAN_PATH = "data/marketing_data.csv"
SUMMARY_PATH = "results/data_exploration_summary.csv"

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

# 1. Load ---------------------------------------------------------------
df = pd.read_csv(RAW_PATH)

EXPECTED_COLUMNS = {
    "user id", "test group", "converted", "total ads", "most ads day", "most ads hour",
}
missing = EXPECTED_COLUMNS - set(df.columns)
assert not missing, (
    f"Expected column(s) missing from {RAW_PATH}: {sorted(missing)} — "
    "the rename step below assumes these exact source names are present."
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
print("Duplicate user ids:", df["user id"].duplicated().sum())

print()
print("test group value counts:")
print(df["test group"].value_counts())
print()
print("most ads day value counts:")
print(df["most ads day"].value_counts())
print()
print("total ads summary:")
print(df["total ads"].describe())
print()
print("most ads hour range:", df["most ads hour"].min(), "-", df["most ads hour"].max())

# 3. Clean ------------------------------------------------------------------
# Drop the stray index column exported by the original CSV.
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# Rename to snake_case for easier downstream code.
df = df.rename(
    columns={
        "user id": "user_id",
        "test group": "test_group",
        "total ads": "total_ads",
        "most ads day": "most_ads_day",
        "most ads hour": "most_ads_hour",
    }
)

df["converted"] = df["converted"].astype(bool)

# Enforce a sensible category order for the day-of-week grouping variable.
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df["most_ads_day"] = pd.Categorical(df["most_ads_day"], categories=day_order, ordered=True)

# No missing values and no duplicate user ids were found (confirmed above),
# so no rows are dropped. total_ads has no negative or impossible values.
assert df["total_ads"].min() >= 0, "Found negative total_ads — unexpected."

# 4. Summarize prepared data -------------------------------------------------
print()
print("=" * 70)
print("PREPARED DATA SUMMARY")
print("=" * 70)
print("Rows:", len(df))
print("Grouping variable: most_ads_day —", df["most_ads_day"].nunique(), "groups")
print(df["most_ads_day"].value_counts().sort_index())
print()
print("Secondary grouping variable: test_group —", df["test_group"].nunique(), "groups")
print(df["test_group"].value_counts())
print()
print("Continuous metric: total_ads (ad exposure per user)")
print("Binary outcome: converted")
print()
print("Overall conversion rate: {:.4%}".format(df["converted"].mean()))
print()
print("Date range: not available — this dataset has no date/timestamp column, only the "
      "categorical most_ads_day / most_ads_hour fields (see dataset_selection.md).")

# 5. Save quality-check summary -----------------------------------------------
# A compact, reviewable record of the checks above (group sizes + data quality),
# separate from the console log, so this deliverable doesn't require re-running the script.
summary_df = pd.DataFrame(
    {
        "check": [
            "rows",
            "missing_values_total",
            "duplicate_rows",
            "duplicate_user_ids",
            "date_range",
            "overall_conversion_rate",
        ],
        "value": [
            len(df),
            int(df.isnull().sum().sum()),
            int(df.duplicated().sum()),
            int(df["user_id"].duplicated().sum()),
            "not available (no date column)",
            f"{df['converted'].mean():.4%}",
        ],
    }
)
group_counts = df["most_ads_day"].value_counts().sort_index().rename_axis("check").reset_index(name="value")
group_counts["check"] = "group_count_" + group_counts["check"].astype(str)
summary_df = pd.concat([summary_df, group_counts], ignore_index=True)
summary_df.to_csv(SUMMARY_PATH, index=False)
print(f"Saved exploration summary to {SUMMARY_PATH}")

# 6. Save cleaned dataset -------------------------------------------------
df.to_csv(CLEAN_PATH, index=False)
print()
print(f"Saved cleaned dataset to {CLEAN_PATH} ({len(df):,} rows)")
