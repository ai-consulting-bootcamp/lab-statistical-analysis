from huggingface_hub import hf_hub_download
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Configuration
# --------------------------------------------------

REPO_ID = "jason1966/alinaboulsi_digital-marketing-performance-dataset"
FILENAME = "digital_marketing_dataset_30k.csv"

OUTPUT_PATH = Path("data/raw/digital_marketing_dataset_30k.csv")


# --------------------------------------------------
# Download
# --------------------------------------------------

print("Downloading marketing dataset...")

file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILENAME,
    repo_type="dataset"
)


# --------------------------------------------------
# Load
# --------------------------------------------------

df = pd.read_csv(file_path)

print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")


# --------------------------------------------------
# Save raw copy
# --------------------------------------------------

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_PATH, index=False)

print(f"Raw dataset saved to: {OUTPUT_PATH}")


# --------------------------------------------------
# Basic validation
# --------------------------------------------------

print("\nDataset validation")
print("-" * 40)

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Missing values:", df.isna().sum().sum())
print("Platforms:", df["platform"].nunique())
print("Date range:", df["date"].min(), "to", df["date"].max())

print("\nPlatforms:")
print(df["platform"].value_counts())