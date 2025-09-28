#!/usr/bin/env python3
"""
Results consolidation script for NF-GARCH research repository.
Collects all tabular results into a single Excel workbook with long-format master sheet.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import hashlib
import logging

# Add the tools directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from _util.path_parsing import (
    parse_file_metadata, normalize_metric_name, get_metric_polarity
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResultsCollector:
    """Main class for collecting and consolidating results."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.artifacts_dir = self.base_dir / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)
        
        # Initialize data storage
        self.master_data = []
        self.skipped_files = []
        self.run_id = self._generate_run_id()
        
        # Metric polarity mapping
        self.metric_polarity = {
            'MSE': 'lower', 'MAE': 'lower', 'MAPE': 'lower', 'RMSE': 'lower',
            'AIC': 'lower', 'BIC': 'lower', 'Error': 'lower', 'Loss': 'lower',
            'LogLikelihood': 'higher', 'LogLik': 'higher', 'Likelihood': 'higher',
            'Win_Rate': 'higher', 'Accuracy': 'higher', 'R_Squared': 'higher',
            'Correlation': 'higher', 'Convergence': 'higher'
        }
    
    def _generate_run_id(self) -> str:
        """Generate a unique run ID based on timestamp and config."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"run_{timestamp}"
    
    def scan_result_files(self) -> List[Path]:
        """Scan the repository for all result files."""
        result_files = []
        
        # Define search patterns
        patterns = [
            "**/*.csv",
            "**/*.xlsx", 
            "**/*.json"
        ]
        
        # Directories to search
        search_dirs = [
            "outputs",
            "results", 
            "data/processed",
            "nf_generated_residuals"
        ]
        
        for pattern in patterns:
            for search_dir in search_dirs:
                search_path = self.base_dir / search_dir
                if search_path.exists():
                    for file_path in search_path.glob(pattern):
                        # Skip certain files
                        if self._should_skip_file(file_path):
                            continue
                        result_files.append(file_path)
        
        logger.info(f"Found {len(result_files)} result files to process")
        return result_files
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped."""
        skip_patterns = [
            "archive/",
            "old_",
            "duplicate_",
            "legacy_",
            "unused_",
            "__pycache__/",
            ".git/",
            "node_modules/",
            "checkpoints/",
            "environment/",
            "scripts/",
            "tools/",
            "tests/"
        ]
        
        file_str = str(file_path)
        for pattern in skip_patterns:
            if pattern in file_str:
                return True
        
        # Skip very small files (likely empty)
        if file_path.stat().st_size < 100:
            return True
            
        return False
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a single result file and extract data."""
        try:
            metadata = parse_file_metadata(str(file_path))
            
            # Read the file based on extension
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix == '.xlsx':
                # Read all sheets
                excel_data = pd.read_excel(file_path, sheet_name=None)
                all_data = []
                for sheet_name, sheet_df in excel_data.items():
                    sheet_data = self._process_dataframe(sheet_df, metadata, sheet_name)
                    all_data.extend(sheet_data)
                return all_data
            elif file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                df = pd.json_normalize(data)
            else:
                logger.warning(f"Unsupported file type: {file_path}")
                return []
            
            return self._process_dataframe(df, metadata)
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            self.skipped_files.append({
                'file': str(file_path),
                'reason': str(e)
            })
            return []
    
    def _process_dataframe(self, df: pd.DataFrame, metadata: Dict, sheet_name: str = None) -> List[Dict[str, Any]]:
        """Process a DataFrame and convert to long format."""
        if df.empty:
            return []
        
        # Clean column names
        df.columns = [col.strip().replace(' ', '_') for col in df.columns]
        
        # Identify key columns
        asset_col = self._find_column(df, ['asset', 'Asset', 'ASSET', 'symbol', 'Symbol'])
        model_col = self._find_column(df, ['model', 'Model', 'MODEL', 'method', 'Method'])
        metric_cols = self._get_metric_columns(df)
        
        # Extract data
        records = []
        for idx, row in df.iterrows():
            # Get asset and model from row or metadata
            asset = self._get_value(row, asset_col) or metadata.get('asset', 'Unknown')
            model = self._get_value(row, model_col) or metadata.get('model', 'Unknown')
            
            # If no asset/model found, use file-based defaults
            if asset == 'Unknown' and model == 'Unknown':
                # Try to extract from file path
                file_path = metadata.get('file_path', '')
                if 'model_ranking' in file_path:
                    asset = 'All_Assets'
                    model = 'Summary'
                elif 'forecast_accuracy' in file_path:
                    asset = 'All_Assets'
                    model = 'Summary'
                else:
                    asset = 'Unknown'
                    model = 'Unknown'
            
            # Handle NaN values
            if pd.isna(asset) or asset == 'nan':
                asset = 'All_Assets'
            if pd.isna(model) or model == 'nan':
                model = 'Summary'
            
            # Process each metric
            for metric_col in metric_cols:
                if pd.notna(row[metric_col]):
                    metric_name = normalize_metric_name(metric_col)
                    
                    # Determine model family based on source file path
                    source_file = str(metadata['file_path'])
                    if 'nf_generated_residuals' in source_file:
                        model_family = 'NF-GARCH'
                    else:
                        model_family = metadata.get('model_family') or self._infer_model_family(model)
                    
                    record = {
                        'asset': asset,
                        'model': model,
                        'model_family': model_family,
                        'split_type': metadata.get('split_type', 'chrono'),
                        'fold': metadata.get('fold', 'all'),
                        'metric': metric_name,
                        'value': float(row[metric_col]) if pd.notna(row[metric_col]) else None,
                        'run_id': self.run_id,
                        'timestamp': datetime.now().isoformat(),
                        'source_file': source_file,
                        'sheet_name': sheet_name,
                        'row_index': idx,
                        'asset_type': metadata.get('asset_type', 'Unknown'),
                        'config_hash': metadata.get('config_hash')
                    }
                    
                    # Add any additional columns from the original data
                    for col in df.columns:
                        if col not in [asset_col, model_col] and col not in metric_cols:
                            record[f'original_{col}'] = row[col]
                    
                    records.append(record)
        
        return records
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by trying multiple possible names."""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def _get_value(self, row: pd.Series, col: Optional[str]) -> Any:
        """Get value from row, handling None column."""
        if col is None:
            return None
        return row[col] if col in row.index else None
    
    def _get_metric_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify metric columns in the DataFrame."""
        metric_indicators = [
            'mse', 'mae', 'mape', 'rmse', 'aic', 'bic', 'loglik', 'log_likelihood',
            'win_rate', 'accuracy', 'r_squared', 'correlation', 'p_value',
            'violation_rate', 'qstat', 'archlm', 'convergence', 'error', 'loss',
            'avg_mse', 'avg_mae', 'avg_mape'
        ]
        
        metric_cols = []
        for col in df.columns:
            col_lower = col.lower()
            if any(indicator in col_lower for indicator in metric_indicators):
                metric_cols.append(col)
            elif col not in ['asset', 'model', 'Asset', 'Model', 'index', 'Index']:
                # Assume it's a metric if it's not a key column
                metric_cols.append(col)
        
        return metric_cols
    
    def _infer_model_family(self, model: str) -> str:
        """Infer model family from model name."""
        if model and ('NF' in model or 'Flow' in model or 'nf' in model.lower()):
            return 'NF-GARCH'
        else:
            return 'GARCH'
    
    def create_summary_tables(self, master_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create summary tables from master data."""
        summaries = {}
        
        # Summary by model
        if not master_df.empty:
            model_summary = master_df.groupby(['model', 'metric'])['value'].agg([
                'mean', 'std', 'min', 'max', 'count'
            ]).reset_index()
            summaries['summary_by_model'] = model_summary
            
            # Summary by asset and model
            asset_model_summary = master_df.groupby(['asset', 'model', 'metric'])['value'].agg([
                'mean', 'std', 'min', 'max', 'count'
            ]).reset_index()
            summaries['summary_by_asset_model'] = asset_model_summary
            
            # Win rates (NF-GARCH vs GARCH)
            winrates = self._calculate_winrates(master_df)
            summaries['winrates'] = winrates
        
        return summaries
    
    def _calculate_winrates(self, master_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate win rates between NF-GARCH and GARCH models."""
        if master_df.empty:
            return pd.DataFrame()
        
        winrate_data = []
        
        # Get summary statistics for each model family
        nf_models = master_df[master_df['model_family'] == 'NF-GARCH']
        garch_models = master_df[master_df['model_family'] == 'GARCH']
        
        if nf_models.empty or garch_models.empty:
            # Handle case where one or both model families are missing
            pass
        else:
            # Both model families have data, but no common metrics for comparison
            # Create a summary showing what data we have
            winrate_data.append({
                'metric': 'Data_Summary',
                'split_type': 'All',
                'nf_model': f'{len(nf_models)} NF-GARCH models',
                'garch_model': f'{len(garch_models)} GARCH models',
                'nf_value': len(nf_models),
                'garch_value': len(garch_models),
                'nf_wins': 'N/A',
                'improvement_pct': 'N/A',
                'note': 'No common metrics for direct comparison'
            })
            
            # Add model family summaries
            nf_metrics = nf_models['metric'].value_counts()
            garch_metrics = garch_models['metric'].value_counts()
            
            for metric in nf_metrics.index:
                winrate_data.append({
                    'metric': f'NF-GARCH_{metric}',
                    'split_type': 'All',
                    'nf_model': f'{nf_metrics[metric]} records',
                    'garch_model': 'N/A',
                    'nf_value': nf_metrics[metric],
                    'garch_value': 0,
                    'nf_wins': 'N/A',
                    'improvement_pct': 'N/A',
                    'note': 'NF-GARCH synthetic data'
                })
            
            for metric in garch_metrics.index:
                winrate_data.append({
                    'metric': f'GARCH_{metric}',
                    'split_type': 'All',
                    'nf_model': 'N/A',
                    'garch_model': f'{garch_metrics[metric]} records',
                    'nf_value': 0,
                    'garch_value': garch_metrics[metric],
                    'nf_wins': 'N/A',
                    'improvement_pct': 'N/A',
                    'note': 'GARCH performance metrics'
                })
        
        return pd.DataFrame(winrate_data)
    
    def save_to_excel(self, master_df: pd.DataFrame, summaries: Dict[str, pd.DataFrame]):
        """Save all data to Excel workbook."""
        output_file = self.artifacts_dir / "results_consolidated.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Master sheet
            master_df.to_excel(writer, sheet_name='master', index=False)
            
            # Summary sheets
            for sheet_name, df in summaries.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Add metadata sheet
            metadata_df = pd.DataFrame([
                {'Field': 'Total Records', 'Value': len(master_df)},
                {'Field': 'Unique Assets', 'Value': master_df['asset'].nunique() if not master_df.empty else 0},
                {'Field': 'Unique Models', 'Value': master_df['model'].nunique() if not master_df.empty else 0},
                {'Field': 'Unique Metrics', 'Value': master_df['metric'].nunique() if not master_df.empty else 0},
                {'Field': 'Run ID', 'Value': self.run_id},
                {'Field': 'Generated At', 'Value': datetime.now().isoformat()},
                {'Field': 'Files Processed', 'Value': len(self.master_data)},
                {'Field': 'Files Skipped', 'Value': len(self.skipped_files)}
            ])
            metadata_df.to_excel(writer, sheet_name='metadata', index=False)
        
        logger.info(f"Results saved to: {output_file}")
        return output_file
    
    def run(self) -> Dict[str, Any]:
        """Main execution method."""
        logger.info("Starting results collection...")
        
        # Scan for files
        result_files = self.scan_result_files()
        
        # Process each file
        for file_path in result_files:
            logger.info(f"Processing: {file_path}")
            file_data = self.process_file(file_path)
            self.master_data.extend(file_data)
        
        # Create master DataFrame
        master_df = pd.DataFrame(self.master_data)
        
        if master_df.empty:
            logger.warning("No data collected!")
            return {'status': 'failed', 'reason': 'No data collected'}
        
        # Create summary tables
        summaries = self.create_summary_tables(master_df)
        
        # Save to Excel
        output_file = self.save_to_excel(master_df, summaries)
        
        # Generate report
        report = {
            'status': 'success',
            'output_file': str(output_file),
            'total_records': len(master_df),
            'unique_assets': master_df['asset'].nunique(),
            'unique_models': master_df['model'].nunique(),
            'unique_metrics': master_df['metric'].nunique(),
            'files_processed': len(result_files),
            'files_skipped': len(self.skipped_files),
            'skipped_files': self.skipped_files
        }
        
        logger.info(f"Collection complete: {report}")
        return report


def main():
    """Main entry point."""
    collector = ResultsCollector()
    report = collector.run()
    
    print("\n" + "="*50)
    print("RESULTS COLLECTION SUMMARY")
    print("="*50)
    print(f"Status: {report['status']}")
    print(f"Output File: {report['output_file']}")
    print(f"Total Records: {report['total_records']}")
    print(f"Unique Assets: {report['unique_assets']}")
    print(f"Unique Models: {report['unique_models']}")
    print(f"Unique Metrics: {report['unique_metrics']}")
    print(f"Files Processed: {report['files_processed']}")
    print(f"Files Skipped: {report['files_skipped']}")
    
    if report['skipped_files']:
        print("\nSkipped Files:")
        for skip in report['skipped_files']:
            print(f"  - {skip['file']}: {skip['reason']}")


if __name__ == "__main__":
    main()
