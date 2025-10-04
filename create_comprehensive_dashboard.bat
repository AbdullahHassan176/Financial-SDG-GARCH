@echo off
echo ========================================
echo CREATING COMPREHENSIVE DASHBOARD
echo ========================================
echo.
echo This will create a comprehensive dashboard with ALL analysis components:
echo - Model Performance Analysis
echo - Risk Assessment Results
echo - Stress Testing Analysis
echo - Stylized Facts Analysis
echo - Quantitative Metrics
echo - Distributional Metrics
echo - Engine Analysis
echo - Model Comparison
echo.
echo Running comprehensive dashboard creation...
python tools/create_comprehensive_final_dashboard.py
echo.
echo ========================================
echo COMPREHENSIVE DASHBOARD CREATED!
echo ========================================
echo.
echo The dashboard now includes:
echo - 9 comprehensive analysis tabs
echo - Complete data coverage
echo - Interactive charts and tables
echo - Tabbed interface for easy navigation
echo.
echo Opening comprehensive dashboard...
echo Navigate to: http://localhost:8000/research_dashboard.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0docs"
python -m http.server 8000 --directory .
