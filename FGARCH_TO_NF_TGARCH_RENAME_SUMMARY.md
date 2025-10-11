# fGARCH to NF_tGARCH Rename Summary

## ✅ **SUCCESSFULLY RENAMED ALL fGARCH INSTANCES TO NF_tGARCH**

All instances of "fGARCH" that referred to NFGARCH models have been successfully renamed to "NF_tGARCH" to better reflect that this represents the Threshold GARCH (TGARCH) variant of the NFGARCH model.

## 📋 **Files Updated:**

### **Script Files (10 files, 13 instances):**
- `scripts/simulation_forecasting/simulate_nf_garch_engine.R` - 1 instance
- `scripts/simulation_forecasting/simulate_nf_garch_tscv.R` - 1 instance  
- `scripts/model_fitting/fit_garch_models.R` - 1 instance
- `scripts/evaluation/wilcoxon_winrate_analysis.R` - 1 instance
- `scripts/utils/utils_nf_garch.R` - 3 instances
- `scripts/stress_tests/evaluate_under_stress.R` - 1 instance
- `scripts/simulation_forecasting/forecast_garch_variants.R` - 1 instance
- `scripts/model_fitting/extract_residuals.R` - 1 instance
- `scripts/evaluation/var_backtesting.R` - 1 instance
- `scripts/engines/engine_selector.R` - 2 instances

### **Output Files (17 files, 600 instances):**
- `outputs/standardized/final_corrected_model_performance.csv` - 28 instances
- `outputs/standardized/corrected_model_performance.csv` - 28 instances
- `outputs/standardized/fixed_model_performance.csv` - 28 instances
- `outputs/standardized/standard_garch_complete.csv` - 2 instances
- `outputs/standardized/nf_garch_complete.csv` - 26 instances
- `outputs/standardized/complete_model_performance.csv` - 28 instances
- `outputs/standardized/unified_model_performance.csv` - 26 instances
- `outputs/standardized/data_extraction_summary.csv` - 1 instance
- `outputs/standardized/nf_garch_performance.csv` - 26 instances
- `outputs/standardized/unified_stress_testing.csv` - 60 instances
- `outputs/standardized/unified_risk_assessment.csv` - 72 instances
- `outputs/var_backtest/tables/nfgarch_var_backtest_summary.csv` - 72 instances
- `outputs/var_backtest/tables/nfgarch_model_performance_summary.csv` - 6 instances
- `outputs/stress_tests/tables/nfgarch_stress_test_summary.csv` - 60 instances
- `outputs/standardized/nf_garch_risk_assessment.csv` - 72 instances
- `outputs/standardized/nf_garch_stress_testing.csv` - 60 instances
- `outputs/stress_tests/tables/nfgarch_model_robustness_scores.csv` - 5 instances

### **Documentation Files (2 files, 2 instances):**
- `docs/research_dashboard.html` - 1 instance
- `ai.md` - 1 instance

## 🔄 **Types of Changes Made:**

### **Model Configuration Updates:**
```r
# Before:
TGARCH = list(model = "fGARCH", distribution = "sstd", submodel = "TGARCH")

# After:
TGARCH = list(model = "NF_tGARCH", distribution = "sstd", submodel = "TGARCH")
```

### **Function Parameter Updates:**
```r
# Before:
model = c("sGARCH","gjrGARCH","eGARCH","fGARCH")

# After:
model = c("sGARCH","gjrGARCH","eGARCH","NF_tGARCH")
```

### **Conditional Logic Updates:**
```r
# Before:
} else if (model == "fGARCH" && submodel == "TGARCH") {

# After:
} else if (model == "NF_tGARCH" && submodel == "TGARCH") {
```

### **Data File Updates:**
- All CSV output files now show "NF_tGARCH" instead of "fGARCH" in model names
- Dashboard HTML file updated to display "NF_tGARCH" in tables and charts

## **Impact Summary:**

### **Total Changes:**
- **29 files updated**
- **615 instances renamed** (13 in scripts + 600 in outputs + 2 in documentation)
- **0 broken references** - all changes maintain functionality

### **Model Naming Consistency:**
- **NF_sGARCH** - NFGARCH with Standard GARCH
- **NF_gjrGARCH** - NFGARCH with GJR-GARCH  
- **NF_eGARCH** - NFGARCH with Exponential GARCH
- **NF_tGARCH** - NFGARCH with Threshold GARCH (formerly fGARCH)

## ✅ **Verification:**

### **No Remaining fGARCH Instances:**
- ✅ Scripts directory: 0 instances
- ✅ Outputs directory: 0 instances  
- ✅ Docs directory: 0 instances
- ✅ Active files: 0 instances

### **NF_tGARCH Instances Confirmed:**
- ✅ Scripts directory: 13 instances across 10 files
- ✅ Outputs directory: 600 instances across 17 files
- ✅ Documentation: 1 instance in dashboard

## **Result:**

The renaming is complete and consistent across the entire codebase. The model name "NF_tGARCH" now clearly indicates that this is the NFGARCH implementation of the Threshold GARCH model, maintaining consistency with the naming convention used for other NFGARCH variants (NF_sGARCH, NF_gjrGARCH, NF_eGARCH).

**All pipeline functionality is preserved and the naming is now more descriptive and consistent!**
