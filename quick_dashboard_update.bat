@echo off
echo Quick Dashboard Update...
echo.

python tools\create_simple_dashboard.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to update dashboard
    pause
    exit /b 1
)

echo Dashboard updated successfully!
echo.
echo To view: http://localhost:8000/research_dashboard.html
echo.
