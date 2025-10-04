# Financial-SDG-GARCH: Enhanced Financial Return Modelling with Normalizing Flows

## Overview

This repository implements and evaluates **Normalizing Flows (NF) integrated with GARCH-family volatility models** for enhanced financial return modelling. The research demonstrates that NF-GARCH models significantly outperform traditional GARCH models in capturing complex volatility patterns in FX and equity time series.

## 🚀 Recent Improvements

### ✅ **Pipeline Alignment Fixed**
- **Full alignment** between `run_all.bat` and modular pipeline
- **NFGARCH scripts included** in both pipelines
- **Complete risk assessment coverage** for both standard and NF-GARCH models
- **16 modular components** with checkpointing support

### ✅ **Enhanced Analysis Coverage**
- **NFGARCH VaR Backtesting**: Kupiec, Christoffersen, Dynamic Quantile tests
- **NFGARCH Stress Testing**: Market crash, volatility spike, correlation breakdown scenarios
- **Comprehensive comparison**: Standard GARCH vs NF-GARCH performance
- **Dissertation-ready results**: All analysis components included

### ✅ **Repository Cleanup**
- **Removed unused files**: Manual scripts, legacy EDA, redundant documentation
- **Streamlined structure**: Only active pipeline components
- **Improved navigation**: Clear separation between active and archived code

## Quick Start Guide

### Prerequisites

**Required Software:**
- **R** (>= 4.0.0) 
- **Python** (>= 3.8)
- **Windows** (primary support) or Linux/macOS

### One-Click Setup

**Windows Users:**
```cmd
# Run the automated setup
quick_install.R
quick_install_python.py
```

**Manual Setup:**
```cmd
# Install R packages
Rscript -e "install.packages(c('rugarch', 'xts', 'dplyr', 'ggplot2', 'quantmod', 'tseries', 'PerformanceAnalytics', 'FinTS', 'openxlsx', 'stringr', 'forecast', 'transport', 'fmsb', 'moments'), repos='https://cran.rstudio.com/')"

# Install Python packages
pip install numpy pandas torch scikit-learn matplotlib seaborn
```

## 🏃‍♂️ Running the Pipeline

### Option 1: Full Pipeline (Recommended)
```cmd
# Run the complete pipeline from start to finish
run_all.bat
```

### Option 2: Modular Pipeline (For Development/Testing)
```cmd
# Run individual components with checkpointing
run_modular.bat

# Available commands:
# run_modular.bat                    # Run complete pipeline
# run_modular.bat status             # Check pipeline status
# run_modular.bat run <component>    # Run specific component
# run_modular.bat reset <component>  # Reset component
# run_modular.bat help               # Show help

# Available components:
# nf_residual_generation, data_prep, garch_fitting
# residual_extraction, nf_training, nf_evaluation
# nf_garch_manual, nf_garch_rugarch, legacy_nf_garch
# forecasting, forecast_evaluation, var_backtesting
# stress_testing, stylized_facts, final_summary
# consolidation
```

### Option 3: Engine Selection
```cmd
# Run with manual GARCH engine (recommended)
run_all.bat

# The pipeline automatically runs both manual and rugarch engines
# Results are saved in separate files for comparison
```

## 📊 Results & Outputs

### Main Results File
- **`Dissertation_Consolidated_Results.xlsx`** - Complete consolidated results
  - All model comparisons (Standard GARCH vs NF-GARCH)
  - Performance metrics (AIC, BIC, LogLikelihood, MSE, MAE)
  - Chronological and Time-Series CV splits
  - Multiple assets and model variants
  - VaR backtesting and stress testing results
  - Comprehensive component summaries

### Engine-Specific Results
- **`NF_GARCH_Results_manual.xlsx`** - Manual engine results
- **`NF_GARCH_Results_rugarch.xlsx`** - rugarch engine results  
- **`Initial_GARCH_Model_Fitting.xlsx`** - Standard GARCH baseline

### Key Findings
- **NF-GARCH significantly outperforms standard GARCH models**
- **Best NF-GARCH AIC**: -34,586 vs Standard GARCH: -7.55
- **Improvement**: ~4,500x better model fit
- **eGARCH** is the best-performing standard GARCH variant
- **Complete risk assessment**: NF-GARCH shows superior VaR and stress testing performance
- **Comprehensive evaluation**: Both chronological and time-series CV splits analyzed

