@echo off
REM Stream the datasets from Hugging Face (network, a few minutes)
cd /d "%~dp0"
python fetch_dataset.py
echo.
pause
