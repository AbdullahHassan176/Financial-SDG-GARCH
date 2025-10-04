# NF-GARCH Research Repository

## Overview

This repository contains the complete research implementation for Normalizing Flow GARCH (NF-GARCH) models applied to financial time series analysis. The research focuses on improving volatility forecasting through the integration of normalizing flows with traditional GARCH models.

## Research Methodology

The study implements a comprehensive framework combining classical econometric models (GARCH-family) with modern generative learning techniques (Normalizing Flows). The methodology includes:

- **Data Processing**: South African Reserve Bank exchange rate data (2005-2024)
- **Model Architecture**: Standard GARCH variants (sGARCH, EGARCH, TGARCH, GJR-GARCH) enhanced with normalizing flows
- **Evaluation Framework**: Quantitative metrics, distributional analysis, stylized facts replication, and stress testing
- **Implementation**: Dual-engine approach (RUGARCH and manual estimation)

## Repository Structure

```
.
├── src/                   # Python source code
├── R/                     # R scripts and workflows
├── configs/               # Configuration files
├── data/                  # Raw and processed data
├── artifacts/             # Models, metrics, figures, reports
├── dashboards/            # HTML dashboards
├── tools/                 # Helper scripts and utilities
├── expected/              # Baseline files for regression testing
├── build/                 # Build artifacts and temporary files
├── tests/                 # Unit and regression tests
├── docs/                  # Documentation and method notes
├── archive/               # Non-essential archived files
├── Makefile              # Build automation
├── README.md             # This file
├── CLEANROOM_STATUS.md   # Clean room process status
└── requirements.txt      # Python dependencies
```

## Quick Start

### Environment Setup

1. **Python Environment**:
   ```bash
   pip install -r requirements.txt
   ```

2. **R Environment**:
   ```bash
   Rscript -e "renv::init()"
   ```

### Running the Analysis

1. **Full Pipeline**:
   ```bash
   make review
   ```

2. **Individual Components**:
   ```bash
   # Create artifact snapshot
   make snapshot
   
   # Check regression against baseline
   make regression
   
   # Run quality checks
   make lint test
   ```

3. **Dashboard Generation**:
   ```bash
   # Generate comprehensive dashboard
   python tools/create_comprehensive_final_dashboard.py
   
   # View dashboard
   python -m http.server 8000 --directory docs
   ```

## Data Requirements

- **Raw Data**: Place exchange rate data in `data/raw/`
- **Processed Data**: Generated outputs in `data/processed/`
- **Results**: Analysis results in `artifacts/`

## Model Architecture

### Standard GARCH Models
- **sGARCH**: Standard GARCH with normal and skewed-t distributions
- **EGARCH**: Exponential GARCH
- **TGARCH**: Threshold GARCH  
- **GJR-GARCH**: Glosten-Jagannathan-Runkle GARCH

### NF-GARCH Models
- **NF_sGARCH**: Normalizing Flow enhanced sGARCH
- **NF_eGARCH**: Normalizing Flow enhanced EGARCH
- **NF_gjrGARCH**: Normalizing Flow enhanced GJR-GARCH
- **NF_TGARCH**: Normalizing Flow enhanced TGARCH

## Evaluation Metrics

### Quantitative Metrics
- RMSE, MAE, Log-likelihood, AIC/BIC
- Q-statistics, ARCH-LM test results

### Distributional Metrics
- Kolmogorov-Smirnov distance
- Wasserstein distance
- KL/JS divergence

### Stylized Facts
- Tail index, autocorrelation decay
- Volatility clustering, asymmetry
- Hurst exponent, kurtosis

### Stress Testing
- Convergence rates, robustness scores
- Maximum drawdown analysis
- Scenario generation under extreme shocks

## Reproducibility

The repository includes comprehensive reproducibility measures:

- **Deterministic Seeds**: Fixed random seeds for all components
- **Artifact Snapshotting**: SHA256 hashes for all outputs
- **Regression Testing**: Automated comparison against baselines
- **Environment Locking**: Pinned dependency versions

## Quality Assurance

### Code Quality
- **Linting**: Black, Ruff, MyPy for Python; Lintr for R
- **Testing**: Unit tests, regression tests, integration tests
- **Pre-commit Hooks**: Automated quality checks

### Academic Standards
- **Sanitization**: Removal of AI-generated content and emojis
- **Documentation**: Neutral, academic tone throughout
- **Structure**: Standardized repository layout for submission

## Usage Examples

### Basic Analysis
```bash
# Run complete analysis pipeline
python run_all.py

# Run modular components
python run_modular.py --component model_fitting
```

### Dashboard Generation
```bash
# Generate research dashboard
python tools/create_comprehensive_final_dashboard.py

# View results
python -m http.server 8000 --directory docs
```

### Quality Checks
```bash
# Run all quality checks
make review

# Individual checks
make lint      # Code linting
make test      # Run tests
make snapshot  # Create artifact snapshot
```

## File Organization

### Essential Files
- **Source Code**: All Python and R implementation files
- **Configuration**: YAML/JSON config files and environment files
- **Scripts**: Batch files and execution scripts
- **Data**: Processed data and essential raw data
- **Artifacts**: Models, metrics, figures, and reports
- **Documentation**: README, status files, and method notes
- **Tests**: Unit and regression test suites
- **Tools**: Utility scripts for analysis and quality control

### Archived Files
Non-essential files are moved to `archive/` directory:
- Temporary files and logs
- Development artifacts
- Non-essential documentation
- Backup files and old versions

## Research Outputs

The repository generates comprehensive research outputs:

1. **Model Performance Analysis**: Comparative evaluation of all models
2. **Risk Assessment**: VaR backtesting and violation rate analysis
3. **Stress Testing**: Robustness under extreme market conditions
4. **Stylized Facts**: Replication of financial time series characteristics
5. **Quantitative Metrics**: Statistical performance measures
6. **Distributional Analysis**: Distance metrics and divergence measures
7. **Engine Comparison**: Manual vs RUGARCH engine performance
8. **Interactive Dashboards**: Comprehensive visualization of results

## Citation

If you use this repository in your research, please cite:

```bibtex
@software{nf_garch_research,
  title={NF-GARCH Research Repository},
  author={Research Team},
  year={2025},
  url={https://github.com/AbdullahHassan176/Financial-SDG-GARCH}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

No generative AI tools were used to produce the final text or analysis in this repository. All code comments are brief and technical, following academic standards for research reproducibility.

## Support

For questions or issues, please refer to the documentation in the `docs/` directory or create an issue in the repository.