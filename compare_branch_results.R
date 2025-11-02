#!/usr/bin/env Rscript
# Comprehensive Branch Comparison Script
# Compares key metrics between branches

library(openxlsx)
library(dplyr)

cat("=== COMPREHENSIVE BRANCH COMPARISON ===\n\n")

# Read comparison file
comparison_file <- "results/consolidated/NF_vs_Standard_GARCH_Comparison.xlsx"

if (!file.exists(comparison_file)) {
  stop("Comparison file not found: ", comparison_file)
}

cat("Reading:", comparison_file, "\n")
wb <- loadWorkbook(comparison_file)
sheets <- getSheetNames(comparison_file)
cat("Available sheets:", paste(sheets, collapse = ", "), "\n\n")

# Read Summary sheet if available
if ("Summary" %in% sheets) {
  summary <- read.xlsx(comparison_file, sheet = "Summary")
  cat("=== SUMMARY (NF-GARCH vs Standard GARCH) ===\n")
  print(summary)
  cat("\n")
}

# Read Overall Summary if available
if ("Overall_Summary" %in% sheets) {
  overall <- read.xlsx(comparison_file, sheet = "Overall_Summary")
  cat("=== OVERALL SUMMARY ===\n")
  print(overall)
  cat("\n")
}

# Read comparison results
if ("Comparison_Results" %in% sheets) {
  comparison <- read.xlsx(comparison_file, sheet = "Comparison_Results")
  cat("=== COMPARISON RESULTS ===\n")
  cat("Total comparisons:", nrow(comparison), "\n")
  
  # Calculate overall metrics
  if ("MSE" %in% names(comparison) && "Source" %in% names(comparison)) {
    overall_mse <- comparison %>%
      group_by(Source) %>%
      summarise(mean_MSE = mean(MSE, na.rm = TRUE),
                median_MSE = median(MSE, na.rm = TRUE),
                n = n(),
                .groups = "drop")
    cat("\nOverall MSE by Source:\n")
    print(overall_mse)
    
    # Calculate improvement
    if ("NF_GARCH" %in% overall_mse$Source && "Standard" %in% overall_mse$Source) {
      nf_mse <- overall_mse$mean_MSE[overall_mse$Source == "NF_GARCH"]
      std_mse <- overall_mse$mean_MSE[overall_mse$Source == "Standard"]
      improvement <- (1 - nf_mse / std_mse) * 100
      cat("\nMSE Improvement: ", sprintf("%.1f%%", improvement), "\n")
      cat("  NF-GARCH MSE: ", nf_mse, "\n")
      cat("  Standard GARCH MSE: ", std_mse, "\n")
    }
  }
  
  if ("MAE" %in% names(comparison) && "Source" %in% names(comparison)) {
    overall_mae <- comparison %>%
      group_by(Source) %>%
      summarise(mean_MAE = mean(MAE, na.rm = TRUE),
                median_MAE = median(MAE, na.rm = TRUE),
                .groups = "drop")
    cat("\nOverall MAE by Source:\n")
    print(overall_mae)
    
    # Calculate improvement
    if ("NF_GARCH" %in% overall_mae$Source && "Standard" %in% overall_mae$Source) {
      nf_mae <- overall_mae$mean_MAE[overall_mae$Source == "NF_GARCH"]
      std_mae <- overall_mae$mean_MAE[overall_mae$Source == "Standard"]
      improvement <- (1 - nf_mae / std_mae) * 100
      cat("\nMAE Improvement: ", sprintf("%.1f%%", improvement), "\n")
      cat("  NF-GARCH MAE: ", nf_mae, "\n")
      cat("  Standard GARCH MAE: ", std_mae, "\n")
    }
  }
  
  # Win rate
  if ("MSE" %in% names(comparison) && "Source" %in% names(comparison)) {
    win_rate <- comparison %>%
      group_by(Model, Asset) %>%
      summarise(nf_mse = MSE[Source == "NF_GARCH"],
                std_mse = MSE[Source == "Standard"],
                .groups = "drop") %>%
      filter(!is.na(nf_mse), !is.na(std_mse)) %>%
      summarise(nf_wins = sum(nf_mse < std_mse, na.rm = TRUE),
                std_wins = sum(std_mse < nf_mse, na.rm = TRUE),
                total = n(),
                nf_win_rate = sum(nf_mse < std_mse, na.rm = TRUE) / n() * 100)
    
    cat("\n=== WIN RATE ===\n")
    cat("NF-GARCH wins:", win_rate$nf_wins, "out of", win_rate$total, 
        sprintf("(%.1f%%)", win_rate$nf_win_rate), "\n")
    cat("Standard GARCH wins:", win_rate$std_wins, "out of", win_rate$total, "\n")
  }
  cat("\n")
}

# Read Wilcoxon test results if available
if ("Wilcoxon_Test" %in% sheets) {
  wilcoxon <- read.xlsx(comparison_file, sheet = "Wilcoxon_Test")
  cat("=== WILCOXON SIGNED-RANK TEST ===\n")
  print(wilcoxon)
  cat("\n")
}

cat("=== EXPECTED VALUES (from dissertation guide) ===\n")
cat("NF-GARCH MSE: ~0.000317\n")
cat("Standard GARCH MSE: ~0.000563\n")
cat("NF-GARCH MAE: ~0.0109\n")
cat("Standard GARCH MAE: ~0.0139\n")
cat("MSE Improvement: ~43.7% reduction\n")
cat("MAE Improvement: ~21.6% reduction\n")
cat("NF-GARCH Win Rate: ~28.6% (2/7)\n")
cat("Standard GARCH Win Rate: ~71.4% (5/7)\n")
cat("\n")

