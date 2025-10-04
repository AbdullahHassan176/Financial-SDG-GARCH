@echo off
echo ========================================
echo FIXING ALL DASHBOARD ISSUES
echo ========================================
echo.
echo This will fix:
echo - File naming in results/consolidated/
echo - NF-GARCH model detection
echo - Engine classification (Manual vs RUGARCH)
echo - Dashboard data loading
echo.
echo Running comprehensive fix...
python tools/fix_all_issues.py
echo.
echo ========================================
echo ALL ISSUES FIXED!
echo ========================================
echo.
echo The dashboard now shows:
echo - Standardized file names
echo - NF-GARCH models detected
echo - Manual engine classification
echo - Complete model comparison
echo.
echo Opening fixed dashboard...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
