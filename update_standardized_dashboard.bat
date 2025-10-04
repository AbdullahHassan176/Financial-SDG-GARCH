@echo off
echo Updating Standardized NF-GARCH Research Dashboard...
echo.
echo Step 1: Standardizing output files...
python tools/standardize_outputs.py
echo.
echo Step 2: Creating standardized dashboard...
python tools/create_standardized_dashboard.py
echo.
echo Standardized dashboard updated! Opening in browser...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
