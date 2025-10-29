# Manual Execution Guide - Optimized Pipeline

This guide provides step-by-step instructions for running the Financial-SDG-GARCH pipeline manually in R Studio and Jupyter Notebook with significant optimizations.

## 🚀 Optimization Summary

- **Asset Reduction**: 50% time savings (12 → 6 assets)
- **Model Reduction**: 40% time savings (5 → 3 models)  
- **CV Optimization**: 60% time savings (5 → 3 folds, optimized windows)
- **NF Training**: 25% time savings (100 → 75 epochs, optimized architecture)
- **Total Expected Time Savings**: 70-80%
- **Expected Execution Time**: 45-90 minutes

## 📋 Prerequisites

### R Packages Required
```r
install.packages(c(
  "rugarch", "quantmod", "xts", "PerformanceAnalytics", 
  "FinTS", "tidyverse", "dplyr", "tidyr", "stringr", 
  "ggplot2", "openxlsx", "moments", "tseries", 
  "forecast", "lmtest", "parallel", "doParallel"
))
```

### Python Packages Required
```bash
pip install torch nflows numpy pandas matplotlib scipy psutil
```

## 🔧 Manual Execution Steps

### Phase 1: R Studio - Data Preparation & GARCH Fitting (30 minutes)

#### Step 1: Load Configuration
```r
# Load optimized configuration
source("scripts/manual/manual_optimized_config.R")

# Verify optimization settings
print_optimization_summary()
```

#### Step 2: Run Optimized GARCH Fitting
```r
# Run the optimized GARCH fitting script
source("scripts/manual/manual_garch_fitting.R")
```

**What this does:**
- Loads 6 optimized assets (3 FX + 3 Equity)
- Fits 3 optimized GARCH models (sGARCH, eGARCH, TGARCH)
- Runs optimized time-series cross-validation (3 folds instead of 5)
- Saves residuals for NF training

**Expected Output:**
- `outputs/manual/garch_fitting/model_summary.csv`
- `outputs/manual/residuals_by_model/` (residuals for each model-asset combination)

### Phase 2: Jupyter Notebook - NF Training (20 minutes)

#### Step 1: Open Jupyter Notebook
```bash
jupyter notebook
```

#### Step 2: Create New Notebook or Use Existing
Create a new notebook or use: `archive/Manual Scripts/Python - NF Main Training/NFGARCH - Train all Residuals.ipynb`

#### Step 3: Run Optimized NF Training
```python
# Cell 1: Import and setup
exec(open('scripts/manual/manual_nf_training.py').read())

# Cell 2: Run main training pipeline
training_results, all_samples = main()
```

**What this does:**
- Trains NF models on GARCH residuals (75 epochs instead of 100)
- Uses optimized architecture (4 layers, 64 hidden features)
- Implements early stopping and validation
- Generates synthetic residuals

**Expected Output:**
- `outputs/manual/nf_models/` (trained NF models)
- `outputs/manual/nf_models/*_synthetic_residuals.csv` (synthetic data)

### Phase 3: R Studio - Simulation & Evaluation (15 minutes)

#### Step 1: Run NF-GARCH Simulation
```r
# Load the main simulation script with manual optimizations
source("scripts/simulation_forecasting/simulate_nf_garch_engine.R")
```

#### Step 2: Run Core Evaluation
```r
# Run only essential evaluation metrics
source("scripts/evaluation/core_metrics.R")
```

**What this does:**
- Simulates NF-GARCH models with synthetic residuals
- Evaluates core metrics (RMSE, MAE, KS distance, VaR)
- Skips non-essential evaluations for speed

## 📊 Optimization Details

### Asset Selection (50% Reduction)
**Selected Assets:**
- **FX**: EURUSD, GBPUSD, USDZAR (3 most liquid)
- **Equity**: NVDA, MSFT, AMZN (3 most volatile)

**Excluded Assets:**
- **FX**: GBPCNY, GBPZAR, EURZAR
- **Equity**: PG, CAT, WMT

### Model Selection (40% Reduction)
**Selected Models:**
- **sGARCH**: Standard GARCH with skewed t-distribution
- **eGARCH**: Exponential GARCH with asymmetric effects
- **TGARCH**: Threshold GARCH with regime-dependent behavior

