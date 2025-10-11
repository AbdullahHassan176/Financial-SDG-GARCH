#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Validation Script for All Fixes
Validates that all issues have been resolved and the pipeline is ready to run
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def check_eda_script_fixes():
    """Check that EDA script fixes are in place"""
    print("=== CHECKING EDA SCRIPT FIXES ===")
    
    eda_script = "scripts/eda/eda_summary_stats.R"
    if not os.path.exists(eda_script):
        print("❌ EDA script not found")
        return False
    
    with open(eda_script, 'r') as f:
        content = f.read()
    
    fixes_applied = []
    
    # Check for histogram fixes
    if 'hist_data <- data.frame(Returns =' in content:
        fixes_applied.append("[OK] Histogram function calls fixed")
    else:
        print("[FAIL] Histogram function calls not fixed")
        return False
    
    # Check for time series fixes
    if 'create_enhanced_timeseries(' in content:
        fixes_applied.append("[OK] Time series function calls fixed")
    else:
        print("[FAIL] Time series function calls not fixed")
        return False
    
    # Check for boxplot fixes
    if 'color_scheme = c("FX" = "#1f77b4", "Equity" = "#2ca02c")' in content:
        fixes_applied.append("[OK] Boxplot function calls fixed")
    else:
        print("[FAIL] Boxplot function calls not fixed")
        return False
    
    for fix in fixes_applied:
        print(fix)
    
    return True

def check_python_import_fixes():
    """Check that Python import issues are fixed"""
    print("\n=== CHECKING PYTHON IMPORT FIXES ===")
    
    # Check that rugarch import is commented out
    garch_utils = "archive/unused_scripts/Manual Scripts/Python - NF Extended Training/utils/garch_utils.py"
    if os.path.exists(garch_utils):
        with open(garch_utils, 'r') as f:
            content = f.read()
        
        if '# from rugarch import' in content:
            print("[OK] Incorrect rugarch import fixed")
        else:
            print("[FAIL] Incorrect rugarch import not fixed")
            return False
    
    # Check requirements.txt
    requirements = "environment/requirements.txt"
    if os.path.exists(requirements):
        with open(requirements, 'r') as f:
            content = f.read()
        
        if 'pathlib2' not in content and 'nflows' in content:
            print("[OK] Requirements.txt updated")
        else:
            print("[FAIL] Requirements.txt not properly updated")
            return False
    
    return True

def check_dependency_graph_fixes():
    """Check that dependency graph is cleaned up"""
    print("\n=== CHECKING DEPENDENCY GRAPH FIXES ===")
    
    depgraph = "build/depgraph/depgraph_python.json"
    if os.path.exists(depgraph):
        with open(depgraph, 'r') as f:
            content = f.read()
        
        if '"rugarch"' not in content:
            print("[OK] Dependency graph cleaned up")
        else:
            print("[FAIL] Dependency graph still contains rugarch references")
            return False
    
    return True

def check_output_directories():
    """Check that all required output directories exist"""
    print("\n=== CHECKING OUTPUT DIRECTORIES ===")
    
    required_dirs = [
        "outputs/eda/figures",
        "outputs/eda/tables", 
        "outputs/model_eval/figures",
        "outputs/model_eval/tables",
        "outputs/var_backtest/figures",
        "outputs/var_backtest/tables",
        "outputs/stress_tests/figures",
        "outputs/stress_tests/tables",
        "outputs/diagnostic"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"[OK] {dir_path}")
        else:
            print(f"[FAIL] {dir_path} missing")
            all_exist = False
    
    return all_exist

def check_required_files():
    """Check that all required files exist"""
    print("\n=== CHECKING REQUIRED FILES ===")
    
    required_files = [
        "data/processed/raw (FX + EQ).csv",
        "scripts/utils/safety_functions.R",
        "scripts/utils/cli_parser.R",
        "scripts/engines/engine_selector.R",
        "scripts/manual_garch/fit_sgarch_manual.R",
        "scripts/manual_garch/fit_gjr_manual.R",
        "scripts/manual_garch/fit_egarch_manual.R",
        "scripts/manual_garch/fit_tgarch_manual.R",
        "scripts/manual_garch/forecast_manual.R",
        "scripts/manual_garch/manual_garch_core.R"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} missing")
            all_exist = False
    
    return all_exist

def check_pipeline_status():
    """Check pipeline status"""
    print("\n=== CHECKING PIPELINE STATUS ===")
    
    status_file = "checkpoints/pipeline_status.json"
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        completed_count = 0
        total_count = len(status)
        
        for component, info in status.items():
            if info.get('status') == 'completed':
                completed_count += 1
                print(f"[OK] {component}: {info.get('status')}")
            else:
                print(f"[FAIL] {component}: {info.get('status')}")
        
        print(f"\nPipeline Status: {completed_count}/{total_count} components completed")
        return completed_count == total_count
    else:
        print("[FAIL] Pipeline status file not found")
        return False

def main():
    """Main validation function"""
    print("=== COMPREHENSIVE VALIDATION OF ALL FIXES ===\n")
    
    checks = [
        ("EDA Script Fixes", check_eda_script_fixes),
        ("Python Import Fixes", check_python_import_fixes),
        ("Dependency Graph Fixes", check_dependency_graph_fixes),
        ("Output Directories", check_output_directories),
        ("Required Files", check_required_files),
        ("Pipeline Status", check_pipeline_status)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"[ERROR] Error in {check_name}: {e}")
            results.append((check_name, False))
    
    print("\n=== VALIDATION SUMMARY ===")
    all_passed = True
    for check_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n[SUCCESS] ALL FIXES VALIDATED SUCCESSFULLY!")
        print("The pipeline should now run without errors.")
    else:
        print("\n[WARNING] Some issues remain. Please review the failed checks above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
