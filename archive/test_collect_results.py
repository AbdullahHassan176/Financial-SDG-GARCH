#!/usr/bin/env python3
"""
Unit tests for the results collection functionality.
"""

import unittest
import tempfile
import os
import pandas as pd
import json
from pathlib import Path
import sys

# Add the tools directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

from _util.path_parsing import (
    parse_asset_from_path, parse_model_from_path, parse_split_type_from_path,
    parse_fold_from_path, parse_model_family, parse_asset_type, get_metric_polarity,
    normalize_metric_name
)


class TestPathParsing(unittest.TestCase):
    """Test path parsing utilities."""
    
    def test_parse_asset_from_path(self):
        """Test asset parsing from file paths."""
        test_cases = [
            ("outputs/model_eval/tables/AMZN_results.csv", "AMZN"),
            ("results/plots/EURUSD_forecast.png", "EURUSD"),
            ("nf_generated_residuals/sGARCH_norm_equity_AMZN_residuals.csv", "AMZN"),
            ("outputs/var_backtest/tables/GBPUSD_backtest.csv", "GBPUSD"),
            ("some_random_file.csv", None)
        ]
        
        for path, expected in test_cases:
            with self.subTest(path=path):
                result = parse_asset_from_path(path)
                self.assertEqual(result, expected)
    
    def test_parse_model_from_path(self):
        """Test model parsing from file paths."""
        test_cases = [
            ("outputs/model_eval/tables/sGARCH_results.csv", "sGARCH"),
            ("results/plots/eGARCH_forecast.png", "eGARCH"),
            ("nf_generated_residuals/sGARCH_norm_equity_AMZN_residuals.csv", "sGARCH_norm"),
            ("outputs/var_backtest/tables/gjrGARCH_backtest.csv", "gjrGARCH"),
            ("some_random_file.csv", None)
        ]
        
        for path, expected in test_cases:
            with self.subTest(path=path):
                result = parse_model_from_path(path)
                self.assertEqual(result, expected)
    
    def test_parse_split_type_from_path(self):
        """Test split type parsing from file paths."""
        test_cases = [
            ("outputs/tscv_results.csv", "tscv"),
            ("results/chronological_split.csv", "chrono"),
            ("outputs/cv_results.csv", "tscv"),
            ("outputs/regular_results.csv", "chrono")
        ]
        
        for path, expected in test_cases:
            with self.subTest(path=path):
                result = parse_split_type_from_path(path)
                self.assertEqual(result, expected)
    
    def test_parse_fold_from_path(self):
        """Test fold parsing from file paths."""
        test_cases = [
            ("outputs/fold_1_results.csv", 1),
            ("results/fold2_results.csv", 2),
            ("outputs/3_fold_results.csv", 3),
            ("outputs/regular_results.csv", "all")
        ]
        
        for path, expected in test_cases:
            with self.subTest(path=path):
                result = parse_fold_from_path(path)
                self.assertEqual(result, expected)
    
    def test_parse_model_family(self):
        """Test model family parsing."""
        test_cases = [
            ("sGARCH", "GARCH"),
            ("eGARCH", "GARCH"),
            ("NF_sGARCH", "NF-GARCH"),
            ("NF_eGARCH", "NF-GARCH"),
            ("Flow_GARCH", "NF-GARCH"),
            ("nf_garch", "NF-GARCH")
        ]
        
        for model, expected in test_cases:
            with self.subTest(model=model):
                result = parse_model_family(model)
                self.assertEqual(result, expected)
    
    def test_parse_asset_type(self):
        """Test asset type parsing."""
        test_cases = [
            ("AMZN", "Equity"),
            ("EURUSD", "FX"),
            ("GBPUSD", "FX"),
            ("NVDA", "Equity"),
            ("USDZAR", "FX")
        ]
        
        for asset, expected in test_cases:
            with self.subTest(asset=asset):
                result = parse_asset_type(asset)
                self.assertEqual(result, expected)
    
    def test_get_metric_polarity(self):
        """Test metric polarity determination."""
        test_cases = [
            ("MSE", "lower"),
            ("MAE", "lower"),
            ("AIC", "lower"),
            ("LogLikelihood", "higher"),
            ("Win_Rate", "higher"),
            ("Accuracy", "higher"),
            ("Unknown_Metric", "lower")
        ]
        
        for metric, expected in test_cases:
            with self.subTest(metric=metric):
                result = get_metric_polarity(metric)
                self.assertEqual(result, expected)
    
    def test_normalize_metric_name(self):
        """Test metric name normalization."""
        test_cases = [
            ("mse", "MSE"),
            ("loglik", "LogLikelihood"),
            ("log_likelihood", "LogLikelihood"),
            ("aic", "AIC"),
            ("win_rate", "Win_Rate"),
            ("unknown_metric", "unknown_metric")
        ]
        
        for metric, expected in test_cases:
            with self.subTest(metric=metric):
                result = normalize_metric_name(metric)
                self.assertEqual(result, expected)


