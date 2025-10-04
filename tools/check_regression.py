#!/usr/bin/env python3
"""
Regression Check System
Compares current metrics against expected baseline values.
Tolerances: relative 1e-9 or exact string match for discrete values.
"""

import pandas as pd
import numpy as np
import json
import argparse
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RegressionChecker:
    """Regression checker for metrics validation."""
    
    def __init__(self, tolerance=1e-9):
        self.tolerance = tolerance
        self.failures = []
    
    def compare_numeric(self, current, expected, field_name):
        """Compare numeric values with tolerance."""
        if pd.isna(current) and pd.isna(expected):
            return True
        
        if pd.isna(current) or pd.isna(expected):
            self.failures.append(f"{field_name}: NaN mismatch (current={current}, expected={expected})")
            return False
        
        # Relative tolerance for numeric values
        if abs(expected) < 1e-10:  # Near zero
            if abs(current - expected) > self.tolerance:
                self.failures.append(f"{field_name}: Near-zero mismatch (current={current}, expected={expected})")
                return False
        else:
            relative_diff = abs(current - expected) / abs(expected)
            if relative_diff > self.tolerance:
                self.failures.append(f"{field_name}: Relative difference {relative_diff:.2e} exceeds tolerance {self.tolerance:.2e}")
                return False
        
        return True
    
    def compare_string(self, current, expected, field_name):
        """Compare string values exactly."""
        if str(current) != str(expected):
            self.failures.append(f"{field_name}: String mismatch (current='{current}', expected='{expected}')")
            return False
        return True
    
    def check_csv_file(self, current_file, expected_file):
        """Check CSV file against expected values."""
        try:
            current_df = pd.read_csv(current_file)
            expected_df = pd.read_csv(expected_file)
            
            logger.info(f"Checking {current_file} against {expected_file}")
            logger.info(f"Current shape: {current_df.shape}, Expected shape: {expected_df.shape}")
            
            # Check if shapes match
            if current_df.shape != expected_df.shape:
                self.failures.append(f"Shape mismatch: current {current_df.shape} vs expected {expected_df.shape}")
                return False
            
            # Check column names
            if list(current_df.columns) != list(expected_df.columns):
                self.failures.append(f"Column mismatch: current {list(current_df.columns)} vs expected {list(expected_df.columns)}")
                return False
            
            # Check each cell
            for col in current_df.columns:
                for idx in current_df.index:
                    current_val = current_df.loc[idx, col]
                    expected_val = expected_df.loc[idx, col]
                    
                    # Determine if numeric or string comparison
                    if pd.api.types.is_numeric_dtype(current_df[col]):
                        self.compare_numeric(current_val, expected_val, f"{col}[{idx}]")
                    else:
                        self.compare_string(current_val, expected_val, f"{col}[{idx}]")
            
            return len(self.failures) == 0
            
        except Exception as e:
            logger.error(f"Error checking {current_file}: {e}")
            self.failures.append(f"Error reading {current_file}: {e}")
            return False
    
    def check_excel_file(self, current_file, expected_file):
        """Check Excel file against expected values."""
        try:
            current_xl = pd.ExcelFile(current_file)
            expected_xl = pd.ExcelFile(expected_file)
            
            logger.info(f"Checking Excel file {current_file}")
            
            # Check sheet names
            if current_xl.sheet_names != expected_xl.sheet_names:
                self.failures.append(f"Sheet names mismatch: current {current_xl.sheet_names} vs expected {expected_xl.sheet_names}")
                return False
            
            # Check each sheet
            for sheet_name in current_xl.sheet_names:
                current_df = pd.read_excel(current_file, sheet_name=sheet_name)
                expected_df = pd.read_excel(expected_file, sheet_name=sheet_name)
                
                logger.info(f"Checking sheet '{sheet_name}': current {current_df.shape} vs expected {expected_df.shape}")
                
                # Check shapes
                if current_df.shape != expected_df.shape:
                    self.failures.append(f"Sheet '{sheet_name}' shape mismatch: current {current_df.shape} vs expected {expected_df.shape}")
                    continue
                
                # Check columns
                if list(current_df.columns) != list(expected_df.columns):
                    self.failures.append(f"Sheet '{sheet_name}' column mismatch")
                    continue
                
                # Check values
                for col in current_df.columns:
                    for idx in current_df.index:
                        current_val = current_df.loc[idx, col]
                        expected_val = expected_df.loc[idx, col]
                        
                        if pd.api.types.is_numeric_dtype(current_df[col]):
                            self.compare_numeric(current_val, expected_val, f"{sheet_name}.{col}[{idx}]")
                        else:
                            self.compare_string(current_val, expected_val, f"{sheet_name}.{col}[{idx}]")
            
            return len(self.failures) == 0
            
        except Exception as e:
            logger.error(f"Error checking Excel file {current_file}: {e}")
            self.failures.append(f"Error reading {current_file}: {e}")
            return False
    
    def check_metrics_directory(self, current_dir="outputs/standardized", expected_file="expected/metrics_baseline.csv"):
        """Check all metrics files in directory."""
        current_path = Path(current_dir)
        expected_path = Path(expected_file)
        
        if not current_path.exists():
            logger.error(f"Current metrics directory {current_dir} does not exist")
            return False
        
        if not expected_path.exists():
            logger.error(f"Expected baseline file {expected_file} does not exist")
            return False
        
        # Find all CSV and Excel files in current directory
        metric_files = []
        for pattern in ["*.csv", "*.xlsx", "*.xls"]:
            metric_files.extend(current_path.glob(pattern))
        
        logger.info(f"Found {len(metric_files)} metric files to check")
        
        all_passed = True
        for metric_file in metric_files:
            logger.info(f"Checking {metric_file}")
            
            if metric_file.suffix == '.csv':
                passed = self.check_csv_file(metric_file, expected_path)
            else:
                passed = self.check_excel_file(metric_file, expected_path)
            
            if not passed:
                all_passed = False
                logger.error(f"Regression check failed for {metric_file}")
        
        return all_passed

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check regression against baseline metrics")
    parser.add_argument("--baseline", default="expected/metrics_baseline.csv",
                       help="Baseline metrics file (default: expected/metrics_baseline.csv)")
    parser.add_argument("--current-dir", default="outputs/standardized",
                       help="Current metrics directory (default: outputs/standardized)")
    parser.add_argument("--tolerance", type=float, default=1e-9,
                       help="Numeric tolerance for comparison (default: 1e-9)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting regression check")
    logger.info(f"Baseline: {args.baseline}")
    logger.info(f"Current directory: {args.current_dir}")
    logger.info(f"Tolerance: {args.tolerance}")
    
    checker = RegressionChecker(tolerance=args.tolerance)
    
    # Perform regression check
    passed = checker.check_metrics_directory(args.current_dir, args.baseline)
    
    if passed:
        logger.info("✅ All regression checks passed")
        return 0
    else:
        logger.error("❌ Regression check failed")
        logger.error("Failures:")
        for failure in checker.failures:
            logger.error(f"  - {failure}")
        return 1

if __name__ == "__main__":
    exit(main())
