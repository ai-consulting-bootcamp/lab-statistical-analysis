#!/bin/bash
# Part 1 - explore the data and draw the overview figures
cd "$(dirname "$0")"
PY=/opt/homebrew/Caskroom/miniconda/base/envs/bootcamp-env/bin/python
[ -x "$PY" ] || PY=python3
"$PY" data_exploration.py
echo; echo "Press any key to close..."; read -n 1 -s
