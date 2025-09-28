#!/usr/bin/env Rscript
# NF-GARCH Simulation and Forecasting (Fixed Version)
# This script implements Normalizing Flow-enhanced GARCH models for financial time series
# Supports both rugarch and manual engine implementations with robust error handling

# Load required libraries
library(rugarch)
library(xts)
library(zoo)
library(dplyr)
library(tidyr)
library(stringr)
library(lubridate)

# Set up error handling
options(warn = 1)
options(error = function() {
  cat("ERROR: NF-GARCH simulation failed\n")
  traceback()
  quit(status = 1)
})

# Load configuration and engine selection utilities
tryCatch({
  source("scripts/utils/cli_parser.R")
  source("scripts/engines/engine_selector.R")
  source("scripts/utils/safety_functions.R")
}, error = function(e) {
  cat("ERROR: Failed to load utility scripts:", e$message, "\n")
  quit(status = 1)
})

# Display current configuration and engine selection
print_config()
engine <- get_engine()
cat("Using engine:", engine, "\n\n")

cat("Starting NF-GARCH simulation with engine:", engine, "...\n")
set.seed(123)  # Ensure reproducibility

# Initialize pipeline
tryCatch({
  source("scripts/utils/conflict_resolution.R")
  initialize_pipeline()
}, error = function(e) {
  cat("WARNING: Pipeline initialization failed:", e$message, "\n")
})

# Data Import and Preprocessing
cat("Loading and preprocessing data...\n")

tryCatch({
  # Load data
  if (!file.exists("./data/processed/raw (FX + EQ).csv")) {
    stop("Data file not found: ./data/processed/raw (FX + EQ).csv")
  }
  
  raw_price_data <- read.csv("./data/processed/raw (FX + EQ).csv", row.names = 1, stringsAsFactors = FALSE)
  raw_price_data$Date <- as.Date(rownames(raw_price_data))
  rownames(raw_price_data) <- NULL
  raw_price_data <- raw_price_data %>% dplyr::select(Date, everything())
  
  cat("✅ Data loaded successfully\n")
  cat("   Rows:", nrow(raw_price_data), "\n")
  cat("   Columns:", ncol(raw_price_data), "\n")
  
}, error = function(e) {
  cat("ERROR: Data loading failed:", e$message, "\n")
  quit(status = 1)
})

# Extract time index and price matrix for processing
date_index <- raw_price_data$Date
price_data_matrix <- raw_price_data[, !(names(raw_price_data) %in% "Date")]

# Define asset tickers for equity and foreign exchange instruments
equity_tickers <- c("NVDA", "MSFT", "PG", "CAT", "WMT", "AMZN")
fx_names <- c("EURUSD", "GBPUSD", "GBPCNY", "USDZAR", "GBPZAR", "EURZAR")

# Convert price series to XTS objects for time series analysis
equity_xts <- lapply(equity_tickers, function(ticker) {
  if (ticker %in% names(price_data_matrix)) {
    xts(price_data_matrix[[ticker]], order.by = date_index)
  } else {
    cat("WARNING: Asset", ticker, "not found in data\n")
    NULL
  }
})
names(equity_xts) <- equity_tickers
equity_xts <- equity_xts[!sapply(equity_xts, is.null)]

fx_xts <- lapply(fx_names, function(ticker) {
  if (ticker %in% names(price_data_matrix)) {
    xts(price_data_matrix[[ticker]], order.by = date_index)
  } else {
    cat("WARNING: Asset", ticker, "not found in data\n")
    NULL
  }
})
names(fx_xts) <- fx_names
fx_xts <- fx_xts[!sapply(fx_xts, is.null)]

cat("✅ Asset data prepared\n")
cat("   Equity assets:", length(equity_xts), "\n")
cat("   FX assets:", length(fx_xts), "\n")

# Calculate log returns for volatility modeling
CalculateReturns <- function(x) {
  if (inherits(x, "xts")) {
    diff(log(x))
  } else {
    diff(log(as.numeric(x)))
  }
}

equity_returns <- lapply(equity_xts, function(x) CalculateReturns(x)[-1, ])
fx_returns     <- lapply(fx_xts,     function(x) diff(log(x))[-1, ])

