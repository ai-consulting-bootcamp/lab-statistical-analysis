#!/bin/bash
# Parts 2-3 - pairwise tests, effect sizes, corrections
cd "$(dirname "$0")"
PY=/opt/homebrew/Caskroom/miniconda/base/envs/bootcamp-env/bin/python
[ -x "$PY" ] || PY=python3
"$PY" statistical_analysis.py
echo; echo "Press any key to close..."; read -n 1 -s