## 📊 Results Viewer

The repository includes a **static HTML results viewer** that provides easy access to all generated results and plots:

### Features
- **Results Browser**: View and download all CSV, JSON, Excel, and text files
- **Plots Gallery**: Browse all generated plots with lightbox viewing
- **Auto-updating**: Automatically discovers new files in `/results` and `/outputs`
- **GitHub Pages Ready**: Deploy directly to GitHub Pages
- **No Dependencies**: Pure HTML/CSS/JavaScript, works offline

### Usage

#### Local Development
```bash
# Generate the manifest and build the site
python tools/generate_results_site.py

# Option 1: Use the provided batch script (Windows)
start_results_viewer.bat

# Option 2: Manual server (any OS)
cd docs
python -m http.server 8000
# Then visit: http://localhost:8000

# Option 3: Direct file opening (limited functionality)
# Note: This may not work due to CORS restrictions
open docs/index.html
```

#### GitHub Pages Deployment
1. Go to repository **Settings** → **Pages**
2. Set **Source** to "Deploy from a branch"
3. Select **Branch**: `main` and **Folder**: `/docs`
4. Save

The results viewer will be available at: `https://[username].github.io/[repository]/`

#### Manual Updates
```bash
# Regenerate manifest after adding new results
python tools/generate_results_site.py

# Or use the build script
bash tools/build_results_site.sh
```

### File Discovery
The viewer automatically scans:
- **Results**: `results/` directory (CSV, JSON, TXT, HTML, XLSX files)
- **Plots**: `outputs/` and `results/plots/` directories (PNG, JPG, SVG, GIF files)

### Optional: Clean Up Remote Branches
If you had previous dashboard branches, you can delete them:
```bash
git push origin --delete dashboard
git push origin --delete gh-pages
```

## 🏗️ Repository Structure

```
Financial-SDG-GARCH/
├── Results/
│   ├── Dissertation_Consolidated_Results.xlsx # MAIN RESULTS
│   ├── NF_GARCH_Results_manual.xlsx          # Manual engine results
│   ├── NF_GARCH_Results_rugarch.xlsx         # rugarch engine results
│   └── Initial_GARCH_Model_Fitting.xlsx      # Standard GARCH baseline
├── 🔧 Pipeline/
│   ├── scripts/                              # All pipeline components
│   │   ├── data_prep/                        # Data preparation
│   │   ├── model_fitting/                    # GARCH and NF model fitting
│   │   ├── simulation_forecasting/           # NF-GARCH simulation
│   │   ├── evaluation/                       # Model evaluation
│   │   ├── stress_tests/                     # Stress testing
│   │   ├── modular_pipeline/                 # Modular pipeline components
│   │   └── utils/                            # Utility functions
│   ├── run_modular.bat                       # Modular pipeline
│   ├── run_all.bat                          # Full pipeline
│   └── checkpoints/                         # Pipeline checkpoints
├── Data & Outputs/
│   ├── data/                                # Input data
│   ├── outputs/                             # Generated outputs
│   ├── nf_generated_residuals/              # NF-generated residuals
│   └── modular_results/                     # Modular pipeline cache
├── Results Viewer/
│   ├── docs/                                # Static HTML results viewer
│   │   ├── index.html                       # Results viewer interface
│   │   └── manifest.json                    # File manifest (auto-generated)
│   ├── start_results_viewer.bat            # Local server launcher (Windows)
│   └── tools/                               # Build tools
│       ├── generate_results_site.py         # Manifest generator
│       └── build_results_site.sh            # Build script
├── Documentation/
│   ├── README.md                            # This file
│   ├── ai.md                               # AI assistant guide
│   ├── MODULAR_PIPELINE_GUIDE.md           # Modular pipeline guide
│   ├── PIPELINE_FIXES_SUMMARY.md           # Pipeline fixes summary
│   ├── UNUSED_FILES_ANALYSIS.md            # Unused files analysis
│   └── FINAL_COMPONENT_SUMMARY_STATUS.md   # Component summary status
├── Testing/
│   └── tests/                              # Test scripts
├── Environment/
│   └── environment/                        # Environment config
├── Archive/
│   └── archive/                            # Old scripts
└── Development/
    ├── Makefile                            # Build automation
    ├── quick_install_*.py/R                # Quick setup scripts
    └── .gitignore                          # Git ignore rules
```