# Model Configuration and Data Splitting
cat("Setting up model configurations...\n")

model_configs <- list(
  sGARCH_norm  = list(model = "sGARCH", distribution = "norm", submodel = NULL),
  sGARCH_sstd  = list(model = "sGARCH", distribution = "sstd", submodel = NULL),
  gjrGARCH     = list(model = "gjrGARCH", distribution = "sstd", submodel = NULL),
  eGARCH       = list(model = "eGARCH", distribution = "sstd", submodel = NULL),
  TGARCH       = list(model = "fGARCH", distribution = "sstd", submodel = "TGARCH")
)

# Data Splitting for Model Training and Evaluation
get_split_index <- function(x, split_ratio = 0.65) {
  return(floor(nrow(x) * split_ratio))
}

# Create training and testing sets for both asset classes (Chronological Split)
fx_train_returns <- lapply(fx_returns, function(x) x[1:get_split_index(x)])
fx_test_returns  <- lapply(fx_returns, function(x) x[(get_split_index(x) + 1):nrow(x)])

equity_train_returns <- lapply(equity_returns, function(x) x[1:get_split_index(x)])
equity_test_returns  <- lapply(equity_returns, function(x) x[(get_split_index(x) + 1):nrow(x)])

# Time Series Cross-Validation Implementation for NF-GARCH
cat("Implementing Time Series Cross-Validation for NF-GARCH...\n")

# TS CV function for NF-GARCH with manual engine
ts_cross_validate_nfgarch_manual <- function(returns, model_type, dist_type = "sstd", submodel = NULL, 
                                             nf_residuals, window_size = 500, step_size = 50, forecast_horizon = 20) {
  # Perform sliding window time-series cross-validation for NF-GARCH with manual engine
  # This approach respects temporal ordering and provides robust performance estimates
  
  n <- nrow(returns)
  results <- list()
  
  for (start_idx in seq(1, n - window_size - forecast_horizon, by = step_size)) {
    # Define training and testing windows
    train_set <- returns[start_idx:(start_idx + window_size - 1)]
    test_set  <- returns[(start_idx + window_size):(start_idx + window_size + forecast_horizon - 1)]
    
    # Print progress information for monitoring
    message("Processing NF-GARCH TS CV window: ", start_idx, 
            " | Train size: ", nrow(train_set), 
            " | Test size: ", nrow(test_set),
            " | Train SD: ", round(sd(train_set, na.rm = TRUE), 6))
    
    # Fit GARCH model with manual engine
    fit <- tryCatch({
      engine_fit(
        model = model_type, 
        returns = train_set, 
        dist = dist_type, 
        submodel = submodel, 
        engine = engine
      )
    }, error = function(e) {
      message("NF-GARCH fit error at index ", start_idx, ": ", e$message)
      return(NULL)
    })
    
    if (!is.null(fit) && engine_converged(fit)) {
      # Setup NF-GARCH simulation
      n_sim <- min(length(nf_residuals), length(test_set))
      if (n_sim < length(test_set)) {
        message("⚠️ NF residuals too short for window ", start_idx)
        next
      }
      
      # Use engine_path for NF-GARCH simulation
      sim_result <- tryCatch({
        engine_path(
          fit, 
          head(nf_residuals, n_sim), 
          n_sim, 
          model_type, 
          submodel, 
          engine
        )
      }, error = function(e) {
        message("NF-GARCH simulation error at index ", start_idx, ": ", e$message)
        return(NULL)
      })
      
      if (!is.null(sim_result)) {
        sim_returns <- sim_result$returns
        
        # Calculate performance metrics
        mse <- mean((test_set - sim_returns)^2, na.rm = TRUE)
        mae <- mean(abs(test_set - sim_returns), na.rm = TRUE)
        
        # Get model information criteria
        ic <- engine_infocriteria(fit)
        
        # Store results
        results[[length(results) + 1]] <- data.frame(
          WindowStart = start_idx,
          WindowEnd = start_idx + window_size - 1,
          TestStart = start_idx + window_size,
          TestEnd = start_idx + window_size + forecast_horizon - 1,
          Model = model_type,
          Distribution = dist_type,
          AIC = ic["AIC"],
          BIC = ic["BIC"],
          LogLikelihood = ic["LogLikelihood"],
          MSE = mse,
          MAE = mae,
          SplitType = "TS_CV"
        )
      }
    }
  }
  
  if (length(results) == 0) return(NULL)
  do.call(rbind, results)
}

