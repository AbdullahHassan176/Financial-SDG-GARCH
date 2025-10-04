@echo off
echo ========================================
echo FIXING MODEL SEPARATION ISSUE
echo ========================================
echo.
echo This will fix the model separation to show:
echo - 5 Standard GARCH models (TGARCH, eGARCH, gjrGARCH, sGARCH, sGARCH_norm, sGARCH_sstd)
echo - 4 NF-GARCH models (NF_sGARCH, NF_gjrGARCH, NF_eGARCH, fGARCH)
echo - Proper model naming to distinguish Standard vs NF-GARCH
echo.
echo Running model separation fix...
python tools/fix_model_separation.py
echo.
echo ========================================
echo MODEL SEPARATION FIXED!
echo ========================================
echo.
echo The dashboard now shows:
echo - 5 Standard GARCH models (not 3!)
echo - 4 NF-GARCH models with proper naming
echo - Clear distinction between model types
echo - Proper engine classification
echo.
echo Opening fixed dashboard...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
