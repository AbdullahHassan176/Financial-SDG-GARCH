@echo off
echo Updating NF-GARCH Research Dashboard...
python tools/create_nf_garch_dashboard.py
echo.
echo Dashboard updated! Opening in browser...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
