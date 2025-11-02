#!/usr/bin/env Rscript
# Compare Results Between main and rerun-clean Branches
# Verifies replication of results

library(openxlsx)
library(dplyr)

cat("=== COMPARING RESULTS: MAIN vs RERUN-CLEAN ===\n\n")

# Key file to compare
comparison_file <- "results/consolidated/NF_vs_Standard_GARCH_Comparison.xlsx"
final_dashboard <- "results/consolidated/Final_Dashboard.xlsx"
nf_results <- "results/consolidated/NF_GARCH_Results_manual.xlsx"

# Function to read summary metrics from comparison file
read_comparison_summary <- function(file_path) {
  if (!file.exists(file_path)) {
    return(NULL)
  }
  
  tryCatch({
    wb <- loadWorkbook(file_path)
    sheets <- getSheetNames(file_path)
    
    # Try to find summary sheet
    summary_sheet <- NULL
    if ("Summary" %in% sheets) {
      summary_sheet <- read.xlsx(file_path, sheet = "Summary")
    } else if ("Overall_Summary" %in% sheets) {
      summary_sheet <- read.xlsx(file_path, sheet = "Overall_Summary")
    } else if (length(sheets) > 0) {
      # Read first sheet
      summary_sheet <- read.xlsx(file_path, sheet = 1)
    }
    
    return(summary_sheet)
  }, error = function(e) {
    cat("Error reading:", file_path, ":", e$message, "\n")
    return(NULL)
  })
}

# Read comparison file from rerun-clean (current)
cat("Reading comparison file from rerun-clean (current branch)...\n")
rerun_comparison <- read_comparison_summary(comparison_file)

if (!is.null(rerun_comparison)) {
  cat("[OK] Rerun comparison loaded:", nrow(rerun_comparison), "rows\n")
  print(head(rerun_comparison, 10))
} else {
  cat("[ERROR] Could not read rerun comparison file\n")
}

cat("\n=== KEY METRICS TO CHECK ===\n")
cat("1. Overall MSE: NF-GARCH vs Standard GARCH\n")
cat("2. Overall MAE: NF-GARCH vs Standard GARCH\n")
cat("3. Win rates: NF-GARCH vs Standard GARCH\n")
cat("4. Statistical significance (Wilcoxon test)\n")
cat("\n")

# Read Final Dashboard
cat("\nReading Final Dashboard...\n")
if (file.exists(final_dashboard)) {
  tryCatch({
    wb <- loadWorkbook(final_dashboard)
    sheets <- getSheetNames(final_dashboard)
    cat("Dashboard sheets:", paste(sheets, collapse = ", "), "\n")
    
    if ("Executive_Summary" %in% sheets) {
      exec_summary <- read.xlsx(final_dashboard, sheet = "Executive_Summary")
      cat("\nExecutive Summary:\n")
      print(exec_summary)
    }
  }, error = function(e) {
    cat("Error reading dashboard:", e$message, "\n")
  })
}

# Read NF-GARCH Results
cat("\nReading NF-GARCH Results...\n")
if (file.exists(nf_results)) {
  tryCatch({
    wb <- loadWorkbook(nf_results)
    sheets <- getSheetNames(nf_results)
    cat("NF-GARCH Results sheets:", paste(sheets, collapse = ", "), "\n")
    
    if ("Chrono_Split_NF_GARCH" %in% sheets) {
      nf_chrono <- read.xlsx(nf_results, sheet = "Chrono_Split_NF_GARCH")
      cat("\nNF-GARCH Chrono Split Summary:\n")
      cat("  Total models:", nrow(nf_chrono), "\n")
      if (nrow(nf_chrono) > 0) {
        cat("  Mean MSE:", mean(nf_chrono$MSE, na.rm = TRUE), "\n")
        cat("  Mean MAE:", mean(nf_chrono$MAE, na.rm = TRUE), "\n")
        cat("  Mean AIC:", mean(nf_chrono$AIC, na.rm = TRUE), "\n")
      }
    }
  }, error = function(e) {
    cat("Error reading NF-GARCH results:", e$message, "\n")
  })
}

cat("\n=== COMPARISON INSTRUCTIONS ===\n")
cat("To compare with main branch:\n")
cat("1. Checkout main branch: git checkout main\n")
cat("2. Run this script again to see main branch results\n")
cat("3. Compare the metrics above\n")
cat("\nExpected values (from dissertation guide):\n")
cat("  - NF-GARCH MSE: ~0.000317\n")
cat("  - Standard GARCH MSE: ~0.000563\n")
cat("  - NF-GARCH MAE: ~0.0109\n")
cat("  - Standard GARCH MAE: ~0.0139\n")
cat("  - NF-GARCH improvement: 43.7% MSE reduction, 21.6% MAE reduction\n")
cat("\n")

