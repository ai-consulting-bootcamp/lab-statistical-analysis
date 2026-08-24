"""
Step 2: Load and Explore the Dataset
=====================================
Loads ../data/marketing_AB.csv, inspects structure/quality, cleans it, and saves
a prepared copy to data/marketing_data.csv for downstream steps.

See dataset_selection.md for why this dataset has no cost/revenue/CTR
fields and how the grouping variable / metrics were adapted.
"""
import os

import numpy as np
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run correctly regardless of invocation directory

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

RAW_PATH = "../data/marketing_AB.csv"
CLEAN_PATH = "data/marketing_data.csv"

# 1. Load ---------------------------------------------------------------
df = pd.read_csv(RAW_PATH)

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

# 5. Save ---------------------------------------------------------------
df.to_csv(CLEAN_PATH, index=False)
print()
print(f"Saved cleaned dataset to {CLEAN_PATH} ({len(df):,} rows)")
