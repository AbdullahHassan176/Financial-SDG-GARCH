@echo off
echo Creating working research dashboard...
python tools/create_working_dashboard.py
echo.
echo Dashboard created! Opening in browser...
start "" "http://localhost:8000/research_dashboard.html"
echo.
echo Starting local server...
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
