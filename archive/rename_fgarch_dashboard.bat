@echo off
echo ========================================
echo RENAMING fGARCH TO NF_TGARCH
echo ========================================
echo.
echo This will rename fGARCH to NF_TGARCH in the dashboard.
echo.
echo Running renaming script...
python tools/rename_fgarch_to_nf_tgarch.py
echo.
echo ========================================
echo RENAMING COMPLETE!
echo ========================================
echo.
echo The dashboard now shows:
echo - Standard GARCH: 4 models (sGARCH, eGARCH, gjrGARCH, TGARCH)
echo - NF-GARCH: 4 models (NF_sGARCH, NF_eGARCH, NF_gjrGARCH, NF_TGARCH)
echo - Total: 8 models
echo.
echo Opening renamed dashboard...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
