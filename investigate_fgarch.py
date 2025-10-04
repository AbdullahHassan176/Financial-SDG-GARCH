#!/usr/bin/env python3
"""
Investigate why fGARCH is named fGARCH instead of NF_TGARCH.
"""

import pandas as pd

# Load the fixed data
df = pd.read_csv('outputs/standardized/fixed_model_performance.csv')

print("=== NF-GARCH MODELS INVESTIGATION ===")
print()

# Get NF-GARCH models
nf_models = df[df['Model_Type'] == 'NF-GARCH']
print("NF-GARCH models found:")
for model in nf_models['Model'].unique():
    model_data = nf_models[nf_models['Model'] == model]
    source_file = model_data['Source_File'].iloc[0]
    count = len(model_data)
    print(f"  {model}: {count} records, Source: {source_file}")

print()
print("=== SOURCE FILE ANALYSIS ===")

# Check what's in the source files
source_files = nf_models['Source_File'].unique()
for source_file in source_files:
    print(f"\nSource file: {source_file}")
    file_data = nf_models[nf_models['Source_File'] == source_file]
    print(f"  Models in this file: {file_data['Model'].unique()}")
    print(f"  Model types: {file_data['Model_Type'].unique()}")
    print(f"  Engines: {file_data['Engine'].unique()}")

print()
print("=== CHECKING ORIGINAL DATA ===")

# Let's also check the original data to see what was there
try:
    original_df = pd.read_csv('outputs/standardized/complete_model_performance.csv')
    print("Original data NF-GARCH models:")
    original_nf = original_df[original_df['Model_Type'] == 'NF-GARCH']
    for model in original_nf['Model'].unique():
        model_data = original_nf[original_nf['Model'] == model]
        source_file = model_data['Source_File'].iloc[0]
        count = len(model_data)
        print(f"  {model}: {count} records, Source: {source_file}")
except Exception as e:
    print(f"Could not load original data: {e}")

print()
print("=== HYPOTHESIS ===")
print("The fGARCH model might be:")
print("1. A different model type (not TGARCH)")
print("2. Named differently in the source data")
print("3. A typo in the original data")
print("4. Actually a different GARCH variant (fGARCH vs TGARCH)")
