#!/usr/bin/env Rscript
# EDA Summary Statistics Script
# Performs exploratory data analysis on the financial data

library(dplyr)
library(ggplot2)
library(readr)
library(tidyr)
library(scales)
library(viridis)

# Source utilities
source("scripts/utils/conflict_resolution.R")
source("scripts/utils/enhanced_plotting.R")
source("scripts/utils/safety_functions.R")

# Initialize pipeline
initialize_pipeline()

cat("=== RUNNING EXPLORATORY DATA ANALYSIS ===\n")

# Load data
cat("Loading data...\n")
data_file <- "data/processed/raw (FX + EQ).csv"

if (!file.exists(data_file)) {
  stop("Data file not found: ", data_file)
}

data <- read.csv(data_file, row.names = 1)
data$Date <- as.Date(rownames(data))

cat("Data loaded successfully\n")
cat("  Rows:", nrow(data), "\n")
cat("  Columns:", ncol(data), "\n")

# Separate FX and Equity data
fx_cols <- c("EURUSD", "GBPUSD", "GBPCNY", "USDZAR", "GBPZAR", "EURZAR")
equity_cols <- c("NVDA", "MSFT", "PG", "CAT", "WMT", "AMZN")

fx_data <- data[, fx_cols, drop = FALSE]
equity_data <- data[, equity_cols, drop = FALSE]

# Calculate returns
fx_returns <- fx_data %>%
  mutate_all(~c(NA, diff(log(.)))) %>%
  filter(!is.na(.[,1]))

equity_returns <- equity_data %>%
  mutate_all(~c(NA, diff(log(.)))) %>%
  filter(!is.na(.[,1]))

# Create output directories
dir.create("outputs/eda/figures", showWarnings = FALSE, recursive = TRUE)
dir.create("outputs/eda/tables", showWarnings = FALSE, recursive = TRUE)

# Generate summary statistics with dual splits
cat("Generating summary statistics with chronological and TS CV splits...\n")

# Function to calculate summary statistics for a given split
calculate_summary_stats <- function(train_data, test_data, split_type) {
  # Combine train and test for overall stats, but also calculate split-specific stats
  all_data <- rbind(train_data, test_data)
  
  summary_stats <- all_data %>%
    summarise_all(list(
      mean = ~mean(., na.rm = TRUE),
      sd = ~sd(., na.rm = TRUE),
      min = ~min(., na.rm = TRUE),
      max = ~max(., na.rm = TRUE),
      skewness = ~skewness(., na.rm = TRUE),
      kurtosis = ~kurtosis(., na.rm = TRUE)
    )) %>%
    gather(key = "stat", value = "value") %>%
    separate(stat, into = c("asset", "statistic"), sep = "_") %>%
    spread(statistic, value)
  
  # Add split information
  summary_stats$Split_Type <- split_type
  summary_stats$Train_Size <- nrow(train_data)
  summary_stats$Test_Size <- nrow(test_data)
  
  return(summary_stats)
}

# Apply dual split analysis to FX data
fx_analysis_function <- function(train_data, test_data, split_type) {
  return(calculate_summary_stats(train_data, test_data, split_type))
}

# Apply dual split analysis to Equity data  
equity_analysis_function <- function(train_data, test_data, split_type) {
  return(calculate_summary_stats(train_data, test_data, split_type))
}

# Run dual split analysis for FX
cat("Running dual split analysis for FX data...\n")
fx_results <- list()
for (asset in fx_cols) {
  asset_data <- fx_returns[, asset, drop = FALSE]
  fx_results[[asset]] <- apply_dual_split_analysis(asset_data, fx_analysis_function, paste("FX", asset))
}

# Run dual split analysis for Equity
cat("Running dual split analysis for Equity data...\n")
equity_results <- list()
for (asset in equity_cols) {
  asset_data <- equity_returns[, asset, drop = FALSE]
  equity_results[[asset]] <- apply_dual_split_analysis(asset_data, equity_analysis_function, paste("Equity", asset))
}