# GARCH Model Training
cat("Fitting GARCH models...\n")

Fitted_Chrono_Split_models <- list()

for (config_name in names(model_configs)) {
  cfg <- model_configs[[config_name]]
  
  cat("Fitting", config_name, "models...\n")
  
  # Fit models using the selected engine
  equity_chrono_split_fit <- lapply(names(equity_train_returns), function(asset) {
    tryCatch({
      engine_fit(model = cfg$model, returns = equity_train_returns[[asset]], 
                dist = cfg$distribution, submodel = cfg$submodel, engine = engine)
    }, error = function(e) {
      cat("WARNING: Failed to fit", config_name, "for", asset, ":", e$message, "\n")
      NULL
    })
  })
  names(equity_chrono_split_fit) <- names(equity_train_returns)
  
  fx_chrono_split_fit <- lapply(names(fx_train_returns), function(asset) {
    tryCatch({
      engine_fit(model = cfg$model, returns = fx_train_returns[[asset]], 
                dist = cfg$distribution, submodel = cfg$submodel, engine = engine)
    }, error = function(e) {
      cat("WARNING: Failed to fit", config_name, "for", asset, ":", e$message, "\n")
      NULL
    })
  })
  names(fx_chrono_split_fit) <- names(fx_train_returns)
  
  Fitted_Chrono_Split_models[[paste0("equity_", config_name)]] <- equity_chrono_split_fit
  Fitted_Chrono_Split_models[[paste0("fx_", config_name)]]     <- fx_chrono_split_fit
}

# Load NF Residuals
cat("Loading NF residuals...\n")

tryCatch({
  nf_files <- list.files("nf_generated_residuals", pattern = "*.csv", full.names = TRUE)
  
  if (length(nf_files) == 0) {
    cat("WARNING: No NF residual files found\n")
    cat("Generating dummy residuals for testing...\n")
    
    # Generate dummy residuals for testing
    nf_residuals_map <- list()
    for (config_name in names(model_configs)) {
      for (asset in names(equity_returns)) {
        key <- paste0(config_name, "_equity_", asset, "_residuals_synthetic")
        nf_residuals_map[[key]] <- rnorm(1000, 0, 1)
      }
      for (asset in names(fx_returns)) {
        key <- paste0(config_name, "_fx_", asset, "_residuals_synthetic")
        nf_residuals_map[[key]] <- rnorm(1000, 0, 1)
      }
    }
  } else {
    # Parse model and asset from file names
    nf_residuals_map <- list()
    for (f in nf_files) {
      fname <- basename(f)
      key <- stringr::str_replace(fname, "\\.csv$", "")
      
      tryCatch({
        residuals_data <- read.csv(f)
        
        if ("residual" %in% names(residuals_data)) {
          nf_residuals_map[[key]] <- residuals_data$residual
        } else {
          nf_residuals_map[[key]] <- residuals_data[[1]]
        }
      }, error = function(e) {
        cat("WARNING: Failed to load NF residuals from", fname, ":", e$message, "\n")
      })
    }
  }
  
  cat("✅ Loaded", length(nf_residuals_map), "NF residual files\n")
  
}, error = function(e) {
  cat("ERROR: Failed to load NF residuals:", e$message, "\n")
  quit(status = 1)
})

# NF-GARCH Simulation
cat("Running NF-GARCH simulation...\n")

