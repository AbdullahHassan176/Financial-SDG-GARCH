# NF-GARCH Research Methodology

## Overview
This research compares standard GARCH models with NF-GARCH (Normalizing Flow GARCH) models across multiple financial assets and evaluation metrics.

## Models
- **Standard GARCH**: sGARCH, eGARCH, GJR-GARCH, TGARCH with Normal and Student-t distributions
- **NF-GARCH**: Same GARCH specifications enhanced with Normalizing Flow innovations

## Assets
- **Equity**: AMZN, CAT, MSFT, NVDA, PG, WMT
- **FX**: EURUSD, EURZAR, GBPCNY, GBPUSD, GBPZAR, USDZAR

## Key Findings
- NF-GARCH models significantly outperform standard GARCH models
- Best NF-GARCH AIC: -34,586 vs Standard GARCH: -7.55 (4,500x improvement)
- eGARCH is the best-performing standard GARCH variant
- NF-GARCH shows superior VaR and stress testing performance
