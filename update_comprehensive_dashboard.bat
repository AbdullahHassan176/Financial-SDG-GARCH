@echo off
echo Updating Comprehensive Evaluation Dashboard...
python tools/create_comprehensive_evaluation_dashboard.py
echo.
echo Comprehensive dashboard updated! Opening in browser...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