# Combine all results
all_fx_summaries <- list()
all_equity_summaries <- list()

# Process FX results
for (asset in names(fx_results)) {
  # Chronological results
  chrono_result <- fx_results[[asset]]$chronological
  chrono_result$Asset <- asset
  chrono_result$Asset_Type <- "FX"
  all_fx_summaries[[paste0(asset, "_chronological")]] <- chrono_result
  
  # TS CV results (average across windows)
  if (length(fx_results[[asset]]$tscv) > 0) {
    tscv_avg <- fx_results[[asset]]$tscv[[1]]  # Use first window as template
    for (i in 2:length(fx_results[[asset]]$tscv)) {
      tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] <- 
        tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] + 
        fx_results[[asset]]$tscv[[i]][, c("mean", "sd", "min", "max", "skewness", "kurtosis")]
    }
    tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] <- 
      tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] / length(fx_results[[asset]]$tscv)
    tscv_avg$Asset <- asset
    tscv_avg$Asset_Type <- "FX"
    all_fx_summaries[[paste0(asset, "_tscv")]] <- tscv_avg
  }
}

# Process Equity results
for (asset in names(equity_results)) {
  # Chronological results
  chrono_result <- equity_results[[asset]]$chronological
  chrono_result$Asset <- asset
  chrono_result$Asset_Type <- "Equity"
  all_equity_summaries[[paste0(asset, "_chronological")]] <- chrono_result
  
  # TS CV results (average across windows)
  if (length(equity_results[[asset]]$tscv) > 0) {
    tscv_avg <- equity_results[[asset]]$tscv[[1]]  # Use first window as template
    for (i in 2:length(equity_results[[asset]]$tscv)) {
      tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] <- 
        tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] + 
        equity_results[[asset]]$tscv[[i]][, c("mean", "sd", "min", "max", "skewness", "kurtosis")]
    }
    tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] <- 
      tscv_avg[, c("mean", "sd", "min", "max", "skewness", "kurtosis")] / length(equity_results[[asset]]$tscv)
    tscv_avg$Asset <- asset
    tscv_avg$Asset_Type <- "Equity"
    all_equity_summaries[[paste0(asset, "_tscv")]] <- tscv_avg
  }
}

# Combine and save results
fx_summary <- do.call(rbind, all_fx_summaries)
equity_summary <- do.call(rbind, all_equity_summaries)

# Save summary tables
write.csv(fx_summary, "outputs/eda/tables/fx_summary_stats_dual_splits.csv", row.names = FALSE)
write.csv(equity_summary, "outputs/eda/tables/equity_summary_stats_dual_splits.csv", row.names = FALSE)

# Generate histograms
cat("Generating histograms...\n")

# FX Histograms
for (asset in fx_cols) {
  # Create data frame for histogram function
  hist_data <- data.frame(Returns = fx_returns[[asset]])
  p <- create_enhanced_histogram(
    hist_data, 
    x_var = "Returns",
    title = paste("Return Distribution -", asset),
    color = "#1f77b4"
  )
  ggsave(paste0("outputs/eda/figures/", asset, "_histogram.png"), p, width = 10, height = 6, dpi = 300)
}

# Equity Histograms
for (asset in equity_cols) {
  # Create data frame for histogram function
  hist_data <- data.frame(Returns = equity_returns[[asset]])
  p <- create_enhanced_histogram(
    hist_data, 
    x_var = "Returns",
    title = paste("Return Distribution -", asset),
    color = "#2ca02c"
  )
  ggsave(paste0("outputs/eda/figures/", asset, "_histogram.png"), p, width = 10, height = 6, dpi = 300)
}

# Generate time series plots
cat("Generating time series plots...\n")

# FX Time Series
fx_returns_long <- fx_returns %>%
  mutate(Date = data$Date[-1]) %>%
  gather(key = "Asset", value = "Returns", -Date)

