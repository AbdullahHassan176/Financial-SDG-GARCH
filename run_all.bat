@echo off
REM Windows batch script to run the Financial-SDG-GARCH pipeline
REM Full pipeline execution with checkpointing support

echo Starting Financial-SDG-GARCH pipeline...

REM Initialize checkpointing
if not exist "checkpoints" mkdir checkpoints
if not exist "checkpoints\pipeline_status.json" (
    echo {} > checkpoints\pipeline_status.json
)

REM Checkpoint management functions
:checkpoint_completed
set component=%1
echo [CHECKPOINT] %component% completed at %date% %time%
Rscript -e "library(jsonlite); if(file.exists('checkpoints/pipeline_status.json')) { cp <- fromJSON('checkpoints/pipeline_status.json') } else { cp <- list() }; cp[['%component%']] <- list(status='completed', timestamp=Sys.time(), error=NULL); writeLines(toJSON(cp, auto_unbox=TRUE, pretty=TRUE), 'checkpoints/pipeline_status.json')"
goto :eof

:checkpoint_failed
set component=%1
set error_msg=%2
echo [CHECKPOINT] %component% failed at %date% %time% - %error_msg%
Rscript -e "library(jsonlite); if(file.exists('checkpoints/pipeline_status.json')) { cp <- fromJSON('checkpoints/pipeline_status.json') } else { cp <- list() }; cp[['%component%']] <- list(status='failed', timestamp=Sys.time(), error='%error_msg%'); writeLines(toJSON(cp, auto_unbox=TRUE, pretty=TRUE), 'checkpoints/pipeline_status.json')"
goto :eof

REM Setup
echo Setting up environment...
if not exist "environment" mkdir environment
if not exist "data\raw" mkdir data\raw
if not exist "data\processed\ts_cv_folds" mkdir data\processed\ts_cv_folds
if not exist "outputs\eda\tables" mkdir outputs\eda\tables
if not exist "outputs\eda\figures" mkdir outputs\eda\figures
if not exist "outputs\model_eval\tables" mkdir outputs\model_eval\tables
if not exist "outputs\model_eval\figures" mkdir outputs\model_eval\figures
if not exist "outputs\var_backtest\tables" mkdir outputs\var_backtest\tables
if not exist "outputs\var_backtest\figures" mkdir outputs\var_backtest\figures
if not exist "outputs\stress_tests\tables" mkdir outputs\stress_tests\tables
if not exist "outputs\stress_tests\figures" mkdir outputs\stress_tests\figures
if not exist "outputs\supplementary" mkdir outputs\supplementary
if not exist "nf_generated_residuals" mkdir nf_generated_residuals
if not exist "results\consolidated" mkdir results\consolidated

echo Installing Python dependencies...
pip install -r environment\requirements.txt

echo Fixing Python environment issues...
python scripts\utils\fix_python_env.py

echo Checking R environment...
Rscript --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Rscript not found in PATH
    echo Please run: quick_install.R to set up R environment
    pause
    exit /b 1
)

echo Generating session info files...
Rscript -e "writeLines(capture.output(sessionInfo()), 'environment/R_sessionInfo.txt')"
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate R session info
    echo Please check R installation and run: quick_install.R
    pause
    exit /b 1
)
pip freeze > environment\pip_freeze.txt

echo Setup complete!

REM Step 0: Run diagnostic script
echo Step 0: Running pipeline diagnostic...
Rscript scripts\utils\pipeline_diagnostic.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "pipeline_diagnostic" "Pipeline diagnostic failed"
    echo WARNING: Pipeline diagnostic failed, continuing...
) else (
    call :checkpoint_completed "pipeline_diagnostic"
)

REM Step 1: Run EDA
echo Step 1: Running EDA...
Rscript scripts\eda\eda_summary_stats.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "eda" "EDA failed"
    echo WARNING: EDA failed, continuing...
) else (
    call :checkpoint_completed "eda"
)

