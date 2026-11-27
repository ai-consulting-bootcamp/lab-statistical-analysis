"""Download the Kaggle 'Marketing Campaign Performance Dataset' into data/raw/.

Reads KAGGLE_API_TOKEN from the .env file at the repo root (never committed).
Run from anywhere:  python lab_statistical_analysis_elif_yurdakul/scripts/download_dataset.py
"""
import os
import shutil
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_DIR.parent
RAW_DIR = LAB_DIR / "data" / "raw"
DATASET = "manishabhatt22/marketing-campaign-performance-dataset"

# Load .env without printing any secret
env_file = REPO_ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

if not os.environ.get("KAGGLE_API_TOKEN"):
    raise SystemExit("KAGGLE_API_TOKEN not found in .env")

import kagglehub  # imported after the token is in the environment

path = Path(kagglehub.dataset_download(DATASET))
print("Downloaded to Kaggle cache:", path)

RAW_DIR.mkdir(parents=True, exist_ok=True)
for csv in path.glob("*.csv"):
    shutil.copy2(csv, RAW_DIR / csv.name)
    print(f"Copied {csv.name} -> {RAW_DIR / csv.name} ({csv.stat().st_size / 1e6:.1f} MB)")
