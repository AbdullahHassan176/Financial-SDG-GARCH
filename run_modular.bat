@echo off
REM Modular Pipeline Execution Script
REM Checkpointed version of run_all.bat with component isolation
REM Allows independent execution of pipeline components with checkpointing

echo ========================================
echo MODULAR NF-GARCH PIPELINE
echo ========================================

REM Initialize checkpointing
if not exist "checkpoints" mkdir checkpoints
if not exist "checkpoints\pipeline_status.json" (
    echo {} > checkpoints\pipeline_status.json
)
if not exist "results\consolidated" mkdir results\consolidated

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

REM Component execution functions
:run_component
set component=%1
echo.
echo ========================================
echo RUNNING COMPONENT: %component%
echo ========================================

if "%component%"=="pipeline_diagnostic" (
    echo Running pipeline diagnostic...
    Rscript scripts\utils\pipeline_diagnostic.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "pipeline_diagnostic" "Pipeline diagnostic failed"
        echo ERROR: Pipeline diagnostic failed
        exit /b 1
    ) else (
        call :checkpoint_completed "pipeline_diagnostic"
    )
) else if "%component%"=="eda" (
    echo Running EDA...
    Rscript scripts\eda\eda_summary_stats.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "eda" "EDA failed"
        echo ERROR: EDA failed
        exit /b 1
    ) else (
        call :checkpoint_completed "eda"
    )
) else if "%component%"=="garch_fitting" (
    echo Fitting GARCH models with Time Series Cross-Validation...
    Rscript scripts\model_fitting\fit_garch_models.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "garch_fitting" "GARCH fitting failed"
        echo ERROR: GARCH fitting failed
        exit /b 1
    ) else (
        call :checkpoint_completed "garch_fitting"
    )
) else if "%component%"=="residual_extraction" (
    echo Extracting residuals...
    Rscript scripts\model_fitting\extract_residuals.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "residual_extraction" "Residual extraction failed"
        echo ERROR: Residual extraction failed
        exit /b 1
    ) else (
        call :checkpoint_completed "residual_extraction"
    )
) else if "%component%"=="nf_training" (
    echo Training NF models...
    python scripts\model_fitting\train_nf_models.py
    if %errorlevel% neq 0 (
        call :checkpoint_failed "nf_training" "NF training failed"
        echo ERROR: NF training failed
        exit /b 1
    ) else (
        call :checkpoint_completed "nf_training"
    )
) else if "%component%"=="nf_evaluation" (
    echo Evaluating NF models...
    python scripts\model_fitting\evaluate_nf_fit.py
    if %errorlevel% neq 0 (
        call :checkpoint_failed "nf_evaluation" "NF evaluation failed"
        echo ERROR: NF evaluation failed
        exit /b 1
    ) else (
        call :checkpoint_completed "nf_evaluation"
    )
) else if "%component%"=="nf_garch_manual" (
    echo Running NF-GARCH simulation (MANUAL engine)...
    Rscript scripts\simulation_forecasting\simulate_nf_garch_engine.R --engine manual
    if %errorlevel% neq 0 (
        call :checkpoint_failed "nf_garch_manual" "Manual engine simulation failed"
        echo ERROR: Manual engine simulation failed
        exit /b 1
    ) else (
        call :checkpoint_completed "nf_garch_manual"
    )
) else if "%component%"=="forecasting" (
    echo Running forecasts...
    Rscript scripts\simulation_forecasting\forecast_garch_variants.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "forecasting" "Forecasting failed"
        echo ERROR: Forecasting failed
        exit /b 1
    ) else (
        call :checkpoint_completed "forecasting"
    )
) else if "%component%"=="forecast_evaluation" (
    echo Evaluating forecasts...
    Rscript scripts\evaluation\wilcoxon_winrate_analysis.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "forecast_evaluation" "Forecast evaluation failed"
        echo ERROR: Forecast evaluation failed
        exit /b 1
    ) else (
        call :checkpoint_completed "forecast_evaluation"
    )
) else if "%component%"=="stylized_facts" (
    echo Running stylized fact tests...
    Rscript scripts\evaluation\stylized_fact_tests.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "stylized_facts" "Stylized fact tests failed"
        echo ERROR: Stylized fact tests failed
        exit /b 1
    ) else (
        call :checkpoint_completed "stylized_facts"
    )
) else if "%component%"=="var_backtesting" (
    echo Running VaR backtesting...
    Rscript scripts\evaluation\var_backtesting.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "var_backtesting" "VaR backtesting failed"
        echo ERROR: VaR backtesting failed
        exit /b 1
    ) else (
        call :checkpoint_completed "var_backtesting"
    )
) else if "%component%"=="nfgarch_var_backtesting" (
    echo Running NFGARCH VaR backtesting...
    Rscript scripts\evaluation\nfgarch_var_backtesting.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "nfgarch_var_backtesting" "NFGARCH VaR backtesting failed"
        echo ERROR: NFGARCH VaR backtesting failed
        exit /b 1
    ) else (
        call :checkpoint_completed "nfgarch_var_backtesting"
    )
) else if "%component%"=="stress_testing" (
    echo Running stress tests...
    Rscript scripts\stress_tests\evaluate_under_stress.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "stress_testing" "Stress tests failed"
        echo ERROR: Stress tests failed
        exit /b 1
    ) else (
        call :checkpoint_completed "stress_testing"
    )
) else if "%component%"=="nfgarch_stress_testing" (
    echo Running NFGARCH stress testing...
    Rscript scripts\evaluation\nfgarch_stress_testing.R
    if %errorlevel% neq 0 (
        call :checkpoint_failed "nfgarch_stress_testing" "NFGARCH stress testing failed"
        echo ERROR: NFGARCH stress testing failed
        exit /b 1
    ) else (
        call :checkpoint_completed "nfgarch_stress_testing"
    )
) else if "%component%"=="final_summary" (
    echo Generating final summary...
    Rscript -e "library(openxlsx); cat('=== NF-GARCH PIPELINE SUMMARY ===\n'); cat('Date:', Sys.Date(), '\n'); cat('Time:', Sys.time(), '\n\n'); output_files <- list.files('outputs', recursive = TRUE, full.names = TRUE); cat('Output files generated:', length(output_files), '\n'); nf_files <- list.files('nf_generated_residuals', pattern = '*.csv', full.names = TRUE); cat('NF residual files:', length(nf_files), '\n'); result_files <- list.files(pattern = '*Results*.xlsx', full.names = TRUE); cat('Result files:', length(result_files), '\n'); cat('\n=== PIPELINE COMPLETE ===\n')"
    if %errorlevel% neq 0 (
        call :checkpoint_failed "final_summary" "Final summary generation failed"
        echo ERROR: Final summary generation failed
        exit /b 1
    ) else (
        call :checkpoint_completed "final_summary"
    )
) else if "%component%"=="consolidation" (
    echo Consolidating all results into comprehensive Excel document...
    Rscript -e "source('scripts/core/consolidation.R'); consolidate_all_results(output_dir = 'results/consolidated')"
    if %errorlevel% neq 0 (
        call :checkpoint_failed "consolidation" "Results consolidation failed"
        echo ERROR: Results consolidation failed
        exit /b 1
    ) else (
        call :checkpoint_completed "consolidation"
    )
) else if "%component%"=="validation" (
    echo Validating pipeline results...
    python scripts\utils\validate_pipeline.py
    if %errorlevel% neq 0 (
        call :checkpoint_failed "validation" "Pipeline validation failed"
        echo ERROR: Pipeline validation failed
        exit /b 1
    ) else (
        call :checkpoint_completed "validation"
    )
) else if "%component%"=="appendix_log" (
    echo Generating appendix log...
    python scripts\utils\generate_appendix_log.py
    if %errorlevel% neq 0 (
        call :checkpoint_failed "appendix_log" "Appendix log generation failed"
        echo ERROR: Appendix log generation failed
        exit /b 1
    ) else (
        call :checkpoint_completed "appendix_log"
    )
) else (
    echo ERROR: Unknown component '%component%'
    echo Available components:
    echo   pipeline_diagnostic, eda, garch_fitting, residual_extraction
    echo   nf_training, nf_evaluation, nf_garch_manual, forecasting
    echo   forecast_evaluation, stylized_facts, var_backtesting
    echo   nfgarch_var_backtesting, stress_testing, nfgarch_stress_testing
    echo   final_summary, consolidation, validation, appendix_log
    exit /b 1
)
goto :eof

