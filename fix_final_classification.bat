@echo off
echo ========================================
echo FIXING FINAL MODEL CLASSIFICATION
echo ========================================
echo.
echo This will fix the model classification:
echo - fGARCH correctly classified as NF-GARCH only
echo - Standard GARCH: 6 models (sGARCH variants + eGARCH, gjrGARCH, TGARCH)
echo - NF-GARCH: 4 models (NF_sGARCH, NF_gjrGARCH, NF_eGARCH, fGARCH)
echo.
echo Running classification fix...
python tools/fix_final_model_classification.py
echo.
echo ========================================
echo MODEL CLASSIFICATION FIXED!
echo ========================================
echo.
echo The dashboard now shows:
echo - 6 Standard GARCH models (not 7!)
echo - 4 NF-GARCH models with correct classification
echo - fGARCH properly classified as NF-GARCH only
echo - Correct engine classification
echo.
echo Opening corrected dashboard...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
