@echo off
echo ========================================
echo COMPREHENSIVE NF-GARCH RESEARCH DASHBOARD
echo ========================================
echo.
echo This dashboard includes:
echo - Model Performance Analysis
echo - Risk Assessment (VaR backtesting)
echo - Stress Testing and Scenario Generation
echo - Stylized Facts Analysis
echo - Quantitative Metrics (RMSE, MAE, AIC/BIC, Q-statistics, ARCH-LM)
echo - Distributional Metrics (KS distance, Wasserstein, KL/JS divergence)
echo - Engine Analysis (Manual vs RUGARCH)
echo - Complete Model Comparison
echo.
echo Step 1: Extracting NF-GARCH data...
python tools/extract_nf_garch_data.py
echo.
echo Step 2: Fixing model classification...
python tools/fix_nf_garch_classification.py
echo.
echo Step 3: Creating comprehensive dashboard...
python tools/create_comprehensive_dashboard.py
echo.
echo ========================================
echo COMPREHENSIVE DASHBOARD READY!
echo ========================================
echo.
echo The dashboard now includes:
echo - ALL model types (sGARCH, eGARCH, gjrGARCH, TGARCH, fGARCH)
echo - Engine information (Manual vs RUGARCH)
echo - Complete risk assessment
echo - Stress testing results
echo - Stylized facts analysis
echo - Quantitative and distributional metrics
echo - Comprehensive model comparison
echo.
echo Opening dashboard in browser...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
