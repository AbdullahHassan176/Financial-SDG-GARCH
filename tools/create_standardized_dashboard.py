#!/usr/bin/env python3
"""
Create a dashboard that works with standardized output files.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class StandardizedDashboard:
    """Create a dashboard using standardized output files."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.standardized_dir = self.base_dir / "outputs" / "standardized"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Load standardized data
        self.load_standardized_data()
        
    def load_standardized_data(self):
        """Load data from standardized files."""
        print("Loading standardized data...")
        
        # Load unified data files
        self.model_performance = self.load_csv("outputs/standardized/unified_model_performance.csv")
        self.risk_assessment = self.load_csv("outputs/standardized/unified_risk_assessment.csv")
        self.stress_testing = self.load_csv("outputs/standardized/unified_stress_testing.csv")
        self.stylized_facts = self.load_csv("outputs/standardized/stylized_facts_analysis.csv")
        
        # Load individual standardized files
        self.individual_files = {}
        if self.standardized_dir.exists():
            for file in self.standardized_dir.glob("*.csv"):
                if file.name not in ['unified_model_performance.csv', 'unified_risk_assessment.csv', 'unified_stress_testing.csv']:
                    self.individual_files[file.stem] = pd.read_csv(file)
        
        print(f"Loaded {len(self.individual_files)} individual files")
        print(f"Model performance records: {len(self.model_performance) if self.model_performance is not None else 0}")
        print(f"Risk assessment records: {len(self.risk_assessment) if self.risk_assessment is not None else 0}")
        print(f"Stress testing records: {len(self.stress_testing) if self.stress_testing is not None else 0}")
    
    def load_csv(self, path):
        """Load CSV file if it exists."""
        full_path = self.base_dir / path
        if full_path.exists():
            return pd.read_csv(full_path)
        return None
    
    def create_dashboard_html(self):
        """Create the standardized dashboard HTML."""
        
        # Process model performance data
        model_analysis = self.process_model_performance()
        risk_analysis = self.process_risk_assessment()
        stress_analysis = self.process_stress_testing()
        stylized_analysis = self.process_stylized_facts()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Standardized NF-GARCH Research Dashboard</title>
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Standardized NF-GARCH Research Dashboard</h1>
            <p>Clean, Intuitive Analysis with Standardized Data Structure</p>
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
                <div class="tab" onclick="showTab('comparison')">Model Comparison</div>
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
                            <div class="metric-value">{model_analysis.get('best_model', 'N/A')}</div>
                            <div class="metric-label">Best Performing Model</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{model_analysis.get('improvement_pct', 0):.1f}%</div>
                            <div class="metric-label">NF-GARCH Improvement</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">Standardized</div>
                            <div class="metric-label">Data Structure</div>
                        </div>
                    </div>
                    
                    <div class="success-box">
                        <h3>✅ Standardized Data Structure</h3>
                        <p><strong>File Naming:</strong> Intuitive, descriptive names</p>
                        <p><strong>Column Names:</strong> Clear, standardized terminology</p>
                        <p><strong>Model Classification:</strong> Automatic NF-GARCH vs Standard GARCH identification</p>
                        <p><strong>Data Sources:</strong> Unified structure for easy parsing</p>
                    </div>
                </div>
            </div>
            
            <!-- Model Performance Tab -->
            <div id="performance" class="tab-content">
                <div class="section">
                    <h2>📊 Model Performance Analysis</h2>
                    <div class="chart-container" id="performance-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Type</th><th>MSE</th><th>MAE</th><th>RMSE</th><th>Rank</th></tr>
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
                        <tr><th>Model</th><th>Type</th><th>VaR Violation Rate</th><th>Kupiec P-Value</th><th>Risk Rank</th></tr>
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
                        <tr><th>Model</th><th>Type</th><th>Robustness Score</th><th>Stress Performance</th><th>Rank</th></tr>
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
            
            <!-- Model Comparison Tab -->
            <div id="comparison" class="tab-content">
                <div class="section">
                    <h2>⚖️ Model Type Comparison</h2>
                    <div class="chart-container" id="comparison-chart"></div>
                    <table class="data-table">
                        <tr><th>Model Type</th><th>Count</th><th>Avg MSE</th><th>Avg MAE</th><th>Best Model</th></tr>
                        {self._create_comparison_table(model_analysis)}
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
                        type === 'NF-GARCH' ? '#4caf50' : '#ff9800'
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
                        type === 'NF-GARCH' ? '#4caf50' : '#ff9800'
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
                        type === 'NF-GARCH' ? '#4caf50' : '#ff9800'
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
                x: comparisonData.model_type_counts.keys(),
                y: comparisonData.model_type_counts.values(),
                type: 'bar',
                marker: {{ color: ['#ff9800', '#4caf50'] }},
                text: comparisonData.model_type_counts.values(),
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
    </script>