# Define NF-GARCH fitting function with robust error handling
fit_nf_garch <- function(asset_name, asset_returns, model_config, nf_resid) {
  tryCatch({
    # Use engine_fit
    fit <- engine_fit(
      model = model_config[["model"]], 
      returns = asset_returns, 
      dist = model_config[["distribution"]], 
      submodel = model_config[["submodel"]], 
      engine = engine
    )
    
    if (!engine_converged(fit)) {
      cat("❌ Fit failed for", asset_name, model_config[["model"]], "\n")
      return(NULL)
    }
    
    # Setup simulation
    n_sim <- floor(length(asset_returns) / 2)
    if (length(nf_resid) < n_sim) {
      cat("⚠️ NF residuals too short for", asset_name, "-", model_config[["model"]], "\n")
      return(NULL)
    }
    
    # Use engine_path for simulation
    sim_result <- engine_path(
      fit, 
      head(nf_resid, n_sim), 
      n_sim, 
      model_config[["model"]], 
      model_config[["submodel"]], 
      engine
    )
    sim_returns <- sim_result$returns
    
    fitted_values <- sim_returns
    mse <- mean((asset_returns - fitted_values)^2, na.rm = TRUE)
    mae <- mean(abs(asset_returns - fitted_values), na.rm = TRUE)
    
    # Get model information
    ic <- engine_infocriteria(fit)
    
    return(data.frame(
      Model = model_config[["model"]],
      Distribution = model_config[["distribution"]],
      Asset = asset_name,
      AIC = ic["AIC"],
      BIC = ic["BIC"],
      LogLikelihood = ic["LogLikelihood"],
      MSE = mse,
      MAE = mae,
      SplitType = "Chrono"
    ))
  }, error = function(e) {
    cat("❌ Error for", asset_name, model_config[["model"]], ":", conditionMessage(e), "\n")
    return(NULL)
  })
}

# Run NF-GARCH Analysis - BOTH Chronological and TS CV
cat("=== CHRONOLOGICAL SPLIT NF-GARCH ANALYSIS ===\n")
nf_results_chrono <- list()

for (config_name in names(model_configs)) {
  cfg <- model_configs[[config_name]]
  
  cat("Processing", config_name, "(Chrono Split)...\n")
  
  # FX
  for (asset in names(fx_returns)) {
    possible_keys <- c(
      paste0(config_name, "_fx_", asset, "_residuals_synthetic"),
      paste0("fx_", asset, "_residuals_", config_name, "_residuals_synthetic_synthetic"),
      paste0(config_name, "_", asset, "_residuals_synthetic")
    )
    
    key <- NULL
    for (k in possible_keys) {
      if (k %in% names(nf_residuals_map)) {
        key <- k
        break
      }
    }
    
    if (is.null(key)) {
      cat("❌ Skipped:", asset, config_name, "- No synthetic residuals found.\n")
      next
    }
    
    cat("NF-GARCH (FX):", asset, config_name, "\n")
    r <- fit_nf_garch(asset, fx_returns[[asset]], cfg, nf_residuals_map[[key]])
    if (!is.null(r)) nf_results_chrono[[length(nf_results_chrono) + 1]] <- r
  }
  
  # Equity
  for (asset in names(equity_returns)) {
    possible_keys <- c(
      paste0(config_name, "_equity_", asset, "_residuals_synthetic"),
      paste0("equity_", asset, "_residuals_", config_name, "_residuals_synthetic_synthetic"),
      paste0(config_name, "_", asset, "_residuals_synthetic")
    )
    
    key <- NULL
    for (k in possible_keys) {
      if (k %in% names(nf_residuals_map)) {
        key <- k
        break
      }
    }
    
    if (is.null(key)) {
      cat("❌ Skipped:", asset, config_name, "- No synthetic residuals found.\n")
      next
    }
    
    cat("NF-GARCH (EQ):", asset, config_name, "\n")
    r <- fit_nf_garch(asset, equity_returns[[asset]], cfg, nf_residuals_map[[key]])
    if (!is.null(r)) nf_results_chrono[[length(nf_results_chrono) + 1]] <- r
  }
}

# Run NF-GARCH Time Series Cross-Validation (Manual Engine Focus)
cat("=== RUNNING NF-GARCH TIME SERIES CROSS-VALIDATION ===\n")

# Check and ensure sufficient size and variability across each window
valid_fx_returns <- fx_returns[sapply(fx_returns, function(x) nrow(x) > 520 && sd(x, na.rm = TRUE) > 0)]
valid_equity_returns <- equity_returns[sapply(equity_returns, function(x) nrow(x) > 520 && sd(x, na.rm = TRUE) > 0)]