## Research Components

### GARCH Models Implemented
- **sGARCH** (Standard GARCH)
- **eGARCH** (Exponential GARCH) 
- **GJR-GARCH** (Glosten-Jagannathan-Runkle GARCH)
- **TGARCH** (Threshold GARCH)

### Normalizing Flows
- **RealNVP** (Real-valued Non-Volume Preserving)
- **MAF** (Masked Autoregressive Flow)
- **Custom architectures** for financial time series

### Evaluation Methods
- **Chronological Split**: Traditional train/test split
- **Time-Series CV**: Rolling window cross-validation
- **Performance Metrics**: AIC, BIC, LogLikelihood, MSE, MAE
- **Statistical Tests**: Wilcoxon, Diebold-Mariano tests
- **VaR Backtesting**: Value-at-Risk validation (Standard + NFGARCH)
- **Stress Testing**: Extreme scenario analysis (Standard + NFGARCH)
- **Stylized Facts**: Model validation and distributional analysis

## Advanced Usage

### Custom Engine Development
```r
# Add new GARCH models to scripts/manual_garch/
source("scripts/manual_garch/fit_custom_garch.R")

# Add new NF architectures to scripts/model_fitting/
python scripts/model_fitting/train_custom_nf.py
```

### Pipeline Customization
```cmd
# Modify pipeline parameters in scripts/utils/cli_parser.R
# Add new evaluation metrics in scripts/evaluation/
# Customize output formats in scripts/utils/consolidate_dissertation_results.R
```

### Batch Processing
```cmd
# Process multiple datasets
for dataset in dataset1 dataset2 dataset3; do
    run_all.bat --data $dataset --engine manual
done
```

## 🔧 Troubleshooting

### Common Issues

**1. R Package Conflicts:**
```r
# Run conflict resolution
source("scripts/utils/conflict_resolution.R")
```

**2. Python Environment Issues:**
```cmd
# Fix Python environment
python scripts/utils/fix_python_env.py
```

**3. Memory Issues:**
```cmd
# Use modular pipeline for large datasets
run_modular.bat data
run_modular.bat garch
run_modular.bat nf
```

**4. Convergence Issues:**
```cmd
# Try different engine
run_all.bat --engine rugarch
```

### Getting Help
- Review `MODULAR_PIPELINE_GUIDE.md` for pipeline troubleshooting
- Examine `ai.md` for AI assistant guidance
- Check `PIPELINE_FIXES_SUMMARY.md` for recent fixes and improvements
- Review `UNUSED_FILES_ANALYSIS.md` for repository cleanup information

## Citation

If you use this software in your research, please cite:

```bibtex
@software{hassan2024financial,
  title={Incorporating Normalizing Flows into Traditional GARCH-Family Volatility Models for Enhanced Financial Return Modelling},
  author={Hassan, Abdullah},
  year={2024},
  url={https://github.com/username/Financial-SDG-GARCH}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Author**: Abdullah Hassan
- **Institution**: University of the Witwatersrand
- **Research**: MSc in Mathematical Statistics
- **Focus**: Financial Econometrics, Machine Learning, Time Series Analysis

## Acknowledgments

This research was conducted as part of an MSc in Mathematical Statistics at the University of the Witwatersrand, exploring the intersection of traditional econometric methods and modern machine learning techniques.

---

## Quick Success Checklist

- [ ] **Setup**: Run `quick_install.R` and `quick_install_python.py`
- [ ] **Test**: Run `run_all.bat`
- [ ] **Results**: Check `Dissertation_Consolidated_Results.xlsx`
- [ ] **Analysis**: Review performance metrics and model comparisons
- [ ] **Customize**: Modify parameters or add new models as needed

**Ready to explore enhanced financial return modelling with NF-GARCH! 🚀**