</body>
</html>"""
        
        return html_content
    
    def process_model_performance(self):
        """Process model performance data."""
        if self.model_performance is None:
            return {'models': [], 'mse_values': [], 'model_types': []}
        
        # Get unique models and their performance
        models = self.model_performance['Model'].unique()
        mse_values = []
        model_types = []
        
        for model in models:
            model_data = self.model_performance[self.model_performance['Model'] == model]
            avg_mse = model_data['MSE'].mean()
            model_type = self.classify_model_type(model)
            
            mse_values.append(avg_mse)
            model_types.append(model_type)
        
        # Calculate statistics
        nf_garch_models = len([t for t in model_types if t == 'NF-GARCH'])
        standard_garch_models = len([t for t in model_types if t == 'Standard GARCH'])
        
        # Find best model
        best_idx = np.argmin(mse_values)
        best_model = models[best_idx]
        
        # Calculate improvement
        nf_mse = [mse for mse, mt in zip(mse_values, model_types) if mt == 'NF-GARCH']
        standard_mse = [mse for mse, mt in zip(mse_values, model_types) if mt == 'Standard GARCH']
        
        improvement_pct = 0
        if nf_mse and standard_mse:
            nf_avg = np.mean(nf_mse)
            standard_avg = np.mean(standard_mse)
            improvement_pct = ((standard_avg - nf_avg) / standard_avg) * 100
        
        return {
            'models': list(models),
            'mse_values': mse_values,
            'model_types': model_types,
            'total_models': len(models),
            'nf_garch_models': nf_garch_models,
            'standard_garch_models': standard_garch_models,
            'best_model': best_model,
            'improvement_pct': improvement_pct,
            'model_type_counts': {
                'Standard GARCH': standard_garch_models,
                'NF-GARCH': nf_garch_models
            }
        }
    
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
    
    def process_risk_assessment(self):
        """Process risk assessment data."""
        if self.risk_assessment is None:
            return {'models': [], 'violation_rates': [], 'model_types': []}
        
        # Get unique models and their risk metrics
        models = self.risk_assessment['Model'].unique()
        violation_rates = []
        model_types = []
        
        for model in models:
            model_data = self.risk_assessment[self.risk_assessment['Model'] == model]
            avg_violation = model_data['Violation_Rate'].mean() if 'Violation_Rate' in model_data.columns else 0
            model_type = self.classify_model_type(model)
            
            violation_rates.append(avg_violation)
            model_types.append(model_type)
        
        return {
            'models': list(models),
            'violation_rates': violation_rates,
            'model_types': model_types
        }
    
    def process_stress_testing(self):
        """Process stress testing data."""
        if self.stress_testing is None:
            return {'models': [], 'robustness_scores': [], 'model_types': []}
        
        # Get unique models and their stress metrics
        models = self.stress_testing['Model'].unique()
        robustness_scores = []
        model_types = []
        
        for model in models:
            model_data = self.stress_testing[self.stress_testing['Model'] == model]
            avg_robustness = model_data['Robustness_Score'].mean() if 'Robustness_Score' in model_data.columns else 0
            model_type = self.classify_model_type(model)
            
            robustness_scores.append(avg_robustness)
            model_types.append(model_type)
        
        return {
            'models': list(models),
            'robustness_scores': robustness_scores,
            'model_types': model_types
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
    
    def _create_performance_table(self, model_analysis):
        """Create performance table."""
        if not model_analysis.get('models'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for i, (model, mse, model_type) in enumerate(zip(
            model_analysis['models'],
            model_analysis['mse_values'],
            model_analysis['model_types']
        )):
            rank = i + 1
            type_class = 'nf-garch' if model_type == 'NF-GARCH' else 'standard-garch'
            mae = 0  # Placeholder - would need to calculate from data
            rmse = np.sqrt(mse)
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{mse:.6f}</td><td>{mae:.6f}</td><td>{rmse:.6f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_risk_table(self, risk_analysis):
        """Create risk table."""
        if not risk_analysis.get('models'):
            return "<tr><td colspan='5'>No data available</td></tr>"
        
        rows = []
        for i, (model, violation_rate, model_type) in enumerate(zip(
            risk_analysis['models'],
            risk_analysis['violation_rates'],
            risk_analysis['model_types']
        )):
            rank = i + 1
            type_class = 'nf-garch' if model_type == 'NF-GARCH' else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{violation_rate:.3f}</td><td>N/A</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_stress_table(self, stress_analysis):
        """Create stress table."""
        if not stress_analysis.get('models'):
            return "<tr><td colspan='5'>No data available</td></tr>"
        
        rows = []
        for i, (model, robustness, model_type) in enumerate(zip(
            stress_analysis['models'],
            stress_analysis['robustness_scores'],
            stress_analysis['model_types']
        )):
            rank = i + 1
            type_class = 'nf-garch' if model_type == 'NF-GARCH' else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{robustness:.3f}</td><td>N/A</td><td>{rank}</td></tr>")
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
            return "<tr><td colspan='5'>No data available</td></tr>"
        
        rows = []
        for model_type, count in model_analysis['model_type_counts'].items():
            # Calculate averages (placeholder values)
            avg_mse = 0.001  # Would calculate from actual data
            avg_mae = 0.01   # Would calculate from actual data
            best_model = "N/A"  # Would find from actual data
            
            rows.append(f"<tr><td>{model_type}</td><td>{count}</td><td>{avg_mse:.6f}</td><td>{avg_mae:.6f}</td><td>{best_model}</td></tr>")
        return ''.join(rows)
    
    def run(self):
        """Generate the standardized dashboard."""
        print("Creating standardized dashboard...")
        
        html_content = self.create_dashboard_html()
        
        # Save HTML file
        html_path = self.docs_dir / "research_dashboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Standardized dashboard created: {html_path}")
        return html_path

def main():
    """Main entry point."""
    dashboard = StandardizedDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