# Helper to run all NF-GARCH CV models with manual engine
run_all_nfgarch_cv_models_manual <- function(returns_list, model_configs, nf_residuals_map, 
                                            window_size = 500, forecast_horizon = 40) {
  cv_results_all <- list()
  
  for (model_name in names(model_configs)) {
    cfg <- model_configs[[model_name]]
    message("⚙️ Running NF-GARCH TS CV for model: ", model_name, " (", engine, " engine)")
    
    result <- lapply(names(returns_list), function(asset_name) {
      # Find corresponding NF residuals
      possible_keys <- c(
        paste0(model_name, "_", asset_name, "_residuals_synthetic"),
        paste0(model_name, "_fx_", asset_name, "_residuals_synthetic"),
        paste0(model_name, "_equity_", asset_name, "_residuals_synthetic")
      )
      
      key <- NULL
      for (k in possible_keys) {
        if (k %in% names(nf_residuals_map)) {
          key <- k
          break
        }
      }
      
      if (is.null(key)) {
        message("❌ No NF residuals found for ", asset_name, " - ", model_name)
        return(NULL)
      }
      
      ts_cross_validate_nfgarch_manual(
        returns_list[[asset_name]], 
        model_type = cfg$model, 
        dist_type = cfg$distribution, 
        submodel = cfg$submodel,
        nf_residuals = nf_residuals_map[[key]],
        window_size = window_size,
        forecast_horizon = forecast_horizon
      )
    })
    
    # Label by asset names
    names(result) <- names(returns_list)
    
    # Remove nulls
    result <- result[!sapply(result, is.null)]
    
    message("✅ NF-GARCH TS CV fits found for assets: ", paste(names(result), collapse = ", "))
    
    cv_results_all[[model_name]] <- result
  }
  
  return(cv_results_all)
}

# Run NF-GARCH TS CV Analysis
cat("Processing FX assets with NF-GARCH TS CV...\n")
Fitted_FX_NFGARCH_TS_CV_models <- run_all_nfgarch_cv_models_manual(
  valid_fx_returns, model_configs, nf_residuals_map
)

cat("Processing Equity assets with NF-GARCH TS CV...\n")
Fitted_EQ_NFGARCH_TS_CV_models <- run_all_nfgarch_cv_models_manual(
  valid_equity_returns, model_configs, nf_residuals_map
)

# Flatten all NF-GARCH CV results into one data frame
Fitted_NFGARCH_TS_CV_models <- data.frame()

for (model_name in names(Fitted_FX_NFGARCH_TS_CV_models)) {
  fx_results <- tryCatch({
    do.call(rbind, Fitted_FX_NFGARCH_TS_CV_models[[model_name]])
  }, error = function(e) {
    message("⚠️ FX NF-GARCH CV results failed for: ", model_name, " - ", e$message)
    return(NULL)
  })
  
  eq_results <- tryCatch({
    do.call(rbind, Fitted_EQ_NFGARCH_TS_CV_models[[model_name]])
  }, error = function(e) {
    message("⚠️ EQ NF-GARCH CV results failed for: ", model_name, " - ", e$message)
    return(NULL)
  })
  
  if (!is.null(fx_results)) {
    fx_results$Asset <- names(Fitted_FX_NFGARCH_TS_CV_models[[model_name]])
    fx_results$AssetType <- "FX"
    Fitted_NFGARCH_TS_CV_models <- bind_rows(Fitted_NFGARCH_TS_CV_models, fx_results)
  }
  
  if (!is.null(eq_results)) {
    eq_results$Asset <- names(Fitted_EQ_NFGARCH_TS_CV_models[[model_name]])
    eq_results$AssetType <- "Equity"
    Fitted_NFGARCH_TS_CV_models <- bind_rows(Fitted_NFGARCH_TS_CV_models, eq_results)
  }
}

# Create Comparison Tables
cat("=== CREATING COMPARISON TABLES ===\n")

