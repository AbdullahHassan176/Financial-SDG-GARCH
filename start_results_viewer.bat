@echo off
echo Starting NF-GARCH Results Viewer...
echo.

REM Check if we're in the right directory
if not exist "docs\index.html" (
    echo ERROR: docs\index.html not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Generate manifest if needed
if not exist "docs\manifest.json" (
    echo Generating manifest...
    python tools\generate_results_site.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to generate manifest
        pause
        exit /b 1
    )
)

echo Starting local web server...
echo.
echo Navigate to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

cd docs
python -m http.server 8000
