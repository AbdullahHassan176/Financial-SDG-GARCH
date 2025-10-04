#!/usr/bin/env python3
"""
Debug model classification issues.
"""

import pandas as pd

# Load the data
df = pd.read_csv('outputs/standardized/complete_model_performance.csv')

print("=== MODEL BREAKDOWN ===")
print(f"Total records: {len(df)}")
print(f"Unique models: {len(df['Model'].unique())}")
print()

print("Model details:")
for model in df['Model'].unique():
    model_data = df[df['Model'] == model]
    model_type = model_data['Model_Type'].iloc[0]
    engine = model_data['Engine'].iloc[0]
    count = len(model_data)
    print(f"  {model}: {count} records, Type: {model_type}, Engine: {engine}")

print()
print("Model type counts:")
print(df['Model_Type'].value_counts())

print()
print("Engine counts:")
print(df['Engine'].value_counts())

print()
print("Expected vs Actual:")
print("Expected Standard GARCH models: sGARCH_norm, sGARCH_sstd, eGARCH, gjrGARCH, TGARCH (5 models)")
print("Expected NF-GARCH models: sGARCH, gjrGARCH, eGARCH, fGARCH (4 models)")
print("Total expected: 9 unique models")
print(f"Actual unique models: {len(df['Model'].unique())}")

# Check if we're missing any models
expected_standard = ['sGARCH_norm', 'sGARCH_sstd', 'eGARCH', 'gjrGARCH', 'TGARCH']
expected_nf = ['sGARCH', 'gjrGARCH', 'eGARCH', 'fGARCH']

actual_models = df['Model'].unique()

missing_standard = [m for m in expected_standard if m not in actual_models]
missing_nf = [m for m in expected_nf if m not in actual_models]

print()
print("Missing Standard GARCH models:", missing_standard)
print("Missing NF-GARCH models:", missing_nf)