p <- create_enhanced_timeseries(
  fx_returns_long,
  x_var = "Date",
  y_var = "Returns",
  title = "FX Returns Time Series",
  color = "#1f77b4"
)
ggsave("outputs/eda/figures/fx_returns_timeseries.png", p, width = 12, height = 8, dpi = 300)

# Equity Time Series
equity_returns_long <- equity_returns %>%
  mutate(Date = data$Date[-1]) %>%
  gather(key = "Asset", value = "Returns", -Date)

p <- create_enhanced_timeseries(
  equity_returns_long,
  x_var = "Date",
  y_var = "Returns",
  title = "Equity Returns Time Series",
  color = "#2ca02c"
)
ggsave("outputs/eda/figures/equity_returns_timeseries.png", p, width = 12, height = 8, dpi = 300)

# Generate correlation heatmaps
cat("Generating correlation heatmaps...\n")

# FX Correlation
fx_corr <- cor(fx_returns, use = "complete.obs")
p <- create_enhanced_correlation_heatmap(
  fx_corr,
  title = "FX Returns Correlation Matrix"
)
ggsave("outputs/eda/figures/fx_correlation_heatmap.png", p, width = 10, height = 8, dpi = 300)

# Equity Correlation
equity_corr <- cor(equity_returns, use = "complete.obs")
p <- create_enhanced_correlation_heatmap(
  equity_corr,
  title = "Equity Returns Correlation Matrix"
)
ggsave("outputs/eda/figures/equity_correlation_heatmap.png", p, width = 10, height = 8, dpi = 300)

# Generate volatility clustering plots
cat("Generating volatility clustering plots...\n")

# FX Volatility Clustering
fx_vol <- fx_returns %>%
  mutate_all(~abs(.)) %>%
  mutate(Date = data$Date[-1]) %>%
  gather(key = "Asset", value = "Absolute_Returns", -Date)

p <- create_enhanced_timeseries(
  fx_vol,
  x_var = "Date",
  y_var = "Absolute_Returns",
  title = "FX Volatility Clustering",
  color = "#1f77b4"
)
ggsave("outputs/eda/figures/fx_volatility_clustering.png", p, width = 12, height = 8, dpi = 300)

# Equity Volatility Clustering
equity_vol <- equity_returns %>%
  mutate_all(~abs(.)) %>%
  mutate(Date = data$Date[-1]) %>%
  gather(key = "Asset", value = "Absolute_Returns", -Date)

p <- create_enhanced_timeseries(
  equity_vol,
  x_var = "Date",
  y_var = "Absolute_Returns",
  title = "Equity Volatility Clustering",
  color = "#2ca02c"
)
ggsave("outputs/eda/figures/equity_volatility_clustering.png", p, width = 12, height = 8, dpi = 300)

# Generate comparative analysis
cat("Generating comparative analysis...\n")

# Combine summary statistics
all_summary <- bind_rows(
  fx_summary %>% mutate(Asset_Type = "FX"),
  equity_summary %>% mutate(Asset_Type = "Equity")
)

# Comparative boxplots
all_returns_long <- bind_rows(
  fx_returns_long %>% mutate(Asset_Type = "FX"),
  equity_returns_long %>% mutate(Asset_Type = "Equity")
)

p <- create_enhanced_boxplot(
  all_returns_long,
  x_var = "Asset_Type",
  y_var = "Returns",
  fill_var = "Asset_Type",
  title = "Return Distribution Comparison: FX vs Equity",
  color_scheme = c("FX" = "#1f77b4", "Equity" = "#2ca02c")
)
ggsave("outputs/eda/figures/fx_vs_equity_comparison.png", p, width = 10, height = 6, dpi = 300)

# Save comprehensive summary
write.csv(all_summary, "outputs/eda/tables/comprehensive_summary_stats.csv", row.names = FALSE)

cat("=== EDA ANALYSIS COMPLETE ===\n")
cat("Generated files:\n")
cat("  Tables: outputs/eda/tables/\n")
cat("  Figures: outputs/eda/figures/\n")
cat("  Total files:", length(list.files("outputs/eda", recursive = TRUE)), "\n")
