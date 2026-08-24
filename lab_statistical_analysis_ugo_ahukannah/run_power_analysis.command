#!/bin/bash
# Part 4 - power curves and sample-size planning
cd "$(dirname "$0")"
PY=/opt/homebrew/Caskroom/miniconda/base/envs/bootcamp-env/bin/python
[ -x "$PY" ] || PY=python3
"$PY" power_analysis.py
echo; echo "Press any key to close..."; read -n 1 -s
