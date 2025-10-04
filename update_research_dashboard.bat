@echo off
echo Updating NF-GARCH Research Dashboard...
echo.

REM Generate the research dashboard
python tools\create_research_dashboard_v2.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate research dashboard
    pause
    exit /b 1
)

echo Research dashboard updated successfully!
echo.
echo To view the dashboard:
echo 1. Run: start_research_dashboard.bat
echo 2. Or: cd docs && python -m http.server 8000
echo 3. Then visit: http://localhost:8000/research_dashboard.html
echo.
pause
