@echo off
echo ========================================
echo FIXING FINAL MODEL COUNT
echo ========================================
echo.
echo This will fix the model count to match your actual implementation:
echo - 4 Standard GARCH models: sGARCH, eGARCH, gjrGARCH, TGARCH
echo - 4 NF-GARCH models: NF_sGARCH, NF_eGARCH, NF_gjrGARCH, fGARCH
echo - Total: 8 models (missing NF_TGARCH)
echo - sGARCH_norm and sGARCH_sstd are distribution variants, not separate models
echo.
echo Running model count fix...
python tools/fix_correct_model_count.py
echo.
echo ========================================
echo FINAL MODEL COUNT FIXED!
echo ========================================
echo.
echo The dashboard now shows:
echo - 4 Standard GARCH models (not 6!)
echo - 4 NF-GARCH models (not 5!)
echo - Total: 8 models (not 10!)
echo - Correct model classification
echo.
echo Opening final dashboard...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
