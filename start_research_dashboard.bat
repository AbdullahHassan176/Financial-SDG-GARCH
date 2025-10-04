@echo off
echo Starting NF-GARCH Research Dashboard...
echo.

REM Check if we're in the right directory
if not exist "docs\research_dashboard.html" (
    echo Generating research dashboard...
    python tools\create_research_dashboard.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to generate research dashboard
        pause
        exit /b 1
    )
)

echo Starting local web server...
echo.
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.

cd docs
python -m http.server 8000
