# NF-GARCH Results Consolidation & Interactive Dashboard

This directory contains tools for consolidating all NF-GARCH research results into a single Excel workbook and generating an interactive HTML dashboard.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Required packages: `pandas`, `numpy`, `openpyxl`, `plotly`, `jinja2`, `pyyaml`

### Installation
```bash
# Install required packages
pip install pandas numpy openpyxl plotly jinja2 pyyaml

# Or use the Makefile
make install
```

### Build Everything
```bash
# Single command to build everything
python tools/build_results.py

# Or use the Makefile
make build
```

## 📁 Directory Structure

```
tools/
├── _util/
│   └── path_parsing.py          # Path parsing utilities
├── collect_results.py           # Results consolidation script
├── build_dashboard.py          # Dashboard builder
├── build_results.py            # Main build orchestrator
└── README.md                   # This file

artifacts/
└── results_consolidated.xlsx   # Generated Excel workbook

docs/
├── index.html                  # Interactive dashboard
├── notes.md                    # Methodology notes
├── data/                       # JSON data files
└── plots/                      # Copied plot files
```

## 🔧 Available Commands

### Makefile Commands
```bash
make help          # Show all available commands
make build         # Build Excel + dashboard
make clean         # Clean build artifacts
make install       # Install dependencies
make test          # Run unit tests
make lint          # Run code linting
make collection    # Run only results collection
make dashboard     # Run only dashboard build
make serve         # Serve dashboard locally
```

### Direct Python Commands
```bash
# Full build
python tools/build_results.py

# Collection only
python tools/build_results.py --collection-only

# Dashboard only
python tools/build_results.py --dashboard-only
```

## 📊 What Gets Built

### 1. Excel Consolidation (`artifacts/results_consolidated.xlsx`)
- **master**: Long-format table with all results
- **summary_by_model**: Pivot table by model and metric
- **summary_by_asset_model**: Pivot table by asset, model, and metric
- **winrates**: NF-GARCH vs GARCH win rate analysis
- **metadata**: Build information and statistics

### 2. Interactive Dashboard (`docs/index.html`)
- **Overview**: Key performance indicators and summary charts
- **Compare Models**: Interactive model comparison with filters
- **Win Rates**: Heatmap showing NF-GARCH vs GARCH performance
- **Plots Gallery**: Browseable collection of all generated plots
- **Methodology**: Research notes and methodology

## 🎯 Features

### Data Consolidation
- ✅ Recursively scans for CSV, JSON, and Excel files
- ✅ Extracts metadata from file paths and content
- ✅ Normalizes data into long-format schema
- ✅ Handles multiple data splits (chronological vs TS CV)
- ✅ Calculates win rates between model families
- ✅ Robust error handling and logging

### Interactive Dashboard
- ✅ Static HTML (no backend required)
- ✅ Plotly charts for interactive visualizations
- ✅ DataTables for searchable, exportable tables
- ✅ Client-side routing with URL hash support
- ✅ Responsive design with modern UI
- ✅ Lightbox for plot viewing
- ✅ Export functionality (CSV, Excel)

### GitHub Pages Integration
- ✅ Automatic deployment workflow
- ✅ Hosts dashboard at `https://[username].github.io/[repository]/`
- ✅ Updates on every push to main branch

## 🔍 Data Sources

The system automatically discovers and processes:

### Result Files
- `outputs/model_eval/tables/*.csv` - Model evaluation results
- `outputs/var_backtest/tables/*.csv` - VaR backtesting results
- `outputs/stress_tests/tables/*.csv` - Stress testing results
- `outputs/eda/tables/*.csv` - Exploratory data analysis
- `results/consolidated/*.xlsx` - Consolidated results
- `nf_generated_residuals/*.csv` - NF-generated residuals

### Plot Files
- `outputs/model_eval/figures/*.png` - Model evaluation plots
- `outputs/var_backtest/figures/*.png` - VaR backtesting plots
- `outputs/stress_tests/figures/*.png` - Stress testing plots
- `results/plots/**/*.png` - Additional plot collections

## 📈 Metrics Supported

### Model Fit Metrics
- AIC, BIC, Log-Likelihood
- MSE, MAE, MAPE, RMSE

### Risk Metrics
- VaR violation rates
- Kupiec, Christoffersen, DQ test p-values
- Stress test performance

### Stylized Facts
- Volatility clustering
- Leverage effects
- Excess kurtosis

## 🏗️ Architecture

### Path Parsing (`_util/path_parsing.py`)
- Extracts asset, model, split type, and fold from file paths
- Determines model family (GARCH vs NF-GARCH)
- Normalizes metric names
- Handles metric polarity (higher vs lower is better)

### Results Collection (`collect_results.py`)
- Scans repository for result files
- Processes CSV, JSON, and Excel files
- Converts to long-format schema
- Calculates win rates and summaries
- Saves consolidated Excel workbook

### Dashboard Builder (`build_dashboard.py`)
- Loads consolidated Excel data
- Creates JSON data files for frontend
- Copies plot files to docs/plots
- Generates interactive HTML dashboard
- Creates methodology notes

### Build Orchestrator (`build_results.py`)
- Coordinates collection and dashboard building
- Checks dependencies
- Creates GitHub Pages workflow
- Provides hosting instructions

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Or use Makefile
make test
```

### Test Coverage
- Path parsing utilities
- Data processing functions
- File scanning and processing
- Error handling

## 🚀 Deployment

### Local Development
```bash
# Build and serve locally
make build
make serve
# Open http://localhost:8000
```

### GitHub Pages
1. Push code to GitHub
2. Go to repository Settings → Pages
3. Set Source to "Deploy from a branch"
4. Select branch "main" and folder "/docs"
5. Dashboard will be available at `https://[username].github.io/[repository]/`

## 🔧 Configuration

### Customizing Data Sources
Edit `collect_results.py` to modify:
- File search patterns
- Directory exclusions
- Metric normalizations
- Win rate calculations

### Customizing Dashboard
Edit `build_dashboard.py` to modify:
- Chart configurations
- UI styling
- Data processing
- Plot organization

## 📝 Logging

The system provides comprehensive logging:
- File processing status
- Error messages and warnings
- Build statistics
- Performance metrics

## 🤝 Contributing

1. Add new data sources by updating file patterns
2. Extend path parsing for new file structures
3. Add new chart types to the dashboard
4. Improve error handling and robustness

## 📄 License

This project is part of the NF-GARCH research repository and follows the same license terms.