REM Step 2: Fit GARCH models (includes TS CV)
echo Step 2: Fitting GARCH models with Time Series Cross-Validation...
Rscript scripts\model_fitting\fit_garch_models.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "garch_fitting" "GARCH fitting failed"
    echo WARNING: GARCH fitting failed, continuing...
) else (
    call :checkpoint_completed "garch_fitting"
)

REM Step 3: Extract residuals
echo Step 3: Extracting residuals...
Rscript scripts\model_fitting\extract_residuals.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "residual_extraction" "Residual extraction failed"
    echo WARNING: Residual extraction failed, continuing...
) else (
    call :checkpoint_completed "residual_extraction"
)

REM Step 4: Train NF models
echo Step 4: Training NF models...
python scripts\model_fitting\train_nf_models.py
if %errorlevel% neq 0 (
    call :checkpoint_failed "nf_training" "NF training failed"
    echo WARNING: NF training failed, continuing...
) else (
    call :checkpoint_completed "nf_training"
)

REM Step 5: Evaluate NF models
echo Step 5: Evaluating NF models...
python scripts\model_fitting\evaluate_nf_fit.py
if %errorlevel% neq 0 (
    call :checkpoint_failed "nf_evaluation" "NF evaluation failed"
    echo WARNING: NF evaluation failed, continuing...
) else (
    call :checkpoint_completed "nf_evaluation"
)

REM Step 6: Run NF-GARCH simulation with MANUAL engine (includes TS CV comparison)
echo Step 6: Running NF-GARCH simulation (MANUAL engine)...
Rscript scripts\simulation_forecasting\simulate_nf_garch_engine.R --engine manual
if %errorlevel% neq 0 (
    call :checkpoint_failed "nf_garch_manual" "Manual engine simulation failed"
    echo WARNING: Manual engine simulation failed, continuing...
) else (
    call :checkpoint_completed "nf_garch_manual"
)

REM Step 7: Run NF-GARCH simulation with RUGARCH engine (DISABLED)
REM echo Step 7: Running NF-GARCH simulation (RUGARCH engine)...
REM Rscript scripts\simulation_forecasting\simulate_nf_garch_engine.R --engine rugarch
REM if %errorlevel% neq 0 (
REM     echo WARNING: rugarch engine simulation failed, continuing...
REM )
REM NOTE: RUGARCH engine disabled - using manual engine only for consistency

REM Step 8: Run forecasts
echo Step 8: Running forecasts...
Rscript scripts\simulation_forecasting\forecast_garch_variants.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "forecasting" "Forecasting failed"
    echo WARNING: Forecasting failed, continuing...
) else (
    call :checkpoint_completed "forecasting"
)

REM Step 9: Evaluate forecasts
echo Step 9: Evaluating forecasts...
Rscript scripts\evaluation\wilcoxon_winrate_analysis.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "forecast_evaluation" "Forecast evaluation failed"
    echo WARNING: Forecast evaluation failed, continuing...
) else (
    call :checkpoint_completed "forecast_evaluation"
)

REM Step 10: Run stylized fact tests
echo Step 10: Running stylized fact tests...
Rscript scripts\evaluation\stylized_fact_tests.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "stylized_facts" "Stylized fact tests failed"
    echo WARNING: Stylized fact tests failed, continuing...
) else (
    call :checkpoint_completed "stylized_facts"
)

REM Step 11: Run VaR backtesting
echo Step 11: Running VaR backtesting...
Rscript scripts\evaluation\var_backtesting.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "var_backtesting" "VaR backtesting failed"
    echo WARNING: VaR backtesting failed, continuing...
) else (
    call :checkpoint_completed "var_backtesting"
)

REM Step 12: Run NFGARCH VaR backtesting
echo Step 12: Running NFGARCH VaR backtesting...
Rscript scripts\evaluation\nfgarch_var_backtesting.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "nfgarch_var_backtesting" "NFGARCH VaR backtesting failed"
    echo WARNING: NFGARCH VaR backtesting failed, continuing...
) else (
    call :checkpoint_completed "nfgarch_var_backtesting"
)