**Excluded Models:**
- **sGARCH_norm**: Standard GARCH with normal distribution
- **gjrGARCH**: Glosten-Jagannathan-Runkle GARCH

### CV Optimization (60% Time Savings)
**Optimized Parameters:**
- **Folds**: 3 (reduced from 5)
- **Window Size**: 50% (reduced from 65%)
- **Step Size**: 15% (increased from 10%)
- **Max Windows**: 3 (reduced from 4)
- **Forecast Horizon**: 15 (reduced from 20)

### NF Training Optimization (25% Time Savings)
**Optimized Parameters:**
- **Epochs**: 75 (reduced from 100)
- **Batch Size**: 512 (increased from 256)
- **Layers**: 4 (reduced from 5)
- **Hidden Features**: 64 (reduced from 128)
- **Early Stopping**: Enabled (patience = 15)

## 🔍 Monitoring and Debugging

### Performance Monitoring
```r
# In R Studio - Monitor execution time
start_time <- Sys.time()
# Your code here
end_time <- Sys.time()
cat("Execution time:", end_time - start_time, "\n")
```

```python
# In Jupyter - Monitor memory usage
monitor_memory()
clear_memory()  # Clear GPU/CPU memory
```

### Common Issues and Solutions

#### Issue 1: Memory Errors
**Solution:**
```r
# Clear memory between operations
gc()
```

```python
# Clear GPU memory
clear_memory()
```

#### Issue 2: Convergence Failures
**Solution:**
- Check data quality
- Reduce model complexity
- Increase tolerance parameters

#### Issue 3: Slow Execution
**Solution:**
- Enable parallel processing
- Reduce batch sizes
- Skip non-essential components

## 📈 Expected Results

### Performance Metrics
- **Total Execution Time**: 45-90 minutes
- **Memory Usage**: < 8GB
- **Success Rate**: > 90%
- **Convergence Rate**: > 85%

### Output Files
```
outputs/manual/
├── garch_fitting/
│   ├── model_summary.csv
│   └── detailed_results.rds
├── residuals_by_model/
│   ├── sGARCH/
│   ├── eGARCH/
│   └── TGARCH/
├── nf_models/
│   ├── sGARCH_*_synthetic_residuals.csv
│   ├── eGARCH_*_synthetic_residuals.csv
│   └── TGARCH_*_synthetic_residuals.csv
└── evaluation/
    ├── core_metrics.csv
    └── simulation_results.csv
```

## 🎯 Quick Start Commands

### Ultra-Fast Execution (45 minutes)
```r
# R Studio
source("scripts/manual/manual_optimized_config.R")
source("scripts/manual/manual_garch_fitting.R")
```

```python
# Jupyter Notebook
exec(open('scripts/manual/manual_nf_training.py').read())
training_results, all_samples = main()
```

### Balanced Execution (90 minutes)
```r
# R Studio - Full pipeline with more assets/models
source("scripts/core/config.R")  # Use full config
source("scripts/model_fitting/fit_garch_models.R")
source("scripts/model_fitting/extract_residuals.R")
source("scripts/simulation_forecasting/simulate_nf_garch_engine.R")
```

## 📝 Notes

1. **First Run**: May take longer due to package compilation
2. **Memory**: Ensure at least 8GB RAM available
3. **GPU**: Optional but recommended for NF training
4. **Parallel Processing**: Automatically enabled where possible
5. **Checkpoints**: Results are saved incrementally

## 🆘 Troubleshooting

### If Scripts Fail
1. Check file paths and working directory
2. Verify all required packages are installed
3. Check memory usage and clear if needed
4. Review error messages in console output

### If Results Are Incomplete
1. Check convergence rates in model summary
2. Verify residual files were generated
3. Ensure NF training completed successfully
4. Check output directories for missing files

## 📞 Support

For issues or questions:
1. Check the `outputs/manual/` directory for logs
2. Review error messages in console output
3. Verify optimization settings with `print_optimization_summary()`
4. Check memory usage with monitoring functions
