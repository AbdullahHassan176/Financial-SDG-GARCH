# Archive Moves Summary - R and Python Files

## ✅ **SUCCESSFULLY MOVED UNUSED R AND PYTHON FILES TO ARCHIVE**

The following unused .R and .py files have been moved to the `archive/` folder to clean up the main repository:

### **Files Moved to Archive:**

#### **R Files (.R) - 15 files moved**
- `scripts/core/config.R` → `archive/config.R`
- `scripts/core/enhanced_consolidation.R` → `archive/enhanced_consolidation.R`
- `scripts/core/simulation.R` → `archive/simulation.R`
- `scripts/core/utils.R` → `archive/utils.R`
- `scripts/utils/generate_missing_summaries.R` → `archive/generate_missing_summaries.R`
- `scripts/utils/fix_remaining_missing_values.R` → `archive/fix_remaining_missing_values.R`
- `scripts/utils/fix_na_values.R` → `archive/fix_na_values.R`
- `scripts/utils/fill_missing_values.R` → `archive/fill_missing_values.R`
- `scripts/utils/add_nf_model_prefixes.R` → `archive/add_nf_model_prefixes.R`
- `scripts/utils/add_missing_classical_models.R` → `archive/add_missing_classical_models.R`
- `scripts/utils/utils_nf_garch.R` → `archive/utils_nf_garch.R`
- `scripts/simulation_forecasting/simulate_nf_garch_tscv.R` → `archive/simulate_nf_garch_tscv.R`
- `scripts/simulation_forecasting/test_nf_garch_simple.R` → `archive/test_nf_garch_simple.R`
- `scripts/models/garch_manual.R` → `archive/garch_manual.R`

#### **Python Files (.py) - 10 files moved**
- `scripts/core/create_comprehensive_results.py` → `archive/create_comprehensive_results.py`
- `scripts/model_fitting/generate_missing_nf_residuals.py` → `archive/generate_missing_nf_residuals.py`
- `cleanup_repository.py` → `archive/cleanup_repository.py`
- `tools/rename_fgarch_to_nf_tgarch.py` → `archive/rename_fgarch_to_nf_tgarch.py`
- `tools/create_comprehensive_final_dashboard.py` → `archive/create_comprehensive_final_dashboard.py`
- `tools/standardize_outputs.py` → `archive/standardize_outputs.py`
- `tools/generate_results_site.py` → `archive/generate_results_site.py`
- `tools/collect_results.py` → `archive/collect_results.py`
- `tools/build_results.py` → `archive/build_results.py`
- `tools/_util/path_parsing.py` → `archive/path_parsing.py`
- `tests/test_collect_results.py` → `archive/test_collect_results.py`

### **Files Kept in Main Directory (Actively Used):**

#### **R Files (.R) - 26 files kept**
**Core Pipeline Scripts:**
- `scripts/eda/eda_summary_stats.R` - EDA analysis
- `scripts/core/consolidation.R` - Results consolidation
- `scripts/utils/pipeline_diagnostic.R` - Pipeline diagnostics
- `scripts/modular_pipeline/run_modular_pipeline.R` - Modular orchestrator

**Model Fitting:**
- `scripts/model_fitting/fit_garch_models.R` - GARCH model fitting
- `scripts/model_fitting/extract_residuals.R` - Residual extraction

**Simulation & Forecasting:**
- `scripts/simulation_forecasting/simulate_nf_garch_engine.R` - NF-GARCH simulation
- `scripts/simulation_forecasting/forecast_garch_variants.R` - Forecasting

**Evaluation:**
- `scripts/evaluation/wilcoxon_winrate_analysis.R` - Wilcoxon analysis
- `scripts/evaluation/stylized_fact_tests.R` - Stylized facts
- `scripts/evaluation/var_backtesting.R` - VaR backtesting
- `scripts/evaluation/nfgarch_var_backtesting.R` - NF-GARCH VaR backtesting
- `scripts/evaluation/nfgarch_stress_testing.R` - NF-GARCH stress testing

**Manual GARCH:**
- `scripts/manual_garch/manual_garch_core.R` - Core manual GARCH
- `scripts/manual_garch/forecast_manual.R` - Manual forecasting
- `scripts/manual_garch/fit_sgarch_manual.R` - sGARCH fitting
- `scripts/manual_garch/fit_tgarch_manual.R` - tGARCH fitting
- `scripts/manual_garch/fit_gjr_manual.R` - GJR-GARCH fitting
- `scripts/manual_garch/fit_egarch_manual.R` - eGARCH fitting

**Utilities:**
- `scripts/utils/safety_functions.R` - Safety functions
- `scripts/utils/enhanced_plotting.R` - Enhanced plotting
- `scripts/utils/consolidate_results.R` - Results consolidation
- `scripts/utils/conflict_resolution.R` - Conflict resolution
- `scripts/utils/cli_parser.R` - CLI parsing
- `scripts/engines/engine_selector.R` - Engine selection
- `scripts/stress_tests/evaluate_under_stress.R` - Stress testing

#### **Python Files (.py) - 6 files kept**
- `scripts/model_fitting/train_nf_models.py` - NF model training
- `scripts/model_fitting/evaluate_nf_fit.py` - NF model evaluation
- `scripts/utils/validate_pipeline.py` - Pipeline validation
- `scripts/utils/generate_appendix_log.py` - Appendix generation
- `scripts/utils/fix_python_env.py` - Python environment fixes
- `scripts/utils/validate_all_fixes.py` - Comprehensive validation

## 📋 **Rationale for Moves:**

### **Moved Files (Unused):**
- **Core utilities**: Files that were not referenced in the main pipeline execution
- **Data processing utilities**: Standalone scripts for data cleaning/fixing that are not part of the main flow
- **Tool scripts**: Standalone utilities for dashboard creation, result processing, etc.
- **Test files**: Test scripts not part of the main pipeline
- **Legacy components**: Old versions of scripts that have been replaced

### **Kept Files (Active):**
- **Pipeline execution scripts**: All scripts referenced in `run_all.bat` and `run_modular.bat`
- **Core functionality**: Essential scripts for model fitting, evaluation, and analysis
- **Utilities**: Scripts that are actively sourced or called by the main pipeline
- **Manual GARCH**: All manual GARCH implementation scripts
- **Validation scripts**: Scripts used for pipeline validation and environment setup

## **Result:**

The main repository is now significantly cleaner with only the essential files remaining in the active directories:

- **Scripts directory**: Reduced from 69 R files to 26 active R files
- **Scripts directory**: Reduced from 25 Python files to 6 active Python files
- **Tools directory**: Completely cleaned (all files moved to archive)
- **Root directory**: Cleaned of unused Python scripts

## 📁 **Archive Structure:**

The archive folder now contains:
- **25 R files** (moved from scripts and root)
- **11 Python files** (moved from scripts, tools, and root)
- **Legacy documentation**
- **Unused scripts**
- **Old outputs and results**
- **Installation scripts**

This organization maintains the repository's functionality while dramatically improving its cleanliness and organization. The active pipeline now has a clear, focused structure with only the essential components.
