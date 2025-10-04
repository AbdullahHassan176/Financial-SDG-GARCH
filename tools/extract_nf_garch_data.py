#!/usr/bin/env python3
"""
Extract NF-GARCH data from Excel files and create proper unified datasets.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class NFGARCHDataExtractor:
    """Extract NF-GARCH data from Excel files and create unified datasets."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.standardized_dir = self.base_dir / "outputs" / "standardized"
        self.standardized_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_nf_garch_data(self):
        """Extract NF-GARCH data from Excel files."""
        print("Extracting NF-GARCH data from Excel files...")
        
        # Excel files to process
        excel_files = [
            "results/consolidated/Consolidated_NF_GARCH_Results.xlsx",
            "results/consolidated/NF_GARCH_Results_manual.xlsx",
            "results/Final/Consolidated_NF_GARCH_Results.xlsx",
            "results/Final/NF_GARCH_Results_manual.xlsx"
        ]
        
        all_nf_data = []
        
        for excel_file in excel_files:
            full_path = self.base_dir / excel_file
            if full_path.exists():
                print(f"Processing: {excel_file}")
                try:
                    # Read all sheets
                    excel_data = pd.read_excel(full_path, sheet_name=None)
                    
                    for sheet_name, sheet_data in excel_data.items():
                        if not sheet_data.empty:
                            print(f"  Sheet: {sheet_name} ({len(sheet_data)} rows)")
                            
                            # Process different sheet types
                            if 'Model_Performance' in sheet_name:
                                # This contains NF-GARCH model performance
                                for _, row in sheet_data.iterrows():
                                    if 'NF' in str(row.get('Model', '')) or 'NF--' in str(row.get('Model', '')):
                                        nf_record = {
                                            'Asset': 'NF_GARCH',
                                            'Model': row.get('Model', ''),
                                            'MSE': row.get('Avg_MSE', 0),
                                            'MAE': row.get('Avg_MAE', 0),
                                            'AIC': row.get('Avg_AIC', 0),
                                            'BIC': row.get('Avg_BIC', 0),
                                            'LogLikelihood': row.get('Avg_LogLik', 0),
                                            'Data_Source': 'NF_GARCH_Excel',
                                            'Source_File': excel_file,
                                            'Sheet_Name': sheet_name
                                        }
                                        all_nf_data.append(nf_record)
                                        print(f"    Found NF-GARCH model: {row.get('Model', '')}")
                            
                            elif 'Chrono_Split_NF_GARCH' in sheet_name:
                                # This contains detailed NF-GARCH results
                                for _, row in sheet_data.iterrows():
                                    nf_record = {
                                        'Asset': row.get('Asset', 'NF_GARCH'),
                                        'Model': row.get('Model', ''),
                                        'MSE': row.get('MSE', 0),
                                        'MAE': row.get('MAE', 0),
                                        'AIC': row.get('AIC', 0),
                                        'BIC': row.get('BIC', 0),
                                        'LogLikelihood': row.get('LogLikelihood', 0),
                                        'Data_Source': 'NF_GARCH_Chrono',
                                        'Source_File': excel_file,
                                        'Sheet_Name': sheet_name
                                    }
                                    all_nf_data.append(nf_record)
                            
                            elif 'NF_GARCH_Summary' in sheet_name:
                                # This contains NF-GARCH summary
                                for _, row in sheet_data.iterrows():
                                    nf_record = {
                                        'Asset': 'NF_GARCH',
                                        'Model': row.get('Model', ''),
                                        'MSE': row.get('Avg_MSE', 0),
                                        'MAE': row.get('Avg_MAE', 0),
                                        'AIC': row.get('Avg_AIC', 0),
                                        'BIC': row.get('Avg_BIC', 0),
                                        'LogLikelihood': row.get('Avg_LogLik', 0),
                                        'Data_Source': 'NF_GARCH_Summary',
                                        'Source_File': excel_file,
                                        'Sheet_Name': sheet_name
                                    }
                                    all_nf_data.append(nf_record)
                                    print(f"    Found NF-GARCH summary model: {row.get('Model', '')}")
                
                except Exception as e:
                    print(f"  Error processing {excel_file}: {e}")
        
        if all_nf_data:
            nf_df = pd.DataFrame(all_nf_data)
            print(f"Extracted {len(nf_df)} NF-GARCH records")
            print(f"Unique NF-GARCH models: {nf_df['Model'].unique()}")
            return nf_df
        else:
            print("No NF-GARCH data found in Excel files")
            return pd.DataFrame()
    
    def create_unified_datasets(self):
        """Create unified datasets with both standard and NF-GARCH data."""
        print("Creating unified datasets...")
        
        # Extract NF-GARCH data
        nf_garch_data = self.extract_nf_garch_data()
        
        # Load standard GARCH data
        standard_data = pd.read_csv(self.standardized_dir / "model_performance_metrics.csv")
        standard_data['Data_Source'] = 'Standard_GARCH'
        
        # Combine datasets
        if not nf_garch_data.empty:
            # Ensure both datasets have the same columns
            common_columns = ['Asset', 'Model', 'MSE', 'MAE', 'Data_Source']
            
            # Filter to common columns
            standard_filtered = standard_data[common_columns]
            nf_filtered = nf_garch_data[common_columns]
            
            # Combine
            unified_data = pd.concat([standard_filtered, nf_filtered], ignore_index=True)
            
            # Add model type classification
            unified_data['Model_Type'] = unified_data['Model'].apply(self.classify_model_type)
            
            # Save unified dataset
            unified_data.to_csv(self.standardized_dir / "unified_model_performance.csv", index=False)
            print(f"Created unified model performance: {len(unified_data)} records")
            print(f"Model types: {unified_data['Model_Type'].value_counts().to_dict()}")
            
            # Create NF-GARCH specific dataset
            nf_garch_data.to_csv(self.standardized_dir / "nf_garch_performance.csv", index=False)
            print(f"Created NF-GARCH specific dataset: {len(nf_garch_data)} records")
            
        else:
            print("No NF-GARCH data to unify")
    
    def classify_model_type(self, model_name):
        """Classify model type based on name."""
        if pd.isna(model_name):
            return 'Unknown'
        
        model_str = str(model_name).upper()
        
        if any(keyword in model_str for keyword in ['NF', 'NF--', 'NFGARCH', 'NF_GARCH']):
            return 'NF-GARCH'
        elif any(keyword in model_str for keyword in ['SGARCH', 'EGARCH', 'GJR', 'TGARCH']):
            return 'Standard GARCH'
        else:
            return 'Other'
    
    def create_summary_report(self):
        """Create a summary report of the data extraction."""
        print("Creating summary report...")
        
        # Load unified data
        unified_data = pd.read_csv(self.standardized_dir / "unified_model_performance.csv")
        
        summary = {
            'Extraction_Date': datetime.now().isoformat(),
            'Total_Records': len(unified_data),
            'Model_Types': unified_data['Model_Type'].value_counts().to_dict(),
            'Data_Sources': unified_data['Data_Source'].value_counts().to_dict(),
            'Unique_Models': list(unified_data['Model'].unique()),
            'Assets': list(unified_data['Asset'].unique())
        }
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(self.standardized_dir / "data_extraction_summary.csv", index=False)
        
        print("Summary report created")
        return summary
    
    def run(self):
        """Run the complete data extraction process."""
        print("=== EXTRACTING NF-GARCH DATA ===")
        
        # Create unified datasets
        self.create_unified_datasets()
        
        # Create summary report
        self.create_summary_report()
        
        print("\n=== EXTRACTION COMPLETE ===")
        print(f"Results saved to: {self.standardized_dir}")

def main():
    """Main entry point."""
    extractor = NFGARCHDataExtractor()
    extractor.run()

if __name__ == "__main__":
    main()
