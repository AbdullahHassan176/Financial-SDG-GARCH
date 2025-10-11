#!/usr/bin/env python3
"""
Standardize output file naming and structure for better parsing and understanding.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import shutil

class OutputStandardizer:
    """Standardize output file naming and structure."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.standardized_dir = self.base_dir / "outputs" / "standardized"
        self.standardized_dir.mkdir(parents=True, exist_ok=True)
        
        # New standardized naming conventions
        self.naming_map = {
            # Model Performance
            "forecast_accuracy_summary.csv": "model_performance_metrics.csv",
            "model_ranking.csv": "model_rankings.csv",
            "stylized_facts_summary.csv": "stylized_facts_analysis.csv",
            "asset_type_comparison.csv": "asset_performance_comparison.csv",
            "best_models_per_asset.csv": "best_models_by_asset.csv",
            
            # Risk Assessment
            "var_backtest_summary.csv": "risk_assessment_results.csv",
            "model_performance_summary.csv": "var_model_performance.csv",
            "nfgarch_var_backtest_summary.csv": "nf_garch_risk_assessment.csv",
            
            # Stress Testing
            "stress_test_summary.csv": "stress_testing_results.csv",
            "model_robustness_scores.csv": "model_robustness_analysis.csv",
            "nfgarch_stress_test_summary.csv": "nf_garch_stress_testing.csv",
            "nfgarch_scenario_comparison.csv": "nf_garch_scenario_analysis.csv",
            
            # Excel Files
            "Consolidated_NF_GARCH_Results.xlsx": "nf_garch_comprehensive_results.xlsx",
            "NF_GARCH_Results_manual.xlsx": "nf_garch_manual_results.xlsx",
            "Dissertation_Consolidated_Results.xlsx": "dissertation_final_results.xlsx"
        }
        
        # Sheet naming standardization
        self.sheet_naming_map = {
            "Model_Performance_Summary": "Model_Performance",
            "Chrono_Split_NF_GARCH": "NF_GARCH_Chronological_Results",
            "NF_GARCH_Summary": "NF_GARCH_Summary",
            "Chrono_Summary": "Chronological_Summary",
            "TS_CV_Summary": "Time_Series_CV_Summary",
            "Split_Comparison": "Model_Comparison",
            "Asset_Comparison": "Asset_Analysis",
            "NFGARCH_VaR_Summary": "NF_GARCH_Risk_Assessment",
            "NFGARCH_Stress_Summary": "NF_GARCH_Stress_Testing"
        }
    
    def standardize_csv_files(self):
        """Standardize CSV file naming and structure."""
        print("Standardizing CSV files...")
        
        # Standardize model evaluation files
        model_eval_dir = self.base_dir / "outputs" / "model_eval" / "tables"
        if model_eval_dir.exists():
            for file in model_eval_dir.glob("*.csv"):
                if file.name in self.naming_map:
                    new_name = self.naming_map[file.name]
                    new_path = self.standardized_dir / new_name
                    shutil.copy2(file, new_path)
                    print(f"  Standardized: {file.name} -> {new_name}")
        
        # Standardize VaR backtesting files
        var_backtest_dir = self.base_dir / "outputs" / "var_backtest" / "tables"
        if var_backtest_dir.exists():
            for file in var_backtest_dir.glob("*.csv"):
                if file.name in self.naming_map:
                    new_name = self.naming_map[file.name]
                    new_path = self.standardized_dir / new_name
                    shutil.copy2(file, new_path)
                    print(f"  Standardized: {file.name} -> {new_name}")
        
        # Standardize stress testing files
        stress_test_dir = self.base_dir / "outputs" / "stress_tests" / "tables"
        if stress_test_dir.exists():
            for file in stress_test_dir.glob("*.csv"):
                if file.name in self.naming_map:
                    new_name = self.naming_map[file.name]
                    new_path = self.standardized_dir / new_name
                    shutil.copy2(file, new_path)
                    print(f"  Standardized: {file.name} -> {new_name}")
    
    def standardize_excel_files(self):
        """Standardize Excel file naming and structure."""
        print("Standardizing Excel files...")
        
        # Process consolidated results
        consolidated_dir = self.base_dir / "results" / "consolidated"
        if consolidated_dir.exists():
            for file in consolidated_dir.glob("*.xlsx"):
                if file.name in self.naming_map:
                    new_name = self.naming_map[file.name]
                    new_path = self.standardized_dir / new_name
                    
                    # Copy and standardize sheet names
                    self.standardize_excel_sheets(file, new_path)
                    print(f"  Standardized: {file.name} -> {new_name}")
        
        # Process Final results
        final_dir = self.base_dir / "results" / "Final"
        if final_dir.exists():
            for file in final_dir.glob("*.xlsx"):
                if file.name in self.naming_map:
                    new_name = self.naming_map[file.name]
                    new_path = self.standardized_dir / new_name
                    
                    # Copy and standardize sheet names
                    self.standardize_excel_sheets(file, new_path)
                    print(f"  Standardized: {file.name} -> {new_name}")
    
    def standardize_excel_sheets(self, source_file, target_file):
        """Standardize Excel sheet names and structure."""
        try:
            # Read all sheets
            excel_data = pd.read_excel(source_file, sheet_name=None)
            
            # Create new workbook with standardized sheet names
            with pd.ExcelWriter(target_file, engine='openpyxl') as writer:
                for sheet_name, sheet_data in excel_data.items():
                    # Standardize sheet name
                    new_sheet_name = self.sheet_naming_map.get(sheet_name, sheet_name)
                    
                    # Clean and standardize data
                    cleaned_data = self.clean_dataframe(sheet_data)
                    
                    # Write to new file
                    cleaned_data.to_excel(writer, sheet_name=new_sheet_name, index=False)
            
            print(f"    Standardized sheets in {source_file.name}")
            
        except Exception as e:
            print(f"    Error standardizing {source_file.name}: {e}")
    
    def clean_dataframe(self, df):
        """Clean and standardize dataframe structure."""
        if df.empty:
            return df
        
        # Standardize column names
        column_mapping = {
            'Model': 'Model_Name',
            'Asset': 'Asset_Name',
            'MSE': 'Mean_Squared_Error',
            'MAE': 'Mean_Absolute_Error',
            'RMSE': 'Root_Mean_Squared_Error',
            'AIC': 'Akaike_Information_Criterion',
            'BIC': 'Bayesian_Information_Criterion',
            'LogLikelihood': 'Log_Likelihood',
            'Violation_Rate': 'VaR_Violation_Rate',
            'Kupiec_PValue': 'Kupiec_Test_P_Value',
            'Christoffersen_PValue': 'Christoffersen_Test_P_Value',
            'DQ_PValue': 'DQ_Test_P_Value'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Add model type classification
        if 'Model_Name' in df.columns:
            df['Model_Type'] = df['Model_Name'].apply(self.classify_model_type)
        
        # Add performance ranking
        if 'Mean_Squared_Error' in df.columns:
            df['Performance_Rank'] = df['Mean_Squared_Error'].rank(ascending=True)
        
        return df
    
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
    
    def create_unified_data_structure(self):
        """Create a unified data structure for easier parsing."""
        print("Creating unified data structure...")
        
        # Load all standardized data
        all_data = {}
        
        # Load CSV data
        for csv_file in self.standardized_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                all_data[csv_file.stem] = df
                print(f"  Loaded: {csv_file.name} ({len(df)} records)")
            except Exception as e:
                print(f"  Error loading {csv_file.name}: {e}")
        
        # Create unified model performance data
        self.create_unified_model_performance(all_data)
        
        # Create unified risk assessment data
        self.create_unified_risk_assessment(all_data)
        
        # Create unified stress testing data
        self.create_unified_stress_testing(all_data)
        
        # Create master summary
        self.create_master_summary(all_data)
    
    def create_unified_model_performance(self, all_data):
        """Create unified model performance data."""
        print("Creating unified model performance data...")
        
        # Combine all model performance data
        performance_data = []
        
        # Add from model performance metrics
        if 'model_performance_metrics' in all_data:
            df = all_data['model_performance_metrics'].copy()
            df['Data_Source'] = 'Model_Evaluation'
            performance_data.append(df)
        
        # Add from NF-GARCH results
        for key, df in all_data.items():
            if 'nf_garch' in key.lower() and 'Model_Name' in df.columns:
                df_copy = df.copy()
                df_copy['Data_Source'] = 'NF_GARCH_Results'
                performance_data.append(df_copy)
        
        if performance_data:
            unified_performance = pd.concat(performance_data, ignore_index=True)
            unified_performance.to_csv(
                self.standardized_dir / "unified_model_performance.csv", 
                index=False
            )
            print(f"  Created unified model performance: {len(unified_performance)} records")
    
    def create_unified_risk_assessment(self, all_data):
        """Create unified risk assessment data."""
        print("Creating unified risk assessment data...")
        
        risk_data = []
        
        # Add from risk assessment results
        if 'risk_assessment_results' in all_data:
            df = all_data['risk_assessment_results'].copy()
            df['Data_Source'] = 'VaR_Backtesting'
            risk_data.append(df)
        
        # Add from NF-GARCH risk assessment
        if 'nf_garch_risk_assessment' in all_data:
            df = all_data['nf_garch_risk_assessment'].copy()
            df['Data_Source'] = 'NF_GARCH_Risk'
            risk_data.append(df)
        
        if risk_data:
            unified_risk = pd.concat(risk_data, ignore_index=True)
            unified_risk.to_csv(
                self.standardized_dir / "unified_risk_assessment.csv", 
                index=False
            )
            print(f"  Created unified risk assessment: {len(unified_risk)} records")
    
    def create_unified_stress_testing(self, all_data):
        """Create unified stress testing data."""
        print("Creating unified stress testing data...")
        
        stress_data = []
        
        # Add from stress testing results
        if 'stress_testing_results' in all_data:
            df = all_data['stress_testing_results'].copy()
            df['Data_Source'] = 'Stress_Testing'
            stress_data.append(df)
        
        # Add from NF-GARCH stress testing
        if 'nf_garch_stress_testing' in all_data:
            df = all_data['nf_garch_stress_testing'].copy()
            df['Data_Source'] = 'NF_GARCH_Stress'
            stress_data.append(df)
        
        if stress_data:
            unified_stress = pd.concat(stress_data, ignore_index=True)
            unified_stress.to_csv(
                self.standardized_dir / "unified_stress_testing.csv", 
                index=False
            )
            print(f"  Created unified stress testing: {len(unified_stress)} records")
    
    def create_master_summary(self, all_data):
        """Create master summary file."""
        print("Creating master summary...")
        
        summary = {
            'Standardization_Date': datetime.now().isoformat(),
            'Total_Files_Processed': len(all_data),
            'Data_Sources': list(all_data.keys()),
            'File_Counts': {key: len(df) for key, df in all_data.items()}
        }
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(
            self.standardized_dir / "standardization_summary.csv", 
            index=False
        )
        
        print(f"  Created master summary")
    
    def run(self):
        """Run the complete standardization process."""
        print("=== STANDARDIZING OUTPUT FILES ===")
        print(f"Output directory: {self.standardized_dir}")
        
        # Standardize all files
        self.standardize_csv_files()
        self.standardize_excel_files()
        self.create_unified_data_structure()
        
        print("\n=== STANDARDIZATION COMPLETE ===")
        print(f"Standardized files saved to: {self.standardized_dir}")
        print("\nNew naming conventions:")
        for old, new in self.naming_map.items():
            print(f"  {old} -> {new}")

def main():
    """Main entry point."""
    standardizer = OutputStandardizer()
    standardizer.run()

if __name__ == "__main__":
    main()
