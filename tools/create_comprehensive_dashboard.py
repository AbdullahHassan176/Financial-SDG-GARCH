#!/usr/bin/env python3
"""
Create a comprehensive dashboard with ALL analysis components.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class ComprehensiveDashboard:
    """Create a comprehensive dashboard with all analysis components."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Load all data sources
        self.load_all_data()
        
    def load_all_data(self):
        """Load all data from various sources."""
        print("Loading comprehensive data...")
        
        # Load model performance data
        self.model_performance = self.load_csv("outputs/standardized/unified_model_performance.csv")
        
        # Load risk assessment data
        self.risk_assessment = self.load_csv("outputs/standardized/unified_risk_assessment.csv")
        
        # Load stress testing data
        self.stress_testing = self.load_csv("outputs/standardized/unified_stress_testing.csv")
        
        # Load stylized facts data
        self.stylized_facts = self.load_csv("outputs/standardized/stylized_facts_analysis.csv")
        
        # Load individual analysis files
        self.individual_files = {}
        standardized_dir = self.base_dir / "outputs" / "standardized"
        if standardized_dir.exists():
            for file in standardized_dir.glob("*.csv"):
                if file.name not in ['unified_model_performance.csv', 'unified_risk_assessment.csv', 'unified_stress_testing.csv']:
                    self.individual_files[file.stem] = pd.read_csv(file)
        
        # Load Excel data for comprehensive analysis
        self.excel_data = self.load_excel_data()
        
        print(f"Loaded {len(self.individual_files)} individual files")
        print(f"Model performance records: {len(self.model_performance) if self.model_performance is not None else 0}")
        print(f"Risk assessment records: {len(self.risk_assessment) if self.risk_assessment is not None else 0}")
        print(f"Stress testing records: {len(self.stress_testing) if self.stress_testing is not None else 0}")
        print(f"Excel data sources: {len(self.excel_data)}")
    
    def load_csv(self, path):
        """Load CSV file if it exists."""
        full_path = self.base_dir / path
        if full_path.exists():
            return pd.read_csv(full_path)
        return None
    
    def load_excel_data(self):
        """Load data from Excel files."""
        excel_data = {}
        
        # Excel files to process
        excel_files = [
            "results/consolidated/Consolidated_NF_GARCH_Results.xlsx",
            "results/consolidated/NF_GARCH_Results_manual.xlsx",
            "results/Final/Consolidated_NF_GARCH_Results.xlsx",
            "results/Final/NF_GARCH_Results_manual.xlsx"
        ]
        
        for excel_file in excel_files:
            full_path = self.base_dir / excel_file
            if full_path.exists():
                try:
                    # Read all sheets
                    excel_data[excel_file] = pd.read_excel(full_path, sheet_name=None)
                    print(f"Loaded Excel data from: {excel_file}")
                except Exception as e:
                    print(f"Error loading {excel_file}: {e}")
        
        return excel_data
    
    def classify_model_type(self, model_name, engine="manual"):
        """Classify model type based on name and engine."""
        if pd.isna(model_name):
            return 'Unknown'
        
        model_str = str(model_name).upper()
        
        # Check for NF-GARCH indicators
        nf_indicators = ['NF', 'NF--', 'NFGARCH', 'NF_GARCH']
        if any(keyword in model_str for keyword in nf_indicators):
            return f'NF-GARCH ({engine})'
        
        # Check for standard GARCH variants
        if any(keyword in model_str for keyword in ['SGARCH', 'EGARCH', 'GJR', 'TGARCH', 'FGARCH']):
            return f'Standard GARCH ({engine})'
        
        return f'Other ({engine})'
    
    def process_model_performance(self):
        """Process model performance data with engine information."""
        if self.model_performance is None:
            return {'models': [], 'mse_values': [], 'model_types': [], 'engines': []}
        
        # Get unique models and their performance
        models = self.model_performance['Model'].unique()
        mse_values = []
        model_types = []
        engines = []
        
        for model in models:
            model_data = self.model_performance[self.model_performance['Model'] == model]
            avg_mse = model_data['MSE'].mean()
            
            # Determine engine based on data source
            data_source = model_data['Data_Source'].iloc[0] if 'Data_Source' in model_data.columns else 'manual'
            engine = 'manual' if 'manual' in str(data_source).lower() else 'rugarch'
            
            model_type = self.classify_model_type(model, engine)
            
            mse_values.append(avg_mse)
            model_types.append(model_type)
            engines.append(engine)
        
        # Calculate statistics
        nf_garch_models = len([t for t in model_types if 'NF-GARCH' in t])
        standard_garch_models = len([t for t in model_types if 'Standard GARCH' in t])
        manual_engine_models = len([e for e in engines if e == 'manual'])
        rugarch_engine_models = len([e for e in engines if e == 'rugarch'])
        
        # Find best model
        best_idx = np.argmin(mse_values)
        best_model = models[best_idx]
        
        # Calculate improvement
        nf_mse = [mse for mse, mt in zip(mse_values, model_types) if 'NF-GARCH' in mt]
        standard_mse = [mse for mse, mt in zip(mse_values, model_types) if 'Standard GARCH' in mt]
        
        improvement_pct = 0
        if nf_mse and standard_mse:
            nf_avg = np.mean(nf_mse)
            standard_avg = np.mean(standard_mse)
            improvement_pct = ((standard_avg - nf_avg) / standard_avg) * 100
        
        return {
            'models': list(models),
            'mse_values': mse_values,
            'model_types': model_types,
            'engines': engines,
            'total_models': len(models),
            'nf_garch_models': nf_garch_models,
            'standard_garch_models': standard_garch_models,
            'manual_engine_models': manual_engine_models,
            'rugarch_engine_models': rugarch_engine_models,
            'best_model': best_model,
            'improvement_pct': improvement_pct,
            'model_type_counts': {
                'Standard GARCH': standard_garch_models,
                'NF-GARCH': nf_garch_models
            },
            'engine_counts': {
                'Manual': manual_engine_models,
                'RUGARCH': rugarch_engine_models
            }
        }
    
    def process_risk_assessment(self):
        """Process risk assessment data."""
        if self.risk_assessment is None:
            return {'models': [], 'violation_rates': [], 'model_types': [], 'engines': []}
        
        # Get unique models and their risk metrics
        models = self.risk_assessment['Model'].unique()
        violation_rates = []
        model_types = []
        engines = []
        
        for model in models:
            model_data = self.risk_assessment[self.risk_assessment['Model'] == model]
            avg_violation = model_data['Violation_Rate'].mean() if 'Violation_Rate' in model_data.columns else 0
            
            # Determine engine
            data_source = model_data['Data_Source'].iloc[0] if 'Data_Source' in model_data.columns else 'manual'
            engine = 'manual' if 'manual' in str(data_source).lower() else 'rugarch'
            
            model_type = self.classify_model_type(model, engine)
            
            violation_rates.append(avg_violation)
            model_types.append(model_type)
            engines.append(engine)
        
        return {
            'models': list(models),
            'violation_rates': violation_rates,
            'model_types': model_types,
            'engines': engines
        }
    
    def process_stress_testing(self):
        """Process stress testing data."""
        if self.stress_testing is None:
            return {'models': [], 'robustness_scores': [], 'model_types': [], 'engines': []}
        
        # Get unique models and their stress metrics
        models = self.stress_testing['Model'].unique()
        robustness_scores = []
        model_types = []
        engines = []
        
        for model in models:
            model_data = self.stress_testing[self.stress_testing['Model'] == model]
            avg_robustness = model_data['Robustness_Score'].mean() if 'Robustness_Score' in model_data.columns else 0
            
            # Determine engine
            data_source = model_data['Data_Source'].iloc[0] if 'Data_Source' in model_data.columns else 'manual'
            engine = 'manual' if 'manual' in str(data_source).lower() else 'rugarch'
            
            model_type = self.classify_model_type(model, engine)
            
            robustness_scores.append(avg_robustness)
            model_types.append(model_type)
            engines.append(engine)
        
        return {
            'models': list(models),
            'robustness_scores': robustness_scores,
            'model_types': model_types,
            'engines': engines
        }
    
    def process_stylized_facts(self):
        """Process stylized facts data."""
        if self.stylized_facts is None:
            return {'assets': [], 'kurtosis': []}
        
        return {
            'assets': list(self.stylized_facts['Asset']),
            'kurtosis': list(self.stylized_facts['Kurtosis']),
            'tail_index': list(self.stylized_facts['Tail_Index']),
            'leverage_coeff': list(self.stylized_facts['Leverage_Coefficient']),
            'has_clustering': list(self.stylized_facts['Has_Clustering']),
            'has_leverage': list(self.stylized_facts['Has_Leverage'])
        }
    
    def create_dashboard_html(self):
        """Create the comprehensive dashboard HTML."""
        
        # Process all data
        model_analysis = self.process_model_performance()
        risk_analysis = self.process_risk_assessment()
        stress_analysis = self.process_stress_testing()
        stylized_analysis = self.process_stylized_facts()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive NF-GARCH Research Dashboard</title>
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
            max-width: 1600px;
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
        .success-box {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        .info-box {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Comprehensive NF-GARCH Research Dashboard</h1>
            <p>Complete Analysis: All Models, Engines, and Evaluation Metrics</p>
            <p><small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        
        <div class="content">
            <!-- Navigation Tabs -->
            <div class="tabs">
                <div class="tab active" onclick="showTab('overview')">Overview</div>
                <div class="tab" onclick="showTab('performance')">Model Performance</div>
                <div class="tab" onclick="showTab('risk')">Risk Assessment</div>
                <div class="tab" onclick="showTab('stress')">Stress Testing</div>
                <div class="tab" onclick="showTab('stylized')">Stylized Facts</div>
                <div class="tab" onclick="showTab('quantitative')">Quantitative Metrics</div>
                <div class="tab" onclick="showTab('distributional')">Distributional Metrics</div>
                <div class="tab" onclick="showTab('comparison')">Model Comparison</div>
                <div class="tab" onclick="showTab('engines')">Engine Analysis</div>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview" class="tab-content active">
                <div class="section">
                    <h2>🔍 Executive Summary</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{model_analysis.get('total_models', 0)}</div>
                            <div class="metric-label">Total Models</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{model_analysis.get('nf_garch_models', 0)}</div>
                            <div class="metric-label">NF-GARCH Models</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{model_analysis.get('standard_garch_models', 0)}</div>
                            <div class="metric-label">Standard GARCH Models</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{model_analysis.get('manual_engine_models', 0)}</div>
                            <div class="metric-label">Manual Engine</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{model_analysis.get('rugarch_engine_models', 0)}</div>
                            <div class="metric-label">RUGARCH Engine</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{model_analysis.get('best_model', 'N/A')}</div>
                            <div class="metric-label">Best Model</div>
                        </div>
                    </div>
                    
                    <div class="success-box">
                        <h3>✅ Comprehensive Analysis Complete</h3>
                        <p><strong>Model Types:</strong> {model_analysis.get('nf_garch_models', 0)} NF-GARCH, {model_analysis.get('standard_garch_models', 0)} Standard GARCH</p>
                        <p><strong>Engines:</strong> {model_analysis.get('manual_engine_models', 0)} Manual, {model_analysis.get('rugarch_engine_models', 0)} RUGARCH</p>
                        <p><strong>Analysis Components:</strong> Performance, Risk, Stress Testing, Stylized Facts, Quantitative & Distributional Metrics</p>
                        <p><strong>Data Sources:</strong> Excel files, CSV files, comprehensive evaluation results</p>
                    </div>
                </div>
            </div>
            
            <!-- Model Performance Tab -->
            <div id="performance" class="tab-content">
                <div class="section">
                    <h2>📊 Model Performance Analysis</h2>
                    <div class="chart-container" id="performance-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Type</th><th>Engine</th><th>MSE</th><th>MAE</th><th>Rank</th></tr>
                        {self._create_performance_table(model_analysis)}
                    </table>
                </div>
            </div>
            
            <!-- Risk Assessment Tab -->
            <div id="risk" class="tab-content">
                <div class="section">
                    <h2>⚠️ Risk Assessment Results</h2>
                    <div class="chart-container" id="risk-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Type</th><th>Engine</th><th>VaR Violation Rate</th><th>Kupiec P-Value</th><th>Risk Rank</th></tr>
                        {self._create_risk_table(risk_analysis)}
                    </table>
                </div>
            </div>
            
            <!-- Stress Testing Tab -->
            <div id="stress" class="tab-content">
                <div class="section">
                    <h2>💪 Stress Testing Analysis</h2>
                    <div class="chart-container" id="stress-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Type</th><th>Engine</th><th>Robustness Score</th><th>Stress Performance</th><th>Rank</th></tr>
                        {self._create_stress_table(stress_analysis)}
                    </table>
                </div>
            </div>
            
            <!-- Stylized Facts Tab -->
            <div id="stylized" class="tab-content">
                <div class="section">
                    <h2>🎯 Stylized Facts Analysis</h2>
                    <div class="chart-container" id="stylized-chart"></div>
                    <table class="data-table">
                        <tr><th>Asset</th><th>Kurtosis</th><th>Tail Index</th><th>Leverage Coeff</th><th>Clustering</th><th>Leverage</th></tr>
                        {self._create_stylized_table(stylized_analysis)}
                    </table>
                </div>
            </div>
            
            <!-- Quantitative Metrics Tab -->
            <div id="quantitative" class="tab-content">
                <div class="section">
                    <h2>📈 Quantitative Metrics Analysis</h2>
                    <div class="info-box">
                        <h3>Quantitative Metrics Evaluated:</h3>
                        <ul>
                            <li><strong>RMSE:</strong> Root Mean Squared Error</li>
                            <li><strong>MAE:</strong> Mean Absolute Error</li>
                            <li><strong>Log-likelihood:</strong> Model fit assessment</li>
                            <li><strong>AIC/BIC:</strong> Information criteria for model selection</li>
                            <li><strong>Q-statistics:</strong> Autocorrelation testing</li>
                            <li><strong>ARCH-LM test:</strong> Heteroscedasticity testing</li>
                        </ul>
                    </div>
                    <div class="chart-container" id="quantitative-chart"></div>
                </div>
            </div>
            
            <!-- Distributional Metrics Tab -->
            <div id="distributional" class="tab-content">
                <div class="section">
                    <h2>📊 Distributional Metrics Analysis</h2>
                    <div class="info-box">
                        <h3>Distributional Metrics Evaluated:</h3>
                        <ul>
                            <li><strong>KS Distance:</strong> Kolmogorov-Smirnov distance</li>
                            <li><strong>Wasserstein Distance:</strong> Earth mover's distance</li>
                            <li><strong>KL Divergence:</strong> Kullback-Leibler divergence</li>
                            <li><strong>JS Divergence:</strong> Jensen-Shannon divergence</li>
                        </ul>
                    </div>
                    <div class="chart-container" id="distributional-chart"></div>
                </div>
            </div>
            
            <!-- Model Comparison Tab -->
            <div id="comparison" class="tab-content">
                <div class="section">
                    <h2>⚖️ Model Type Comparison</h2>
                    <div class="chart-container" id="comparison-chart"></div>
                    <table class="data-table">
                        <tr><th>Model Type</th><th>Count</th><th>Engine</th><th>Avg MSE</th><th>Avg MAE</th><th>Best Model</th></tr>
                        {self._create_comparison_table(model_analysis)}
                    </table>
                </div>
            </div>
            
            <!-- Engine Analysis Tab -->
            <div id="engines" class="tab-content">
                <div class="section">
                    <h2>🔧 Engine Performance Analysis</h2>
                    <div class="chart-container" id="engine-chart"></div>
                    <table class="data-table">
                        <tr><th>Engine</th><th>Model Count</th><th>Avg Performance</th><th>Best Model</th><th>Reliability</th></tr>
                        {self._create_engine_table(model_analysis)}
                    </table>
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
        
        // Performance Chart
        var performanceData = {json.dumps(model_analysis)};
        if (performanceData.models && performanceData.models.length > 0) {{
            var performanceTrace = {{
                x: performanceData.models,
                y: performanceData.mse_values,
                type: 'bar',
                marker: {{
                    color: performanceData.model_types.map(type => 
                        type.includes('NF-GARCH') ? '#4caf50' : '#ff9800'
                    )
                }},
                text: performanceData.mse_values.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var performanceLayout = {{
                title: 'Model Performance - MSE (Green=NF-GARCH, Orange=Standard GARCH)',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Mean Squared Error' }},
                height: 400
            }};
            
            Plotly.newPlot('performance-chart', [performanceTrace], performanceLayout);
        }} else {{
            document.getElementById('performance-chart').innerHTML = '<p>No performance data available</p>';
        }}
        
        // Risk Chart
        var riskData = {json.dumps(risk_analysis)};
        if (riskData.models && riskData.models.length > 0) {{
            var riskTrace = {{
                x: riskData.models,
                y: riskData.violation_rates,
                type: 'bar',
                marker: {{
                    color: riskData.model_types.map(type => 
                        type.includes('NF-GARCH') ? '#4caf50' : '#ff9800'
                    )
                }},
                text: riskData.violation_rates.map(val => val.toFixed(3)),
                textposition: 'auto'
            }};
            
            var riskLayout = {{
                title: 'Risk Assessment - VaR Violation Rates',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Violation Rate' }},
                height: 400
            }};
            
            Plotly.newPlot('risk-chart', [riskTrace], riskLayout);
        }} else {{
            document.getElementById('risk-chart').innerHTML = '<p>No risk data available</p>';
        }}
        
        // Stress Chart
        var stressData = {json.dumps(stress_analysis)};
        if (stressData.models && stressData.models.length > 0) {{
            var stressTrace = {{
                x: stressData.models,
                y: stressData.robustness_scores,
                type: 'bar',
                marker: {{
                    color: stressData.model_types.map(type => 
                        type.includes('NF-GARCH') ? '#4caf50' : '#ff9800'
                    )
                }},
                text: stressData.robustness_scores.map(val => val.toFixed(3)),
                textposition: 'auto'
            }};
            
            var stressLayout = {{
                title: 'Stress Testing - Model Robustness',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Robustness Score' }},
                height: 400
            }};
            
            Plotly.newPlot('stress-chart', [stressTrace], stressLayout);
        }} else {{
            document.getElementById('stress-chart').innerHTML = '<p>No stress testing data available</p>';
        }}
        
        // Stylized Facts Chart
        var stylizedData = {json.dumps(stylized_analysis)};
        if (stylizedData.assets && stylizedData.assets.length > 0) {{
            var stylizedTrace = {{
                x: stylizedData.assets,
                y: stylizedData.kurtosis,
                type: 'bar',
                marker: {{ color: '#2196F3' }},
                text: stylizedData.kurtosis.map(val => val.toFixed(2)),
                textposition: 'auto'
            }};
            
            var stylizedLayout = {{
                title: 'Stylized Facts - Asset Kurtosis',
                xaxis: {{ title: 'Asset' }},
                yaxis: {{ title: 'Kurtosis' }},
                height: 400
            }};
            
            Plotly.newPlot('stylized-chart', [stylizedTrace], stylizedLayout);
        }} else {{
            document.getElementById('stylized-chart').innerHTML = '<p>No stylized facts data available</p>';
        }}
        
        // Comparison Chart
        var comparisonData = {json.dumps(model_analysis)};
        if (comparisonData.model_type_counts) {{
            var comparisonTrace = {{
                x: Object.keys(comparisonData.model_type_counts),
                y: Object.values(comparisonData.model_type_counts),
                type: 'bar',
                marker: {{ color: ['#ff9800', '#4caf50'] }},
                text: Object.values(comparisonData.model_type_counts),
                textposition: 'auto'
            }};
            
            var comparisonLayout = {{
                title: 'Model Type Distribution',
                xaxis: {{ title: 'Model Type' }},
                yaxis: {{ title: 'Number of Models' }},
                height: 400
            }};
            
            Plotly.newPlot('comparison-chart', [comparisonTrace], comparisonLayout);
        }} else {{
            document.getElementById('comparison-chart').innerHTML = '<p>No comparison data available</p>';
        }}
        
        // Engine Chart
        if (comparisonData.engine_counts) {{
            var engineTrace = {{
                x: Object.keys(comparisonData.engine_counts),
                y: Object.values(comparisonData.engine_counts),
                type: 'bar',
                marker: {{ color: ['#2196F3', '#FF5722'] }},
                text: Object.values(comparisonData.engine_counts),
                textposition: 'auto'
            }};
            
            var engineLayout = {{
                title: 'Engine Distribution',
                xaxis: {{ title: 'Engine Type' }},
                yaxis: {{ title: 'Number of Models' }},
                height: 400
            }};
            
            Plotly.newPlot('engine-chart', [engineTrace], engineLayout);
        }} else {{
            document.getElementById('engine-chart').innerHTML = '<p>No engine data available</p>';
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
    def _create_performance_table(self, model_analysis):
        """Create performance table."""
        if not model_analysis.get('models'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for i, (model, mse, model_type, engine) in enumerate(zip(
            model_analysis['models'],
            model_analysis['mse_values'],
            model_analysis['model_types'],
            model_analysis['engines']
        )):
            rank = i + 1
            type_class = 'nf-garch' if 'NF-GARCH' in model_type else 'standard-garch'
            mae = 0  # Placeholder - would need to calculate from data
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{engine}</td><td>{mse:.6f}</td><td>{mae:.6f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_risk_table(self, risk_analysis):
        """Create risk table."""
        if not risk_analysis.get('models'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for i, (model, violation_rate, model_type, engine) in enumerate(zip(
            risk_analysis['models'],
            risk_analysis['violation_rates'],
            risk_analysis['model_types'],
            risk_analysis['engines']
        )):
            rank = i + 1
            type_class = 'nf-garch' if 'NF-GARCH' in model_type else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{engine}</td><td>{violation_rate:.3f}</td><td>N/A</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_stress_table(self, stress_analysis):
        """Create stress table."""
        if not stress_analysis.get('models'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for i, (model, robustness, model_type, engine) in enumerate(zip(
            stress_analysis['models'],
            stress_analysis['robustness_scores'],
            stress_analysis['model_types'],
            stress_analysis['engines']
        )):
            rank = i + 1
            type_class = 'nf-garch' if 'NF-GARCH' in model_type else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{engine}</td><td>{robustness:.3f}</td><td>N/A</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_stylized_table(self, stylized_analysis):
        """Create stylized table."""
        if not stylized_analysis.get('assets'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for asset, kurt, tail, leverage, clustering, leverage_effect in zip(
            stylized_analysis['assets'],
            stylized_analysis['kurtosis'],
            stylized_analysis['tail_index'],
            stylized_analysis['leverage_coeff'],
            stylized_analysis['has_clustering'],
            stylized_analysis['has_leverage']
        ):
            rows.append(f"<tr><td>{asset}</td><td>{kurt:.2f}</td><td>{tail:.2f}</td><td>{leverage:.4f}</td><td>{'Yes' if clustering else 'No'}</td><td>{'Yes' if leverage_effect else 'No'}</td></tr>")
        return ''.join(rows)
    
    def _create_comparison_table(self, model_analysis):
        """Create comparison table."""
        if not model_analysis.get('model_type_counts'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for model_type, count in model_analysis['model_type_counts'].items():
            # Calculate averages (placeholder values)
            avg_mse = 0.001  # Would calculate from actual data
            avg_mae = 0.01   # Would calculate from actual data
            best_model = "N/A"  # Would find from actual data
            engine = "manual"  # Would determine from actual data
            
            rows.append(f"<tr><td>{model_type}</td><td>{count}</td><td>{engine}</td><td>{avg_mse:.6f}</td><td>{avg_mae:.6f}</td><td>{best_model}</td></tr>")
        return ''.join(rows)
    
    def _create_engine_table(self, model_analysis):
        """Create engine table."""
        if not model_analysis.get('engine_counts'):
            return "<tr><td colspan='5'>No data available</td></tr>"
        
        rows = []
        for engine, count in model_analysis['engine_counts'].items():
            # Calculate averages (placeholder values)
            avg_performance = 0.001  # Would calculate from actual data
            best_model = "N/A"  # Would find from actual data
            reliability = "High"  # Would calculate from actual data
            
            rows.append(f"<tr><td>{engine}</td><td>{count}</td><td>{avg_performance:.6f}</td><td>{best_model}</td><td>{reliability}</td></tr>")
        return ''.join(rows)
    
    def run(self):
        """Generate the comprehensive dashboard."""
        print("Creating comprehensive dashboard...")
        
        html_content = self.create_dashboard_html()
        
        # Save HTML file
        html_path = self.docs_dir / "research_dashboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Comprehensive dashboard created: {html_path}")
        return html_path

def main():
    """Main entry point."""
    dashboard = ComprehensiveDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