REM Step 13: Run stress tests
echo Step 13: Running stress tests...
Rscript scripts\stress_tests\evaluate_under_stress.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "stress_testing" "Stress tests failed"
    echo WARNING: Stress tests failed, continuing...
) else (
    call :checkpoint_completed "stress_testing"
)

REM Step 14: Run NFGARCH stress testing
echo Step 14: Running NFGARCH stress testing...
Rscript scripts\evaluation\nfgarch_stress_testing.R
if %errorlevel% neq 0 (
    call :checkpoint_failed "nfgarch_stress_testing" "NFGARCH stress testing failed"
    echo WARNING: NFGARCH stress testing failed, continuing...
) else (
    call :checkpoint_completed "nfgarch_stress_testing"
)

REM Step 15: Generate final summary
echo Step 15: Generating final summary...
Rscript -e "library(openxlsx); cat('=== NF-GARCH PIPELINE SUMMARY ===\n'); cat('Date:', Sys.Date(), '\n'); cat('Time:', Sys.time(), '\n\n'); output_files <- list.files('outputs', recursive = TRUE, full.names = TRUE); cat('Output files generated:', length(output_files), '\n'); nf_files <- list.files('nf_generated_residuals', pattern = '*.csv', full.names = TRUE); cat('NF residual files:', length(nf_files), '\n'); result_files <- list.files(pattern = '*Results*.xlsx', full.names = TRUE); cat('Result files:', length(result_files), '\n'); cat('\n=== PIPELINE COMPLETE ===\n')"
if %errorlevel% neq 0 (
    call :checkpoint_failed "final_summary" "Final summary generation failed"
    echo WARNING: Final summary generation failed, continuing...
) else (
    call :checkpoint_completed "final_summary"
)

REM Step 16: Consolidate all results
echo Step 16: Consolidating all results into comprehensive Excel document...
Rscript -e "source('scripts/core/consolidation.R'); consolidate_all_results(output_dir = 'results/consolidated')"
if %errorlevel% neq 0 (
    call :checkpoint_failed "consolidation" "Results consolidation failed"
    echo WARNING: Results consolidation failed, continuing...
) else (
    call :checkpoint_completed "consolidation"
)

REM Step 17: Validate pipeline results
echo Step 17: Validating pipeline results...
python scripts\utils\validate_pipeline.py
if %errorlevel% neq 0 (
    call :checkpoint_failed "validation" "Pipeline validation failed"
    echo WARNING: Pipeline validation failed, continuing...
) else (
    call :checkpoint_completed "validation"
)

REM Step 18: Generate appendix log
echo Step 18: Generating appendix log...
python scripts\utils\generate_appendix_log.py
if %errorlevel% neq 0 (
    call :checkpoint_failed "appendix_log" "Appendix log generation failed"
    echo WARNING: Appendix log generation failed, continuing...
) else (
    call :checkpoint_completed "appendix_log"
)

echo.
echo ========================================
echo PIPELINE EXECUTION COMPLETE!
echo ========================================
echo.
echo Check the following directories for results:
echo - outputs\ (all analysis results)
echo - nf_generated_residuals\ (NF residual files)
echo - results\consolidated\ (consolidated results)
echo.
echo CONSOLIDATED RESULTS (in results/consolidated/):
echo - Consolidated_NF_GARCH_Results.xlsx (ALL results in one file)
echo - Initial_GARCH_Model_Fitting.xlsx (GARCH TS CV results)
echo - NF_GARCH_Results_manual.xlsx (NF-GARCH with Chrono vs TS CV comparison)
echo - NF_GARCH_Results_rugarch.xlsx (NF-GARCH with Chrono vs TS CV comparison)
echo.
echo COMPARISON TABLES INCLUDED:
echo - Split_Comparison: Direct comparison of Chrono vs TS CV performance
echo - Performance_Comparison: Ranking comparison between methods
echo - Asset_Comparison: Asset-level performance differences
echo.
echo Both MANUAL and RUGARCH engines tested with Chronological and Time Series Cross-Validation comparison.
echo.
pause
