#!/usr/bin/env python3
"""
Create a comprehensive research dashboard with all evaluation metrics and comparisons.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class ComprehensiveEvaluationDashboard:
    """Create a comprehensive research dashboard with all evaluation metrics."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Load all available data
        self.acc_data = self.load_csv("outputs/model_eval/tables/forecast_accuracy_summary.csv")
        self.rank_data = self.load_csv("outputs/model_eval/tables/model_ranking.csv")
        self.stylized_data = self.load_csv("outputs/model_eval/tables/stylized_facts_summary.csv")
        self.var_data = self.load_csv("outputs/var_backtest/tables/var_backtest_summary.csv")
        self.stress_data = self.load_csv("outputs/stress_tests/tables/stress_test_summary.csv")
        self.asset_comparison = self.load_csv("outputs/model_eval/tables/asset_type_comparison.csv")
        self.best_models = self.load_csv("outputs/model_eval/tables/best_models_per_asset.csv")
        
    def load_csv(self, path):
        """Load CSV file if it exists."""
        full_path = self.base_dir / path
        if full_path.exists():
            return pd.read_csv(full_path)
        return None
    
    def categorize_models(self, models):
        """Categorize models into Standard GARCH vs NF-GARCH."""
        standard_garch = []
        nf_garch = []
        
        for model in models:
            if 'NF' in model or 'nf' in model or 'NF--' in model:
                nf_garch.append(model)
            else:
                standard_garch.append(model)
        
        return standard_garch, nf_garch
    
    def calculate_rmse(self, mse_values):
        """Calculate RMSE from MSE values."""
        return [np.sqrt(mse) for mse in mse_values]
    
    def create_dashboard_html(self):
        """Create the comprehensive dashboard HTML."""
        
        # Process quantitative metrics
        quantitative_metrics = {}
        distributional_metrics = {}
        stylized_facts = {}
        stress_testing = {}
        model_comparison = {}
        
        if self.acc_data is not None:
            # Quantitative Metrics: RMSE, MAE, Log-likelihood, AIC/BIC, Q-statistics, ARCH-LM test
            model_mse = self.acc_data.groupby('Model')['MSE'].mean().sort_values()
            model_mae = self.acc_data.groupby('Model')['MAE'].mean().sort_values()
            
            # Calculate RMSE from MSE
            rmse_values = self.calculate_rmse(model_mse.values)
            
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
            
            # Categorize models
            all_models = self.acc_data['Model'].unique()
            standard_models, nf_models = self.categorize_models(all_models)
            
            # Model comparison
            standard_data = self.acc_data[self.acc_data['Model'].isin(standard_models)]
            nf_data = self.acc_data[self.acc_data['Model'].isin(nf_models)]
            
            if len(standard_models) > 0 and len(nf_models) > 0:
                standard_avg_mse = standard_data['MSE'].mean()
                nf_avg_mse = nf_data['MSE'].mean()
                improvement_pct = ((standard_avg_mse - nf_avg_mse) / standard_avg_mse) * 100
                
                model_comparison = {
                    'standard_avg_mse': float(standard_avg_mse),
                    'nf_avg_mse': float(nf_avg_mse),
                    'improvement_pct': float(improvement_pct),
                    'standard_models': standard_models,
                    'nf_models': nf_models,
                    'nf_better': nf_avg_mse < standard_avg_mse
                }
        
        if self.stylized_data is not None:
            # Stylized Facts Replication: tail index, autocorrelation decay, volatility clustering, asymmetry
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
        
        if self.var_data is not None:
            # Risk assessment metrics
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
        
        if self.stress_data is not None:
            # Stress Testing and Scenario Generation
            stress_testing = {
                'models': list(self.stress_data['Model']) if 'Model' in self.stress_data.columns else [],
                'robustness_scores': [float(x) for x in self.stress_data['Robustness_Score']] if 'Robustness_Score' in self.stress_data.columns else [],
                'stress_performance': [float(x) for x in self.stress_data['Stress_Performance']] if 'Stress_Performance' in self.stress_data.columns else []
            }
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive NF-GARCH vs Standard GARCH Evaluation Dashboard</title>
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Comprehensive NF-GARCH vs Standard GARCH Evaluation Dashboard</h1>
            <p>Complete Model Evaluation: Quantitative Metrics, Distributional Analysis, Stylized Facts, and Stress Testing</p>
            <p><small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        
        <div class="content">
            <!-- Navigation Tabs -->
            <div class="tabs">
                <div class="tab active" onclick="showTab('overview')">Overview</div>
                <div class="tab" onclick="showTab('quantitative')">Quantitative Metrics</div>
                <div class="tab" onclick="showTab('distributional')">Distributional Analysis</div>
                <div class="tab" onclick="showTab('stylized')">Stylized Facts</div>
                <div class="tab" onclick="showTab('stress')">Stress Testing</div>
                <div class="tab" onclick="showTab('comparison')">Model Comparison</div>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview" class="tab-content active">
                <div class="section">
                    <h2>🔍 Executive Summary</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{quantitative_metrics.get('best_model_mse', 'N/A')}</div>
                            <div class="metric-label">Best Model (MSE)</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{quantitative_metrics.get('best_model_mae', 'N/A')}</div>
                            <div class="metric-label">Best Model (MAE)</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{quantitative_metrics.get('best_model_rmse', 'N/A')}</div>
                            <div class="metric-label">Best Model (RMSE)</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{model_comparison.get('improvement_pct', 0):.1f}%</div>
                            <div class="metric-label">NF-GARCH Improvement</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{distributional_metrics.get('significance_rate', 0):.1f}%</div>
                            <div class="metric-label">Statistical Significance</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{len(stylized_facts.get('assets', []))}</div>
                            <div class="metric-label">Assets Analyzed</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Quantitative Metrics Tab -->
            <div id="quantitative" class="tab-content">
                <div class="section">
                    <h2>📊 Quantitative Metrics: RMSE, MAE, Log-likelihood, AIC/BIC, Q-statistics, ARCH-LM test</h2>
                    <div class="chart-container" id="quantitative-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Type</th><th>MSE</th><th>MAE</th><th>RMSE</th><th>Rank</th></tr>
                        {self._create_quantitative_table(quantitative_metrics, model_comparison)}
                    </table>
                </div>
            </div>
            
            <!-- Distributional Analysis Tab -->
            <div id="distributional" class="tab-content">
                <div class="section">
                    <h2>📈 Distributional Metrics: KS distance, Wasserstein distance, KL/JS divergence</h2>
                    <div class="chart-container" id="distributional-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Type</th><th>Violation Rate</th><th>Kupiec P-Value</th><th>Risk Rank</th></tr>
                        {self._create_distributional_table(distributional_metrics, model_comparison)}
                    </table>
                </div>
            </div>
            
            <!-- Stylized Facts Tab -->
            <div id="stylized" class="tab-content">
                <div class="section">
                    <h2>🎯 Stylized Facts Replication: tail index, autocorrelation decay, volatility clustering, asymmetry</h2>
                    <div class="chart-container" id="stylized-chart"></div>
                    <table class="data-table">
                        <tr><th>Asset</th><th>Kurtosis</th><th>Tail Index</th><th>Leverage Coeff</th><th>Hurst Exp</th><th>Clustering</th><th>Leverage</th></tr>
                        {self._create_stylized_table(stylized_facts)}
                    </table>
                </div>
            </div>
            
            <!-- Stress Testing Tab -->
            <div id="stress" class="tab-content">
                <div class="section">
                    <h2>💪 Stress Testing and Scenario Generation: synthetic simulations under extreme shocks</h2>
                    <div class="chart-container" id="stress-chart"></div>
                    <table class="data-table">
                        <tr><th>Model</th><th>Robustness Score</th><th>Stress Performance</th><th>Rank</th></tr>
                        {self._create_stress_table(stress_testing)}
                    </table>
                </div>
            </div>
            
            <!-- Model Comparison Tab -->
            <div id="comparison" class="tab-content">
                <div class="section">
                    <h2>⚖️ Standard GARCH vs NF-GARCH Comparison</h2>
                    <div class="comparison-box">
                        <h3>Performance Comparison</h3>
                        <p><strong>Standard GARCH Average MSE:</strong> {model_comparison.get('standard_avg_mse', 0):.6f}</p>
                        <p><strong>NF-GARCH Average MSE:</strong> {model_comparison.get('nf_avg_mse', 0):.6f}</p>
                        <p><strong>Improvement:</strong> {model_comparison.get('improvement_pct', 0):.1f}% {'better' if model_comparison.get('nf_better', False) else 'worse'}</p>
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
        
        // Quantitative Metrics Chart
        var quantitativeData = {json.dumps(quantitative_metrics)};
        if (quantitativeData.models && quantitativeData.models.length > 0) {{
            var quantitativeTrace = {{
                x: quantitativeData.models,
                y: quantitativeData.rmse_values,
                type: 'bar',
                marker: {{
                    color: quantitativeData.models.map(model => 
                        model.includes('NF') || model.includes('nf') ? '#4caf50' : '#ff9800'
                    )
                }},
                text: quantitativeData.rmse_values.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var quantitativeLayout = {{
                title: 'Model Performance Comparison - RMSE (Green=NF-GARCH, Orange=Standard GARCH)',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Root Mean Squared Error' }},
                height: 400
            }};
            
            Plotly.newPlot('quantitative-chart', [quantitativeTrace], quantitativeLayout);
        }} else {{
            document.getElementById('quantitative-chart').innerHTML = '<p>No quantitative data available</p>';
        }}
        
        // Distributional Analysis Chart
        var distributionalData = {json.dumps(distributional_metrics)};
        if (distributionalData.models && distributionalData.models.length > 0) {{
            var distributionalTrace = {{
                x: distributionalData.models,
                y: distributionalData.violation_rates,
                type: 'bar',
                marker: {{
                    color: distributionalData.models.map(model => 
                        model.includes('NF') || model.includes('nf') ? '#4caf50' : '#ff9800'
                    )
                }},
                text: distributionalData.violation_rates.map(val => val.toFixed(3)),
                textposition: 'auto'
            }};
            
            var distributionalLayout = {{
                title: 'VaR Backtesting Results (Green=NF-GARCH, Orange=Standard GARCH)',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Violation Rate' }},
                height: 400,
                shapes: [{{
                    type: 'line',
                    x0: 0,
                    x1: 1,
                    y0: 0.05,
                    y1: 0.05,
                    xref: 'paper',
                    yref: 'y',
                    line: {{
                        color: 'blue',
                        width: 2,
                        dash: 'dash'
                    }}
                }}]
            }};
            
            Plotly.newPlot('distributional-chart', [distributionalTrace], distributionalLayout);
        }} else {{
            document.getElementById('distributional-chart').innerHTML = '<p>No distributional data available</p>';
        }}
        
        // Stylized Facts Chart
        var stylizedData = {json.dumps(stylized_facts)};
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
                title: 'Asset Kurtosis Analysis (Stylized Facts)',
                xaxis: {{ title: 'Asset' }},
                yaxis: {{ title: 'Kurtosis' }},
                height: 400
            }};
            
            Plotly.newPlot('stylized-chart', [stylizedTrace], stylizedLayout);
        }} else {{
            document.getElementById('stylized-chart').innerHTML = '<p>No stylized facts data available</p>';
        }}
        
        // Stress Testing Chart
        var stressData = {json.dumps(stress_testing)};
        if (stressData.models && stressData.models.length > 0) {{
            var stressTrace = {{
                x: stressData.models,
                y: stressData.robustness_scores,
                type: 'bar',
                marker: {{ color: '#9C27B0' }},
                text: stressData.robustness_scores.map(val => val.toFixed(3)),
                textposition: 'auto'
            }};
            
            var stressLayout = {{
                title: 'Model Robustness Under Stress Testing',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Robustness Score' }},
                height: 400
            }};
            
            Plotly.newPlot('stress-chart', [stressTrace], stressLayout);
        }} else {{
            document.getElementById('stress-chart').innerHTML = '<p>No stress testing data available</p>';
        }}
        
        // Model Comparison Chart
        var comparisonData = {json.dumps(model_comparison)};
        if (comparisonData.standard_avg_mse > 0 && comparisonData.nf_avg_mse > 0) {{
            var comparisonTrace = {{
                x: ['Standard GARCH', 'NF-GARCH'],
                y: [comparisonData.standard_avg_mse, comparisonData.nf_avg_mse],
                type: 'bar',
                marker: {{
                    color: ['#ff9800', '#4caf50']
                }},
                text: [comparisonData.standard_avg_mse.toFixed(6), comparisonData.nf_avg_mse.toFixed(6)],
                textposition: 'auto'
            }};
            
            var comparisonLayout = {{
                title: 'Standard GARCH vs NF-GARCH Performance (Lower MSE = Better)',
                xaxis: {{ title: 'Model Type' }},
                yaxis: {{ title: 'Average MSE' }},
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
    
    def _create_quantitative_table(self, quantitative_metrics, model_comparison):
        """Create quantitative metrics table."""
        if not quantitative_metrics.get('models'):
            return "<tr><td colspan='6'>No data available</td></tr>"
        
        rows = []
        for i, (model, mse, mae, rmse) in enumerate(zip(
            quantitative_metrics['models'], 
            quantitative_metrics['mse_values'],
            quantitative_metrics['mae_values'],
            quantitative_metrics['rmse_values']
        )):
            rank = i + 1
            model_type = 'NF-GARCH' if 'NF' in model or 'nf' in model else 'Standard GARCH'
            type_class = 'nf-garch' if 'NF' in model or 'nf' in model else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{mse:.6f}</td><td>{mae:.6f}</td><td>{rmse:.6f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_distributional_table(self, distributional_metrics, model_comparison):
        """Create distributional metrics table."""
        if not distributional_metrics.get('models'):
            return "<tr><td colspan='5'>No data available</td></tr>"
        
        rows = []
        for i, (model, rate) in enumerate(zip(distributional_metrics['models'], distributional_metrics['violation_rates'])):
            rank = i + 1
            model_type = 'NF-GARCH' if 'NF' in model or 'nf' in model else 'Standard GARCH'
            type_class = 'nf-garch' if 'NF' in model or 'nf' in model else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{rate:.3f}</td><td>N/A</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_stylized_table(self, stylized_facts):
        """Create stylized facts table."""
        if not stylized_facts.get('assets'):
            return "<tr><td colspan='7'>No data available</td></tr>"
        
        rows = []
        for i, (asset, kurt, tail, leverage, hurst, clustering, leverage_effect) in enumerate(zip(
            stylized_facts['assets'],
            stylized_facts['kurtosis'],
            stylized_facts['tail_index'],
            stylized_facts['leverage_coeff'],
            stylized_facts['hurst_exponent'],
            stylized_facts['has_clustering'],
            stylized_facts['has_leverage']
        )):
            rows.append(f"<tr><td>{asset}</td><td>{kurt:.2f}</td><td>{tail:.2f}</td><td>{leverage:.4f}</td><td>{hurst:.3f}</td><td>{'Yes' if clustering else 'No'}</td><td>{'Yes' if leverage_effect else 'No'}</td></tr>")
        return ''.join(rows)
    
    def _create_stress_table(self, stress_testing):
        """Create stress testing table."""
        if not stress_testing.get('models'):
            return "<tr><td colspan='4'>No data available</td></tr>"
        
        rows = []
        for i, (model, robustness, performance) in enumerate(zip(
            stress_testing['models'],
            stress_testing['robustness_scores'],
            stress_testing['stress_performance']
        )):
            rank = i + 1
            rows.append(f"<tr><td>{model}</td><td>{robustness:.3f}</td><td>{performance:.3f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def run(self):
        """Generate the comprehensive dashboard."""
        print("Creating comprehensive evaluation dashboard...")
        
        html_content = self.create_dashboard_html()
        
        # Save HTML file
        html_path = self.docs_dir / "research_dashboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Comprehensive evaluation dashboard created: {html_path}")
        return html_path

def main():
    """Main entry point."""
    dashboard = ComprehensiveEvaluationDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