# Combine results
if (length(nf_results_chrono) > 0) {
  nf_results_df <- do.call(rbind, nf_results_chrono)
  
  # Create comparison tables
  comparison_tables <- list()
  
  # 1. Chronological Summary
  chrono_summary <- nf_results_df %>%
    group_by(Model, Distribution) %>%
    summarise(
      Avg_AIC = mean(AIC, na.rm = TRUE),
      Avg_BIC = mean(BIC, na.rm = TRUE),
      Avg_LogLik = mean(LogLikelihood, na.rm = TRUE),
      Avg_MSE = mean(MSE, na.rm = TRUE),
      Avg_MAE = mean(MAE, na.rm = TRUE),
      Models_Count = n(),
      .groups = 'drop'
    ) %>%
    mutate(Split_Type = "Chronological")
  
  # 2. TS CV Summary (if available)
  tscv_summary <- data.frame()
  if (nrow(Fitted_NFGARCH_TS_CV_models) > 0) {
    tscv_summary <- Fitted_NFGARCH_TS_CV_models %>%
      group_by(Model, Distribution) %>%
      summarise(
        Avg_AIC = mean(AIC, na.rm = TRUE),
        Avg_BIC = mean(BIC, na.rm = TRUE),
        Avg_LogLik = mean(LogLikelihood, na.rm = TRUE),
        Avg_MSE = mean(MSE, na.rm = TRUE),
        Avg_MAE = mean(MAE, na.rm = TRUE),
        Windows_Processed = n(),
        .groups = 'drop'
      ) %>%
      mutate(Split_Type = "Time_Series_CV")
  }
  
  # 3. Direct Comparison Table
  comparison_table <- data.frame()
  if (nrow(chrono_summary) > 0 && nrow(tscv_summary) > 0) {
    # Merge chronological and TS CV results for direct comparison
    comparison_table <- bind_rows(chrono_summary, tscv_summary) %>%
      pivot_wider(
        names_from = Split_Type,
        values_from = c(Avg_AIC, Avg_BIC, Avg_LogLik, Avg_MSE, Avg_MAE),
        names_sep = "_"
      ) %>%
      # Calculate differences
      mutate(
        AIC_Diff = Avg_AIC_Time_Series_CV - Avg_AIC_Chronological,
        BIC_Diff = Avg_BIC_Time_Series_CV - Avg_BIC_Chronological,
        MSE_Diff = Avg_MSE_Time_Series_CV - Avg_MSE_Chronological,
        MAE_Diff = Avg_MAE_Time_Series_CV - Avg_MAE_Chronological,
        # Performance ranking
        Chrono_Rank = rank(Avg_MSE_Chronological),
        TS_CV_Rank = rank(Avg_MSE_Time_Series_CV),
        Rank_Change = TS_CV_Rank - Chrono_Rank
      ) %>%
      arrange(Chrono_Rank)
  }
  
  # 4. Model Performance Comparison by Asset
  asset_comparison <- data.frame()
  if (nrow(Fitted_NFGARCH_TS_CV_models) > 0) {
    # Get asset-level comparison
    chrono_asset <- nf_results_df %>%
      group_by(Model, Asset) %>%
      summarise(
        Chrono_MSE = mean(MSE, na.rm = TRUE),
        Chrono_MAE = mean(MAE, na.rm = TRUE),
        .groups = 'drop'
      )
    
    tscv_asset <- Fitted_NFGARCH_TS_CV_models %>%
      group_by(Model, Asset) %>%
      summarise(
        TS_CV_MSE = mean(MSE, na.rm = TRUE),
        TS_CV_MAE = mean(MAE, na.rm = TRUE),
        Windows = n(),
        .groups = 'drop'
      )
    
    asset_comparison <- full_join(chrono_asset, tscv_asset, by = c("Model", "Asset")) %>%
      mutate(
        MSE_Improvement = Chrono_MSE - TS_CV_MSE,
        MAE_Improvement = Chrono_MAE - TS_CV_MAE,
        MSE_Improvement_Pct = (MSE_Improvement / Chrono_MSE) * 100,
        MAE_Improvement_Pct = (MAE_Improvement / Chrono_MAE) * 100
      ) %>%
      arrange(desc(MSE_Improvement_Pct))
  }
  
          # Save results with comprehensive comparison
          # Create consolidated directory if it doesn't exist
          if (!dir.exists("results/consolidated")) {
            dir.create("results/consolidated", recursive = TRUE, showWarnings = FALSE)
          }
          output_file <- paste0("results/consolidated/NF_GARCH_Results_", engine, ".xlsx")
  
  tryCatch({
    wb <- createWorkbook()
    
    # Add chronological split results
    addWorksheet(wb, "Chrono_Split_NF_GARCH")
    writeData(wb, "Chrono_Split_NF_GARCH", nf_results_df)
    
    # Add TS CV results if available
    if (nrow(Fitted_NFGARCH_TS_CV_models) > 0) {
      addWorksheet(wb, "TS_CV_NF_GARCH")
      writeData(wb, "TS_CV_NF_GARCH", Fitted_NFGARCH_TS_CV_models)
    }
    
    # Add comparison tables
    addWorksheet(wb, "Chrono_Summary")
    writeData(wb, "Chrono_Summary", chrono_summary)
    
    if (nrow(tscv_summary) > 0) {
      addWorksheet(wb, "TS_CV_Summary")
      writeData(wb, "TS_CV_Summary", tscv_summary)
    }
    
    if (nrow(comparison_table) > 0) {
      addWorksheet(wb, "Split_Comparison")
      writeData(wb, "Split_Comparison", comparison_table)
    }
    
    if (nrow(asset_comparison) > 0) {
      addWorksheet(wb, "Asset_Comparison")
      writeData(wb, "Asset_Comparison", asset_comparison)
    }
    
    # Add overall performance comparison
    if (nrow(comparison_table) > 0) {
      # Create performance ranking comparison
      performance_comparison <- comparison_table %>%
        select(Model, Distribution, 
               Chrono_MSE = Avg_MSE_Chronological, 
               TS_CV_MSE = Avg_MSE_Time_Series_CV,
               Chrono_Rank, TS_CV_Rank, Rank_Change) %>%
        mutate(
          Best_Method = ifelse(Chrono_MSE < TS_CV_MSE, "Chronological", "TS_CV"),
          Improvement = abs(Chrono_MSE - TS_CV_MSE),
          Improvement_Pct = (Improvement / pmin(Chrono_MSE, TS_CV_MSE)) * 100
        ) %>%
        arrange(Chrono_Rank)
      
      addWorksheet(wb, "Performance_Comparison")
      writeData(wb, "Performance_Comparison", performance_comparison)
    }
    
    # Save workbook
    saveWorkbook(wb, output_file, overwrite = TRUE)
    
    cat("✅ NF-GARCH results saved to:", output_file, "\n")
    cat("   Total chronological models:", nrow(nf_results_df), "\n")
    cat("   Successful chronological fits:", sum(!is.na(nf_results_df$AIC)), "\n")
    if (nrow(Fitted_NFGARCH_TS_CV_models) > 0) {
      cat("   TS CV windows processed:", nrow(Fitted_NFGARCH_TS_CV_models), "\n")
      cat("   Comparison tables created:", length(comparison_tables), "\n")
    }
    
    # Print summary statistics
    if (nrow(comparison_table) > 0) {
      cat("\n=== COMPARISON SUMMARY ===\n")
      cat("Models with better TS CV performance:", sum(comparison_table$TS_CV_Rank < comparison_table$Chrono_Rank), "\n")
      cat("Models with better Chrono performance:", sum(comparison_table$Chrono_Rank < comparison_table$TS_CV_Rank), "\n")
      cat("Average MSE improvement (TS CV vs Chrono):", round(mean(comparison_table$MSE_Diff, na.rm = TRUE), 6), "\n")
    }
    
  }, error = function(e) {
    cat("ERROR: Failed to save results:", e$message, "\n")
  })
  
} else {
  cat("❌ No NF-GARCH results generated\n")
}

cat("\n=== NF-GARCH SIMULATION COMPLETE ===\n")
cat("Engine used:", engine, "\n")
cat("Models attempted:", length(names(model_configs)) * (length(fx_returns) + length(equity_returns)), "\n")
cat("Successful fits:", ifelse(length(nf_results_chrono) > 0, length(nf_results_chrono), 0), "\n")
