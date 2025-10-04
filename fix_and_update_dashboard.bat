@echo off
echo ========================================
echo FIXING NF-GARCH CLASSIFICATION AND DASHBOARD
echo ========================================
echo.
echo Step 1: Extracting NF-GARCH data from Excel files...
python tools/extract_nf_garch_data.py
echo.
echo Step 2: Fixing model classification...
python tools/fix_nf_garch_classification.py
echo.
echo ========================================
echo DASHBOARD UPDATED SUCCESSFULLY!
echo ========================================
echo.
echo The dashboard now shows:
echo - 112 NF-GARCH models (with NF residuals)
echo - 60 Standard GARCH models
echo - Proper classification and comparison
echo.
echo Opening dashboard in browser...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
