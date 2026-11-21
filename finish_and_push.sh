#!/usr/bin/env bash
# End-to-end validate, run public dataset, then GitHub publish.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${1:-sean173-lang/lab-statistical-analysis}"
command -v gh >/dev/null || { echo 'Install GitHub CLI (gh) first'; exit 1; }
gh auth status >/dev/null 2>&1 || { echo 'GitHub CLI not signed in; run gh auth login'; exit 1; }
cd "$SRC"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip -q install -r requirements.txt
printf '\n==> Running all unit tests\n'
.venv/bin/python -m unittest discover -s tests -v
printf '\n==> Downloading/exploring external Hugging Face dataset\n'
.venv/bin/python run_lab.py --source hf
printf '\n==> Verifying source-data outputs and exact budget\n'
.venv/bin/python - <<'PY'
import json
from pathlib import Path
import pandas as pd
p=Path('results/data_audit.json'); d=json.loads(p.read_text())
assert 'huggingface.co' in d['source'] and d['analysis_rows']>100
assert d['unique_channels']==7
assert d['synthetic'] is True
assert pd.read_csv('results/budget_allocation_500k.csv')['monthly_budget_usd'].sum()==500_000
for f in ['data/marketing_data.csv','executive_memo.md','lab_proof.md','results/daily_cpa_comparisons.csv','results/fisher_conversion_comparisons.csv','results/power_curve.csv','figures/power_analysis_cpa.png']:
    assert Path(f).stat().st_size>0,f
assert 'pending source-data' not in Path('lab_proof.md').read_text()
print(f"Verified: {d['source_rows_in_window']} source rows in window, {d['analysis_rows']} channel-days, 7 observed delivery segments")
PY
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  echo "Creating a new public lab repository: $REPO"
  gh repo create "$REPO" --public --description 'Ironhack statistical marketing lab: rigorous seven-segment analysis and $500K allocation' || exit 1
else
  echo "Reusing existing GitHub repository: $REPO"
fi
TEMPDIR="$(mktemp -d)"
trap 'rm -rf "$TEMPDIR"' EXIT
# Preserve any remote commits, e.g. initial lab scaffold. Never force-push.
gh repo clone "$REPO" "$TEMPDIR/repo" -- --quiet
if ! git -C "$TEMPDIR/repo" show-ref --verify --quiet refs/heads/main; then
  git -C "$TEMPDIR/repo" switch -c main
else
  git -C "$TEMPDIR/repo" switch main
fi
rsync -a "$SRC/" "$TEMPDIR/repo/" \
 --exclude='.git' --exclude='.venv' --exclude='venv' --exclude='__pycache__' \
 --exclude='.DS_Store' --exclude='.env' --exclude='.env.*' --exclude='*.pyc' \
 --exclude='demo_data/' --exclude='demo_results/' --exclude='demo_figures/' \
 --exclude='lab_proof_demo.md' --exclude='executive_memo_demo.md' \
 --exclude='digital_marketing_dataset_30k.csv' \
 --exclude='*.log'
cd "$TEMPDIR/repo"
# Check no obvious secrets got staged.
git add -A
if git diff --cached --name-only | grep -E '(^|/)\.env$|(^|/)\.venv/' >/dev/null; then echo 'Refusing to commit secrets'; exit 1; fi
if git diff --cached --quiet; then
  echo 'Already up to date; no new commit.'
else
  git commit -m 'Complete seven-segment marketing statistics lab with source-derived analysis'
  git push -u origin main
fi
printf '\nSUCCESS: https://github.com/%s\n' "$REPO"
printf 'Original project folder was not modified by Git operations.\n'
