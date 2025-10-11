#!/usr/bin/env python3
"""
Path parsing utilities for extracting metadata from file paths and content.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import json
import yaml


def parse_asset_from_path(file_path: str) -> Optional[str]:
    """
    Extract asset name from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Asset name or None if not found
    """
    # Known assets from the repository
    known_assets = [
        'AMZN', 'CAT', 'MSFT', 'NVDA', 'PG', 'WMT',  # Equity
        'EURUSD', 'EURZAR', 'GBPCNY', 'GBPUSD', 'GBPZAR', 'USDZAR'  # FX
    ]
    
    path_lower = file_path.lower()
    
    # Check for asset names in path
    for asset in known_assets:
        if asset.lower() in path_lower:
            return asset
    
    # Try to extract from common patterns
    patterns = [
        r'/([A-Z]{3,6})_',  # Pattern like /AMZN_ or /EURUSD_
        r'([A-Z]{3,6})\.csv',  # Pattern like AMZN.csv
        r'([A-Z]{3,6})\.png',  # Pattern like AMZN.png
    ]
    
    for pattern in patterns:
        match = re.search(pattern, file_path)
        if match:
            return match.group(1)
    
    return None


def parse_model_from_path(file_path: str) -> Optional[str]:
    """
    Extract model name from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Model name or None if not found
    """
    # Known models from the repository
    known_models = [
        'sGARCH_norm', 'sGARCH_sstd', 'eGARCH', 'gjrGARCH', 'TGARCH',
        'NF_sGARCH_norm', 'NF_sGARCH_sstd', 'NF_eGARCH', 'NF_gjrGARCH', 'NF_TGARCH'
    ]
    
    path_lower = file_path.lower()
    
    # Check for model names in path
    for model in known_models:
        if model.lower() in path_lower:
            return model
    
    # Try to extract from common patterns
    patterns = [
        r'([a-zA-Z_]+)_[a-zA-Z_]+\.csv',  # Pattern like sGARCH_norm_AMZN.csv
        r'([a-zA-Z_]+)_[a-zA-Z_]+\.png',  # Pattern like sGARCH_norm_AMZN.png
        r'([a-zA-Z_]+)_results',  # Pattern like sGARCH_results
    ]
    
    for pattern in patterns:
        match = re.search(pattern, file_path)
        if match:
            return match.group(1)
    
    return None


def parse_split_type_from_path(file_path: str) -> Optional[str]:
    """
    Extract split type from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Split type ('chrono' or 'tscv') or None if not found
    """
    path_lower = file_path.lower()
    
    if 'tscv' in path_lower or 'ts_cv' in path_lower or 'cross_validation' in path_lower:
        return 'tscv'
    elif 'chrono' in path_lower or 'chronological' in path_lower:
        return 'chrono'
    elif 'cv' in path_lower and 'tscv' not in path_lower:
        return 'tscv'  # Assume CV means time series CV
    else:
        return 'chrono'  # Default to chronological


def parse_fold_from_path(file_path: str) -> Optional[Union[int, str]]:
    """
    Extract fold number from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Fold number or 'all' if not found
    """
    # Look for fold patterns
    patterns = [
        r'fold_(\d+)',  # fold_1, fold_2, etc.
        r'fold(\d+)',   # fold1, fold2, etc.
        r'(\d+)_fold',  # 1_fold, 2_fold, etc.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, file_path)
        if match:
            return int(match.group(1))
    
    return 'all'  # Default to 'all' if no fold specified


def parse_metric_from_content(file_path: str) -> List[str]:
    """
    Extract metric names from file content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        List of metric names found in the file
    """
    metrics = []
    
    try:
        if file_path.endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(file_path, nrows=1)  # Read only header
            metrics = list(df.columns)
        elif file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    metrics = list(data.keys())
                elif isinstance(data, list) and len(data) > 0:
                    metrics = list(data[0].keys()) if isinstance(data[0], dict) else []
    except Exception:
        pass
    
    return metrics


def parse_model_family(model_name: str) -> str:
    """
    Determine model family from model name.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Model family ('GARCH' or 'NF-GARCH')
    """
    if model_name and ('NF' in model_name or 'Flow' in model_name or 'nf' in model_name.lower()):
        return 'NF-GARCH'
    else:
        return 'GARCH'


def parse_asset_type(asset_name: str) -> str:
    """
    Determine asset type from asset name.
    
    Args:
        asset_name: Name of the asset
        
    Returns:
        Asset type ('Equity' or 'FX')
    """
    if asset_name:
        # FX pairs typically have 6 characters (e.g., EURUSD, GBPUSD)
        if len(asset_name) == 6 and asset_name.isalpha():
            return 'FX'
        else:
            return 'Equity'
    return 'Unknown'


def get_metric_polarity(metric_name: str) -> str:
    """
    Determine if a metric is better when higher or lower.
    
    Args:
        metric_name: Name of the metric
        
    Returns:
        'higher' if higher is better, 'lower' if lower is better
    """
    # Metrics where lower is better
    lower_is_better = [
        'mse', 'mae', 'mape', 'aic', 'bic', 'rmse', 'error', 'loss',
        'violation_rate', 'qstat', 'archlm_pval'
    ]
    
    # Metrics where higher is better
    higher_is_better = [
        'loglik', 'log_likelihood', 'likelihood', 'win_rate', 'accuracy',
        'r_squared', 'correlation', 'p_value', 'convergence'
    ]
    
    metric_lower = metric_name.lower()
    
    for metric in lower_is_better:
        if metric in metric_lower:
            return 'lower'
    
    for metric in higher_is_better:
        if metric in metric_lower:
            return 'higher'
    
    # Default to lower is better for unknown metrics
    return 'lower'


def extract_config_hash(file_path: str) -> Optional[str]:
    """
    Extract configuration hash from adjacent config files.
    
    Args:
        file_path: Path to the result file
        
    Returns:
        Configuration hash or None if not found
    """
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    
    # Look for config files in the same directory
    config_files = [
        'config.json', 'config.yaml', 'config.yml',
        'params.json', 'params.yaml', 'params.yml',
        'settings.json', 'settings.yaml', 'settings.yml'
    ]
    
    for config_file in config_files:
        config_path = os.path.join(file_dir, config_file)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    if config_file.endswith('.json'):
                        config_data = json.load(f)
                    else:
                        config_data = yaml.safe_load(f)
                
                # Create a simple hash from the config data
                import hashlib
                config_str = json.dumps(config_data, sort_keys=True)
                return hashlib.md5(config_str.encode()).hexdigest()[:8]
            except Exception:
                continue
    
    return None


def parse_file_metadata(file_path: str) -> Dict[str, Union[str, int, List[str], None]]:
    """
    Parse all metadata from a file path and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing all parsed metadata
    """
    metadata = {
        'file_path': file_path,
        'asset': parse_asset_from_path(file_path),
        'model': parse_model_from_path(file_path),
        'split_type': parse_split_type_from_path(file_path),
        'fold': parse_fold_from_path(file_path),
        'metrics': parse_metric_from_content(file_path),
        'config_hash': extract_config_hash(file_path)
    }
    
    # Add derived fields
    if metadata['model']:
        metadata['model_family'] = parse_model_family(metadata['model'])
    else:
        metadata['model_family'] = None
    
    if metadata['asset']:
        metadata['asset_type'] = parse_asset_type(metadata['asset'])
    else:
        metadata['asset_type'] = None
    
    return metadata


def normalize_metric_name(metric_name: str) -> str:
    """
    Normalize metric names to standard format.
    
    Args:
        metric_name: Original metric name
        
    Returns:
        Normalized metric name
    """
    # Common normalizations
    normalizations = {
        'loglik': 'LogLikelihood',
        'log_likelihood': 'LogLikelihood',
        'loglikelihood': 'LogLikelihood',
        'aic': 'AIC',
        'bic': 'BIC',
        'mse': 'MSE',
        'mae': 'MAE',
        'mape': 'MAPE',
        'rmse': 'RMSE',
        'r_squared': 'R_Squared',
        'r2': 'R_Squared',
        'correlation': 'Correlation',
        'win_rate': 'Win_Rate',
        'violation_rate': 'Violation_Rate',
        'p_value': 'P_Value',
        'qstat': 'QStat',
        'archlm_pval': 'ARCHLM_PValue'
    }
    
    metric_lower = metric_name.lower().replace('_', '').replace('-', '')
    
    for key, value in normalizations.items():
        if key.lower().replace('_', '').replace('-', '') == metric_lower:
            return value
    
    # Return original if no normalization found
    return metric_name


if __name__ == "__main__":
    # Test the parsing functions
    test_paths = [
        "outputs/model_eval/tables/model_ranking.csv",
        "outputs/var_backtest/tables/var_backtest_summary.csv",
        "results/plots/exhaustive/histograms_Real_Equity/AMZN_histogram.png",
        "nf_generated_residuals/sGARCH_norm_equity_AMZN_residuals_synthetic.csv"
    ]
    
    for path in test_paths:
        print(f"\nPath: {path}")
        metadata = parse_file_metadata(path)
        for key, value in metadata.items():
            print(f"  {key}: {value}")