class TestDataProcessing(unittest.TestCase):
    """Test data processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_csv(self, filename: str, data: dict) -> Path:
        """Create a test CSV file."""
        file_path = self.temp_path / filename
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return file_path
    
    def create_test_json(self, filename: str, data: dict) -> Path:
        """Create a test JSON file."""
        file_path = self.temp_path / filename
        with open(file_path, 'w') as f:
            json.dump(data, f)
        return file_path
    
    def test_csv_processing(self):
        """Test CSV file processing."""
        # Create test CSV
        test_data = {
            'Asset': ['AMZN', 'NVDA'],
            'Model': ['sGARCH', 'eGARCH'],
            'MSE': [0.001, 0.002],
            'AIC': [-100, -150]
        }
        
        csv_file = self.create_test_csv('test_results.csv', test_data)
        
        # Test that the file was created correctly
        self.assertTrue(csv_file.exists())
        
        # Test reading the CSV
        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 2)
        self.assertIn('Asset', df.columns)
        self.assertIn('Model', df.columns)
    
    def test_json_processing(self):
        """Test JSON file processing."""
        # Create test JSON
        test_data = {
            'results': [
                {'asset': 'AMZN', 'model': 'sGARCH', 'mse': 0.001},
                {'asset': 'NVDA', 'model': 'eGARCH', 'mse': 0.002}
            ]
        }
        
        json_file = self.create_test_json('test_results.json', test_data)
        
        # Test that the file was created correctly
        self.assertTrue(json_file.exists())
        
        # Test reading the JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)


class TestResultsCollector(unittest.TestCase):
    """Test the ResultsCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test directory structure
        (self.temp_path / "outputs" / "model_eval" / "tables").mkdir(parents=True)
        (self.temp_path / "outputs" / "var_backtest" / "tables").mkdir(parents=True)
        (self.temp_path / "artifacts").mkdir()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_data_files(self):
        """Create test data files."""
        # Model ranking data
        model_ranking = {
            'Model': ['sGARCH', 'eGARCH', 'gjrGARCH'],
            'Avg_MSE': [0.001, 0.0008, 0.0012],
            'Avg_MAE': [0.01, 0.008, 0.012]
        }
        
        ranking_file = self.temp_path / "outputs" / "model_eval" / "tables" / "model_ranking.csv"
        pd.DataFrame(model_ranking).to_csv(ranking_file, index=False)
        
        # VaR backtest data
        var_backtest = {
            'Asset': ['AMZN', 'NVDA'],
            'Model': ['sGARCH_norm', 'eGARCH'],
            'Violation_Rate': [0.05, 0.04],
            'Kupiec_PValue': [0.5, 0.6]
        }
        
        var_file = self.temp_path / "outputs" / "var_backtest" / "tables" / "var_backtest_summary.csv"
        pd.DataFrame(var_backtest).to_csv(var_file, index=False)
    
    def test_file_scanning(self):
        """Test file scanning functionality."""
        # Create test files
        self.create_test_data_files()
        
        # Import and test the collector
        from collect_results import ResultsCollector
        
        collector = ResultsCollector(str(self.temp_path))
        result_files = collector.scan_result_files()
        
        # Should find our test files
        self.assertGreater(len(result_files), 0)
        
        # Check that our test files are included
        file_paths = [str(f) for f in result_files]
        self.assertTrue(any('model_ranking.csv' in path for path in file_paths))
        self.assertTrue(any('var_backtest_summary.csv' in path for path in file_paths))
    
    def test_file_processing(self):
        """Test file processing functionality."""
        # Create test files
        self.create_test_data_files()
        
        # Import and test the collector
        from collect_results import ResultsCollector
        
        collector = ResultsCollector(str(self.temp_path))
        
        # Process a single file
        ranking_file = self.temp_path / "outputs" / "model_eval" / "tables" / "model_ranking.csv"
        records = collector.process_file(ranking_file)
        
        # Should extract records
        self.assertGreater(len(records), 0)
        
        # Check record structure
        if records:
            record = records[0]
            self.assertIn('asset', record)
            self.assertIn('model', record)
            self.assertIn('metric', record)
            self.assertIn('value', record)


if __name__ == '__main__':
    unittest.main()