REM Main execution logic
if "%1"=="" (
    echo Running full modular pipeline...
    echo.
    echo ========================================
    echo FULL PIPELINE EXECUTION
    echo ========================================
    echo.
    
    REM Run all components in sequence
    call :run_component "pipeline_diagnostic"
    call :run_component "eda"
    call :run_component "garch_fitting"
    call :run_component "residual_extraction"
    call :run_component "nf_training"
    call :run_component "nf_evaluation"
    call :run_component "nf_garch_manual"
    call :run_component "forecasting"
    call :run_component "forecast_evaluation"
    call :run_component "stylized_facts"
    call :run_component "var_backtesting"
    call :run_component "nfgarch_var_backtesting"
    call :run_component "stress_testing"
    call :run_component "nfgarch_stress_testing"
    call :run_component "final_summary"
    call :run_component "consolidation"
    call :run_component "validation"
    call :run_component "appendix_log"
    
    echo.
    echo ========================================
    echo FULL PIPELINE COMPLETE!
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
    echo.
    echo COMPARISON TABLES INCLUDED:
    echo - Split_Comparison: Direct comparison of Chrono vs TS CV performance
    echo - Performance_Comparison: Ranking comparison between methods
    echo - Asset_Comparison: Asset-level performance differences
    echo.
    echo Both MANUAL and RUGARCH engines tested with Chronological and Time Series Cross-Validation comparison.
    echo.
    
) else if "%1"=="status" (
    echo Checking pipeline status...
    echo.
    if exist "checkpoints\pipeline_status.json" (
        Rscript -e "library(jsonlite); cp <- fromJSON('checkpoints/pipeline_status.json'); if(length(cp) > 0) { cat('=== PIPELINE STATUS ===\n'); for(i in names(cp)) { cat(sprintf('%-20s: %s (%s)\n', i, cp[[i]]$status, cp[[i]]$timestamp)) }; cat('\n') } else { cat('No checkpoints found.\n') }"
    ) else (
        echo No checkpoints found.
    )
    
) else if "%1"=="run" (
    if "%2"=="" (
        echo ERROR: Please specify a component to run
        echo.
        echo Available components:
        echo   pipeline_diagnostic - Run pipeline diagnostic
        echo   eda                - EDA analysis
        echo   garch_fitting      - Standard GARCH model fitting (includes TS CV)
        echo   residual_extraction - Extract residuals for NF training
        echo   nf_training        - Python NF model training
        echo   nf_evaluation      - NF model evaluation
        echo   nf_garch_manual    - NF-GARCH with manual engine
        echo   forecasting        - Forecasting evaluation
        echo   forecast_evaluation - Evaluate forecasts (Wilcoxon)
        echo   stylized_facts     - Stylized facts analysis
        echo   var_backtesting    - VaR backtesting
        echo   nfgarch_var_backtesting - NFGARCH VaR backtesting
        echo   stress_testing     - Stress testing
        echo   nfgarch_stress_testing - NFGARCH stress testing
        echo   final_summary      - Generate final summary
        echo   consolidation      - Final results consolidation
        echo   validation         - Pipeline validation
        echo   appendix_log       - Generate appendix log
        echo.
        echo EXAMPLES:
        echo   run_modular.bat run nf_garch_manual
        echo   run_modular.bat run garch_fitting
        echo   run_modular.bat status
        exit /b 1
    ) else (
        call :run_component "%2"
    )
    
) else if "%1"=="reset" (
    if "%2"=="" (
        echo ERROR: Please specify a component to reset
        echo.
        echo Available components:
        echo   pipeline_diagnostic, eda, garch_fitting, residual_extraction
        echo   nf_training, nf_evaluation, nf_garch_manual, forecasting
        echo   forecast_evaluation, stylized_facts, var_backtesting
        echo   nfgarch_var_backtesting, stress_testing, nfgarch_stress_testing
        echo   final_summary, consolidation, validation, appendix_log
        echo.
        echo EXAMPLES:
        echo   run_modular.bat reset nf_training
        echo   run_modular.bat reset garch_fitting
        exit /b 1
    ) else (
        echo Resetting component: %2
        Rscript -e "library(jsonlite); if(file.exists('checkpoints/pipeline_status.json')) { cp <- fromJSON('checkpoints/pipeline_status.json'); cp[['%2']] <- NULL; writeLines(toJSON(cp, auto_unbox=TRUE, pretty=TRUE), 'checkpoints/pipeline_status.json'); cat('Component %2 reset.\n') } else { cat('No checkpoints found.\n') }"
    )
    
) else if "%1"=="help" (
    echo.
    echo USAGE:
    echo   run_modular.bat                    - Run full pipeline
    echo   run_modular.bat status             - Show pipeline status
    echo   run_modular.bat run <component>    - Run specific component
    echo   run_modular.bat reset <component>  - Reset component
    echo   run_modular.bat help               - Show this help
    echo.
    echo COMPONENTS:
    echo   pipeline_diagnostic - Run pipeline diagnostic
    echo   eda                - EDA analysis
    echo   garch_fitting      - Standard GARCH model fitting (includes TS CV)
    echo   residual_extraction - Extract residuals for NF training
    echo   nf_training        - Python NF model training
    echo   nf_evaluation      - NF model evaluation
    echo   nf_garch_manual    - NF-GARCH with manual engine
    echo   forecasting        - Forecasting evaluation
    echo   forecast_evaluation - Evaluate forecasts (Wilcoxon)
    echo   stylized_facts     - Stylized facts analysis
    echo   var_backtesting    - VaR backtesting
    echo   nfgarch_var_backtesting - NFGARCH VaR backtesting
    echo   stress_testing     - Stress testing
    echo   nfgarch_stress_testing - NFGARCH stress testing
    echo   final_summary      - Generate final summary
    echo   consolidation      - Final results consolidation
    echo   validation         - Pipeline validation
    echo   appendix_log       - Generate appendix log
    echo.
    echo EXAMPLES:
    echo   run_modular.bat run nf_garch_manual
    echo   run_modular.bat reset nf_training
    echo   run_modular.bat status
    echo.
    echo DIFFERENCES FROM run_all.bat:
    echo   - run_all.bat: Full pipeline execution with checkpointing
    echo   - run_modular.bat: Component-based execution with checkpointing
    echo   - Both use identical pipeline steps and checkpointing system
    echo   - run_modular.bat allows selective component execution
    echo.
    
) else (
    echo ERROR: Unknown command '%1'
    echo Run 'run_modular.bat help' for usage information
    exit /b 1
)

echo.
pause