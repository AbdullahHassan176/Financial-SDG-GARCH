#!/usr/bin/env python3
"""
Create a complete research dashboard that reads both CSV and Excel files to include NF-GARCH data.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class CompleteNFGARCHDashboard:
    """Create a complete research dashboard with both standard GARCH and NF-GARCH data."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Load all available data from both CSV and Excel files
        self.load_all_data()
        
    def load_all_data(self):
        """Load data from both CSV and Excel files."""
        print("Loading data from CSV and Excel files...")
        
        # Load CSV data (standard GARCH)
        self.acc_data = self.load_csv("outputs/model_eval/tables/forecast_accuracy_summary.csv")
        self.var_data = self.load_csv("outputs/var_backtest/tables/var_backtest_summary.csv")
        self.stylized_data = self.load_csv("outputs/model_eval/tables/stylized_facts_summary.csv")
        self.stress_data = self.load_csv("outputs/stress_tests/tables/stress_test_summary.csv")
        
        # Load Excel data (NF-GARCH results)
        self.nf_garch_data = self.load_excel_data()
        
        print(f"Loaded CSV data: {len(self.acc_data) if self.acc_data is not None else 0} records")
        print(f"Loaded NF-GARCH data: {len(self.nf_garch_data) if self.nf_garch_data is not None else 0} records")
    
    def load_csv(self, path):
        """Load CSV file if it exists."""
        full_path = self.base_dir / path
        if full_path.exists():
            return pd.read_csv(full_path)
        return None
    
    def load_excel_data(self):
        """Load NF-GARCH data from Excel files."""
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
                try:
                    # Try to read different sheets
                    excel_data = pd.read_excel(full_path, sheet_name=None)
                    
                    for sheet_name, sheet_data in excel_data.items():
                        if not sheet_data.empty:
                            # Add source information
                            sheet_data['Source_File'] = excel_file
                            sheet_data['Sheet_Name'] = sheet_name
                            all_nf_data.append(sheet_data)
                            print(f"Loaded {len(sheet_data)} records from {excel_file} - {sheet_name}")
                            
                except Exception as e:
                    print(f"Error loading {excel_file}: {e}")
        
        if all_nf_data:
            return pd.concat(all_nf_data, ignore_index=True)
        return None
    
    def categorize_models(self, models):
        """Categorize models into Standard GARCH vs NF-GARCH."""
        standard_garch = []
        nf_garch = []
        
        for model in models:
            if any(keyword in str(model).upper() for keyword in ['NF', 'NF--', 'NFGARCH', 'NF_GARCH']):
                nf_garch.append(model)
            else:
                standard_garch.append(model)
        
        return standard_garch, nf_garch
    
    def create_dashboard_html(self):
        """Create the complete dashboard HTML."""
        
        # Process all data
        quantitative_metrics = {}
        distributional_metrics = {}
        stylized_facts = {}
        stress_testing = {}
        model_comparison = {}
        nf_garch_analysis = {}
        
        # Process standard GARCH data
        if self.acc_data is not None:
            model_mse = self.acc_data.groupby('Model')['MSE'].mean().sort_values()
            model_mae = self.acc_data.groupby('Model')['MAE'].mean().sort_values()
            rmse_values = [np.sqrt(mse) for mse in model_mse.values]
            
            quantitative_metrics = {
                'models': list(model_mse.index),
                'mse_values': [float(x) for x in model_mse.values],
                'mae_values': [float(x) for x in model_mae.values],
                'rmse_values': [float(x) for x in rmse_values],
                'best_model_mse': model_mse.idxmin(),
                'best_model_mae': model_mae.idxmin(),
                'best_model_rmse': list(model_mse.index)[np.argmin(rmse_values)],
                'improvement_ratio': float(model_mse.max() / model_mse.min())
            }
        
        # Process NF-GARCH data
        if self.nf_garch_data is not None:
            # Extract NF-GARCH specific metrics
            nf_models = []
            nf_mse_values = []
            nf_mae_values = []
            nf_aic_values = []
            nf_bic_values = []
            
            # Look for performance metrics in the NF-GARCH data
            for _, row in self.nf_garch_data.iterrows():
                if 'Model' in row and any(keyword in str(row['Model']).upper() for keyword in ['NF', 'NF--']):
                    nf_models.append(row['Model'])
                    
                    # Extract metrics if available
                    if 'MSE' in row and pd.notna(row['MSE']):
                        nf_mse_values.append(float(row['MSE']))
                    if 'MAE' in row and pd.notna(row['MAE']):
                        nf_mae_values.append(float(row['MAE']))
                    if 'AIC' in row and pd.notna(row['AIC']):
                        nf_aic_values.append(float(row['AIC']))
                    if 'BIC' in row and pd.notna(row['BIC']):
                        nf_bic_values.append(float(row['BIC']))
            
            nf_garch_analysis = {
                'models': nf_models,
                'mse_values': nf_mse_values,
                'mae_values': nf_mae_values,
                'aic_values': nf_aic_values,
                'bic_values': nf_bic_values,
                'total_records': len(self.nf_garch_data)
            }
        
        # Combine standard and NF-GARCH data for comparison
        all_models = []
        all_mse = []
        all_mae = []
        all_rmse = []
        model_types = []
        
        # Add standard GARCH models
        if quantitative_metrics.get('models'):
            all_models.extend(quantitative_metrics['models'])
            all_mse.extend(quantitative_metrics['mse_values'])
            all_mae.extend(quantitative_metrics['mae_values'])
            all_rmse.extend(quantitative_metrics['rmse_values'])
            model_types.extend(['Standard GARCH'] * len(quantitative_metrics['models']))
        
        # Add NF-GARCH models
        if nf_garch_analysis.get('models'):
            all_models.extend(nf_garch_analysis['models'])
            if nf_garch_analysis.get('mse_values'):
                all_mse.extend(nf_garch_analysis['mse_values'])
            if nf_garch_analysis.get('mae_values'):
                all_mae.extend(nf_garch_analysis['mae_values'])
            if nf_garch_analysis.get('mse_values'):
                all_rmse.extend([np.sqrt(mse) for mse in nf_garch_analysis['mse_values']])
            model_types.extend(['NF-GARCH'] * len(nf_garch_analysis['models']))
        
        # Create combined analysis
        combined_analysis = {
            'all_models': all_models,
            'all_mse': all_mse,
            'all_mae': all_mae,
            'all_rmse': all_rmse,
            'model_types': model_types,
            'standard_count': len([t for t in model_types if t == 'Standard GARCH']),
            'nf_count': len([t for t in model_types if t == 'NF-GARCH'])
        }
        
        # Process other metrics
        if self.var_data is not None:
            model_violations = self.var_data.groupby('Model')['Violation_Rate'].mean().sort_values()
            significant_tests = len(self.var_data[self.var_data['Kupiec_PValue'] < 0.05])
            total_tests = len(self.var_data)
            significance_rate = significant_tests / total_tests * 100
            
            distributional_metrics = {
                'models': list(model_violations.index),
                'violation_rates': [float(x) for x in model_violations.values],
                'best_risk_model': model_violations.idxmin(),
                'best_violation_rate': float(model_violations.min()),
                'significant_tests': significant_tests,
                'total_tests': total_tests,
                'significance_rate': significance_rate
            }
        
        if self.stylized_data is not None:
            stylized_facts = {
                'assets': list(self.stylized_data['Asset']),
                'kurtosis': [float(x) for x in self.stylized_data['Kurtosis']],
                'excess_kurtosis': [float(x) for x in self.stylized_data['Excess_Kurtosis']],
                'tail_index': [float(x) for x in self.stylized_data['Tail_Index']],
                'acf1': [float(x) for x in self.stylized_data['ACF1']],
                'leverage_coeff': [float(x) for x in self.stylized_data['Leverage_Coefficient']],
                'hurst_exponent': [float(x) for x in self.stylized_data['Hurst_Exponent']],
                'has_clustering': [bool(x) for x in self.stylized_data['Has_Clustering']],
                'has_leverage': [bool(x) for x in self.stylized_data['Has_Leverage']],
                'has_autocorr': [bool(x) for x in self.stylized_data['Has_Autocorr']],
                'is_heavy_tailed': [bool(x) for x in self.stylized_data['Is_Heavy_Tailed']]
            }
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete NF-GARCH vs Standard GARCH Research Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .chart-container {{
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .comparison-box {{
            background: #e8f4fd;
            border: 2px solid #2196F3;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .model-type {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 8px;
        }}
        .standard-garch {{
            background: #ff9800;
            color: #000;
        }}
        .nf-garch {{
            background: #4caf50;
            color: white;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 0.9em;
        }}
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .data-table th {{
            background-color: #f2f2f2;
        }}
        .tabs {{
            display: flex;
            border-bottom: 2px solid #ddd;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-right: 10px;
        }}
        .tab.active {{
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: bold;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .nf-highlight {{
            background: #e8f5e8;
            border: 2px solid #4caf50;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Complete NF-GARCH vs Standard GARCH Research Dashboard</h1>
            <p>Comprehensive Analysis: Standard GARCH + NF-GARCH Models with NF Residuals</p>
            <p><small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        
        <div class="content">
            <!-- Navigation Tabs -->
            <div class="tabs">
                <div class="tab active" onclick="showTab('overview')">Overview</div>
                <div class="tab" onclick="showTab('combined')">Combined Analysis</div>
                <div class="tab" onclick="showTab('nf-garch')">NF-GARCH Analysis</div>
                <div class="tab" onclick="showTab('standard')">Standard GARCH</div>
                <div class="tab" onclick="showTab('comparison')">Direct Comparison</div>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview" class="tab-content active">
                <div class="section">
                    <h2>🔍 Executive Summary</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{combined_analysis.get('standard_count', 0)}</div>
                            <div class="metric-label">Standard GARCH Models</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{combined_analysis.get('nf_count', 0)}</div>
                            <div class="metric-label">NF-GARCH Models</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{nf_garch_analysis.get('total_records', 0)}</div>
                            <div class="metric-label">NF-GARCH Records</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{len(stylized_facts.get('assets', []))}</div>
                            <div class="metric-label">Assets Analyzed</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{distributional_metrics.get('significance_rate', 0):.1f}%</div>
                            <div class="metric-label">Statistical Significance</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">Complete</div>
                            <div class="metric-label">Data Coverage</div>
                        </div>
                    </div>
                    
                    <div class="nf-highlight">
                        <h3>🎯 NF-GARCH Data Status</h3>
                        <p><strong>NF-GARCH Models Found:</strong> {nf_garch_analysis.get('total_records', 0)} records</p>
                        <p><strong>Data Sources:</strong> Excel files with NF residual injection results</p>
                        <p><strong>Model Types:</strong> NF--sGARCH, NF--eGARCH, NF--gjrGARCH, NF--TGARCH</p>
                        <p><strong>Analysis:</strong> Complete comparison between standard GARCH and NF-GARCH approaches</p>
                    </div>
                </div>
            </div>
            
            <!-- Combined Analysis Tab -->
            <div id="combined" class="tab-content">
                <div class="section">
                    <h2>📊 Combined Model Performance Analysis</h2>
                    <div class="chart-container" id="combined-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Type</th><th>MSE</th><th>MAE</th><th>RMSE</th><th>Rank</th></tr>
                        {self._create_combined_table(combined_analysis)}
                    </table>
                </div>
            </div>
            
            <!-- NF-GARCH Analysis Tab -->
            <div id="nf-garch" class="tab-content">
                <div class="section">
                    <h2>🧠 NF-GARCH Specific Analysis</h2>
                    <div class="nf-highlight">
                        <h3>NF Residual Injection Results</h3>
                        <p>Analysis of GARCH models enhanced with Neural Flow (NF) generated residuals</p>
                    </div>
                    <div class="chart-container" id="nf-garch-chart"></div>
                    <table class="data-table">
                        <tr><th>NF-GARCH Model</th><th>MSE</th><th>MAE</th><th>AIC</th><th>BIC</th><th>Performance</th></tr>
                        {self._create_nf_garch_table(nf_garch_analysis)}
                    </table>
                </div>
            </div>
            
            <!-- Standard GARCH Tab -->
            <div id="standard" class="tab-content">
                <div class="section">
                    <h2>📈 Standard GARCH Analysis</h2>
                    <div class="chart-container" id="standard-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>MSE</th><th>MAE</th><th>RMSE</th><th>Rank</th></tr>
                        {self._create_standard_table(quantitative_metrics)}
                    </table>
                </div>
            </div>
            
            <!-- Direct Comparison Tab -->
            <div id="comparison" class="tab-content">
                <div class="section">
                    <h2>⚖️ Direct Standard GARCH vs NF-GARCH Comparison</h2>
                    <div class="comparison-box">
                        <h3>Performance Comparison</h3>
                        <p><strong>Standard GARCH Models:</strong> {combined_analysis.get('standard_count', 0)} models analyzed</p>
                        <p><strong>NF-GARCH Models:</strong> {combined_analysis.get('nf_count', 0)} models analyzed</p>
                        <p><strong>Data Sources:</strong> CSV files (Standard) + Excel files (NF-GARCH)</p>
                    </div>
                    <div class="chart-container" id="comparison-chart"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab functionality
        function showTab(tabName) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }}
        
        // Combined Analysis Chart
        var combinedData = {json.dumps(combined_analysis)};
        if (combinedData.all_models && combinedData.all_models.length > 0) {{
            var combinedTrace = {{
                x: combinedData.all_models,
                y: combinedData.all_rmse,
                type: 'bar',
                marker: {{
                    color: combinedData.model_types.map(type => 
                        type === 'NF-GARCH' ? '#4caf50' : '#ff9800'
                    )
                }},
                text: combinedData.all_rmse.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var combinedLayout = {{
                title: 'Combined Model Performance - RMSE (Green=NF-GARCH, Orange=Standard GARCH)',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Root Mean Squared Error' }},
                height: 400
            }};
            
            Plotly.newPlot('combined-chart', [combinedTrace], combinedLayout);
        }} else {{
            document.getElementById('combined-chart').innerHTML = '<p>No combined data available</p>';
        }}
        
        // NF-GARCH Analysis Chart
        var nfGarchData = {json.dumps(nf_garch_analysis)};
        if (nfGarchData.models && nfGarchData.models.length > 0) {{
            var nfGarchTrace = {{
                x: nfGarchData.models,
                y: nfGarchData.mse_values,
                type: 'bar',
                marker: {{ color: '#4caf50' }},
                text: nfGarchData.mse_values.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var nfGarchLayout = {{
                title: 'NF-GARCH Model Performance (MSE)',
                xaxis: {{ title: 'NF-GARCH Model' }},
                yaxis: {{ title: 'Mean Squared Error' }},
                height: 400
            }};
            
            Plotly.newPlot('nf-garch-chart', [nfGarchTrace], nfGarchLayout);
        }} else {{
            document.getElementById('nf-garch-chart').innerHTML = '<p>No NF-GARCH data available</p>';
        }}
        
        // Standard GARCH Chart
        var standardData = {json.dumps(quantitative_metrics)};
        if (standardData.models && standardData.models.length > 0) {{
            var standardTrace = {{
                x: standardData.models,
                y: standardData.rmse_values,
                type: 'bar',
                marker: {{ color: '#ff9800' }},
                text: standardData.rmse_values.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var standardLayout = {{
                title: 'Standard GARCH Model Performance (RMSE)',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Root Mean Squared Error' }},
                height: 400
            }};
            
            Plotly.newPlot('standard-chart', [standardTrace], standardLayout);
        }} else {{
            document.getElementById('standard-chart').innerHTML = '<p>No standard GARCH data available</p>';
        }}
        
        // Comparison Chart
        var comparisonData = {json.dumps(combined_analysis)};
        if (comparisonData.standard_count > 0 && comparisonData.nf_count > 0) {{
            var comparisonTrace = {{
                x: ['Standard GARCH', 'NF-GARCH'],
                y: [comparisonData.standard_count, comparisonData.nf_count],
                type: 'bar',
                marker: {{
                    color: ['#ff9800', '#4caf50']
                }},
                text: [comparisonData.standard_count, comparisonData.nf_count],
                textposition: 'auto'
            }};
            
            var comparisonLayout = {{
                title: 'Model Count Comparison',
                xaxis: {{ title: 'Model Type' }},
                yaxis: {{ title: 'Number of Models' }},
                height: 400
            }};
            
            Plotly.newPlot('comparison-chart', [comparisonTrace], comparisonLayout);
        }} else {{
            document.getElementById('comparison-chart').innerHTML = '<p>No comparison data available</p>';
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
    def _create_combined_table(self, combined_analysis):
        """Create combined analysis table."""
        if not combined_analysis.get('all_models'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for i, (model, mse, mae, rmse, model_type) in enumerate(zip(
            combined_analysis['all_models'],
            combined_analysis['all_mse'],
            combined_analysis['all_mae'],
            combined_analysis['all_rmse'],
            combined_analysis['model_types']
        )):
            rank = i + 1
            type_class = 'nf-garch' if model_type == 'NF-GARCH' else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{mse:.6f}</td><td>{mae:.6f}</td><td>{rmse:.6f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_nf_garch_table(self, nf_garch_analysis):
        """Create NF-GARCH analysis table."""
        if not nf_garch_analysis.get('models'):
            return "<tr><td colspan='6'>No NF-GARCH data available</td></tr>"
        
        rows = []
        for i, model in enumerate(nf_garch_analysis['models']):
            rank = i + 1
            mse = nf_garch_analysis['mse_values'][i] if i < len(nf_garch_analysis['mse_values']) else 'N/A'
            mae = nf_garch_analysis['mae_values'][i] if i < len(nf_garch_analysis['mae_values']) else 'N/A'
            aic = nf_garch_analysis['aic_values'][i] if i < len(nf_garch_analysis['aic_values']) else 'N/A'
            bic = nf_garch_analysis['bic_values'][i] if i < len(nf_garch_analysis['bic_values']) else 'N/A'
            performance = 'Excellent' if isinstance(mse, (int, float)) and mse < 0.001 else 'Good'
            rows.append(f"<tr><td>{model}</td><td>{mse}</td><td>{mae}</td><td>{aic}</td><td>{bic}</td><td>{performance}</td></tr>")
        return ''.join(rows)
    
    def _create_standard_table(self, quantitative_metrics):
        """Create standard GARCH table."""
        if not quantitative_metrics.get('models'):
            return "<tr><td colspan='5'>No data available</td></tr>"
        
        rows = []
        for i, (model, mse, mae, rmse) in enumerate(zip(
            quantitative_metrics['models'],
            quantitative_metrics['mse_values'],
            quantitative_metrics['mae_values'],
            quantitative_metrics['rmse_values']
        )):
            rank = i + 1
            rows.append(f"<tr><td>{model}</td><td>{mse:.6f}</td><td>{mae:.6f}</td><td>{rmse:.6f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def run(self):
        """Generate the complete dashboard."""
        print("Creating complete NF-GARCH vs Standard GARCH dashboard...")
        
        html_content = self.create_dashboard_html()
        
        # Save HTML file
        html_path = self.docs_dir / "research_dashboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Complete dashboard created: {html_path}")
        return html_path

def main():
    """Main entry point."""
    dashboard = CompleteNFGARCHDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
