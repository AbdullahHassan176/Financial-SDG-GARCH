#!/usr/bin/env python3
"""
Check if fGARCH is actually NF_TGARCH in the results.
"""

import pandas as pd

print("=== CHECKING NF-GARCH MODELS ===")

# Check NF-GARCH results
try:
    df_nf = pd.read_excel('results/consolidated/nf_garch_manual_results.xlsx', sheet_name='NF_GARCH_Summary')
    print("Models in NF-GARCH results:")
    print(df_nf['Model'].unique())
    print(f"Count: {len(df_nf['Model'].unique())}")
    
    print("\nDetailed breakdown:")
    for model in df_nf['Model'].unique():
        model_data = df_nf[df_nf['Model'] == model]
        print(f"  {model}: {len(model_data)} records")
    
    print("\n=== MODEL ANALYSIS ===")
    print("fGARCH description: Fractional GARCH")
    print("NF_TGARCH would be: Normalizing Flow Threshold GARCH")
    print("TGARCH description: Threshold GARCH")
    
    print("\n=== CHECKING IF fGARCH IS ACTUALLY NF_TGARCH ===")
    print("Looking at the models:")
    for model in df_nf['Model'].unique():
        if model == 'fGARCH':
            print(f"  {model} - This could be NF_TGARCH (Normalizing Flow Threshold GARCH)")
        elif model.startswith('NF_'):
            print(f"  {model} - This is clearly NF-GARCH")
        else:
            print(f"  {model} - This appears to be Standard GARCH")
    
    print("\n=== CONCLUSION ===")
    print("If fGARCH is actually NF_TGARCH, then we should rename it.")
    print("The models suggest:")
    print("- sGARCH, eGARCH, gjrGARCH: Standard GARCH models")
    print("- fGARCH: Could be NF_TGARCH (Normalizing Flow Threshold GARCH)")
    
except Exception as e:
    print(f"Error reading NF-GARCH results: {e}")

# Check comprehensive results
try:
    print("\n=== CHECKING COMPREHENSIVE RESULTS ===")
    df_comp = pd.read_excel('results/consolidated/comprehensive_results_all.xlsx', sheet_name='Model_Performance_Summary')
    print("Models in comprehensive results:")
    print(df_comp['Model'].unique())
    
    print("\nChecking for TGARCH variants:")
    for model in df_comp['Model'].unique():
        if 'TGARCH' in model or 'fGARCH' in model:
            print(f"  {model} - TGARCH variant found")
    
except Exception as e:
    print(f"Error reading comprehensive results: {e}")
