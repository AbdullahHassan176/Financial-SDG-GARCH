#!/usr/bin/env python3
"""
Create a research dashboard that clearly distinguishes between standard GARCH and NF-GARCH models.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class NFGARCHDashboard:
    """Create a research dashboard with clear GARCH vs NF-GARCH distinction."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Load data
        self.acc_data = self.load_csv("outputs/model_eval/tables/forecast_accuracy_summary.csv")
        self.var_data = self.load_csv("outputs/var_backtest/tables/var_backtest_summary.csv")
        self.rank_data = self.load_csv("outputs/model_eval/tables/model_ranking.csv")
        
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
    
    def create_dashboard_html(self):
        """Create the dashboard HTML with embedded data."""
        
        # Process data
        model_performance = {}
        asset_performance = {}
        risk_performance = {}
        garch_comparison = {}
        
        if self.acc_data is not None:
            # Categorize models
            all_models = self.acc_data['Model'].unique()
            standard_models, nf_models = self.categorize_models(all_models)
            
            # Model performance by category
            standard_data = self.acc_data[self.acc_data['Model'].isin(standard_models)]
            nf_data = self.acc_data[self.acc_data['Model'].isin(nf_models)]
            
            # Overall model performance
            model_mse = self.acc_data.groupby('Model')['MSE'].mean().sort_values()
            model_performance = {
                'models': list(model_mse.index),
                'mse_values': [float(x) for x in model_mse.values],
                'best_model': model_mse.idxmin(),
                'best_mse': float(model_mse.min()),
                'worst_mse': float(model_mse.max()),
                'improvement_ratio': float(model_mse.max() / model_mse.min())
            }
            
            # GARCH vs NF-GARCH comparison
            if len(standard_models) > 0 and len(nf_models) > 0:
                standard_avg_mse = standard_data['MSE'].mean()
                nf_avg_mse = nf_data['MSE'].mean()
                improvement_pct = ((standard_avg_mse - nf_avg_mse) / standard_avg_mse) * 100
                
                garch_comparison = {
                    'standard_avg_mse': float(standard_avg_mse),
                    'nf_avg_mse': float(nf_avg_mse),
                    'improvement_pct': float(improvement_pct),
                    'standard_models': standard_models,
                    'nf_models': nf_models,
                    'nf_better': nf_avg_mse < standard_avg_mse
                }
            else:
                garch_comparison = {
                    'standard_avg_mse': 0,
                    'nf_avg_mse': 0,
                    'improvement_pct': 0,
                    'standard_models': standard_models,
                    'nf_models': nf_models,
                    'nf_better': False
                }
            
            # Asset performance
            asset_mse = self.acc_data.groupby('Asset')['MSE'].mean().sort_values()
            asset_performance = {
                'assets': list(asset_mse.index),
                'mse_values': [float(x) for x in asset_mse.values],
                'best_asset': asset_mse.idxmin(),
                'best_asset_mse': float(asset_mse.min())
            }
        
        if self.var_data is not None:
            # Risk performance
            model_violations = self.var_data.groupby('Model')['Violation_Rate'].mean().sort_values()
            risk_performance = {
                'models': list(model_violations.index),
                'violation_rates': [float(x) for x in model_violations.values],
                'best_risk_model': model_violations.idxmin(),
                'best_violation_rate': float(model_violations.min())
            }
            
            # Statistical significance
            significant_tests = len(self.var_data[self.var_data['Kupiec_PValue'] < 0.05])
            total_tests = len(self.var_data)
            significance_rate = significant_tests / total_tests * 100
        else:
            significant_tests = 0
            total_tests = 0
            significance_rate = 0
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NF-GARCH vs Standard GARCH Research Dashboard</title>
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
            max-width: 1200px;
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
        .insights {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .insight-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .insight-value {{
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
            background: #ffeb3b;
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
        }}
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .data-table th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NF-GARCH vs Standard GARCH Research Dashboard</h1>
            <p>Comparative Analysis: Standard GARCH vs NF-GARCH Models</p>
            <p><small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        
        <div class="content">
            <!-- Key Insights -->
            <div class="section">
                <h2>🔍 Key Research Insights</h2>
                <div class="insights">
                    <div class="insight-card">
                        <div class="insight-value">{model_performance.get('best_model', 'N/A')}</div>
                        <div class="insight-label">Best Performing Model</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-value">{asset_performance.get('best_asset', 'N/A')}</div>
                        <div class="insight-label">Best Performing Asset</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-value">{garch_comparison.get('improvement_pct', 0):.1f}%</div>
                        <div class="insight-label">NF-GARCH Improvement</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-value">{significance_rate:.1f}%</div>
                        <div class="insight-label">Statistical Significance</div>
                    </div>
                </div>
            </div>
            
            <!-- GARCH vs NF-GARCH Comparison -->
            <div class="section">
                <h2>⚖️ Standard GARCH vs NF-GARCH Comparison</h2>
                <div class="comparison-box">
                    <h3>Performance Comparison</h3>
                    <p><strong>Standard GARCH Average MSE:</strong> {garch_comparison.get('standard_avg_mse', 0):.6f}</p>
                    <p><strong>NF-GARCH Average MSE:</strong> {garch_comparison.get('nf_avg_mse', 0):.6f}</p>
                    <p><strong>Improvement:</strong> {garch_comparison.get('improvement_pct', 0):.1f}% {'better' if garch_comparison.get('nf_better', False) else 'worse'}</p>
                </div>
                <div class="chart-container" id="comparison-chart"></div>
            </div>
            
            <!-- Model Performance -->
            <div class="section">
                <h2>📊 Model Performance Comparison</h2>
                <div class="chart-container" id="model-chart"></div>
                <table class="data-table">
                    <tr><th>Model</th><th>Type</th><th>Average MSE</th><th>Performance Rank</th></tr>
                    {self._create_model_table_with_types(model_performance, garch_comparison)}
                </table>
            </div>
            
            <!-- Asset Performance -->
            <div class="section">
                <h2>🏢 Asset Performance Analysis</h2>
                <div class="chart-container" id="asset-chart"></div>
                <table class="data-table">
                    <tr><th>Asset</th><th>Average MSE</th><th>Asset Type</th></tr>
                    {self._create_asset_table(asset_performance)}
                </table>
            </div>
            
            <!-- Risk Assessment -->
            <div class="section">
                <h2>⚠️ Risk Assessment Results</h2>
                <div class="chart-container" id="risk-chart"></div>
                <table class="data-table">
                    <tr><th>Model</th><th>Type</th><th>Violation Rate</th><th>Risk Rank</th></tr>
                    {self._create_risk_table_with_types(risk_performance, garch_comparison)}
                </table>
            </div>
            
            <!-- Research Summary -->
            <div class="section">
                <h2>🎯 Research Summary</h2>
                <p><strong>Key Findings:</strong></p>
                <ul>
                    <li><strong>Best Model:</strong> {model_performance.get('best_model', 'N/A')} with MSE of {model_performance.get('best_mse', 'N/A'):.6f}</li>
                    <li><strong>Best Asset:</strong> {asset_performance.get('best_asset', 'N/A')} shows lowest prediction error</li>
                    <li><strong>NF-GARCH Performance:</strong> {garch_comparison.get('improvement_pct', 0):.1f}% {'improvement' if garch_comparison.get('nf_better', False) else 'degradation'} over standard GARCH</li>
                    <li><strong>Risk Assessment:</strong> {risk_performance.get('best_risk_model', 'N/A')} shows most reliable VaR estimates</li>
                    <li><strong>Statistical Validation:</strong> {significant_tests} out of {total_tests} tests show significant results</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // GARCH vs NF-GARCH Comparison Chart
        var garchData = {json.dumps(garch_comparison)};
        if (garchData.standard_avg_mse > 0 && garchData.nf_avg_mse > 0) {{
            var comparisonTrace = {{
                x: ['Standard GARCH', 'NF-GARCH'],
                y: [garchData.standard_avg_mse, garchData.nf_avg_mse],
                type: 'bar',
                marker: {{
                    color: ['#ff9800', '#4caf50']
                }},
                text: [garchData.standard_avg_mse.toFixed(6), garchData.nf_avg_mse.toFixed(6)],
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
            document.getElementById('comparison-chart').innerHTML = '<p>No NF-GARCH data available for comparison</p>';
        }}
        
        // Model Performance Chart
        var modelData = {json.dumps(model_performance)};
        if (modelData.models && modelData.models.length > 0) {{
            var modelTrace = {{
                x: modelData.models,
                y: modelData.mse_values,
                type: 'bar',
                marker: {{
                    color: modelData.models.map(model => 
                        model.includes('NF') || model.includes('nf') ? '#4caf50' : '#ff9800'
                    )
                }},
                text: modelData.mse_values.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var modelLayout = {{
                title: 'Model Performance Comparison (Green=NF-GARCH, Orange=Standard GARCH)',
                xaxis: {{ title: 'Model' }},
                yaxis: {{ title: 'Mean Squared Error' }},
                height: 400
            }};
            
            Plotly.newPlot('model-chart', [modelTrace], modelLayout);
        }} else {{
            document.getElementById('model-chart').innerHTML = '<p>No model data available</p>';
        }}
        
        // Asset Performance Chart
        var assetData = {json.dumps(asset_performance)};
        if (assetData.assets && assetData.assets.length > 0) {{
            var fxAssets = ['EURUSD', 'EURZAR', 'GBPCNY', 'GBPUSD', 'GBPZAR', 'USDZAR'];
            var assetTrace = {{
                x: assetData.assets,
                y: assetData.mse_values,
                type: 'bar',
                marker: {{
                    color: assetData.assets.map(asset => 
                        fxAssets.includes(asset) ? 'blue' : 'red'
                    )
                }},
                text: assetData.mse_values.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var assetLayout = {{
                title: 'Asset Performance (Blue=FX, Red=Equity)',
                xaxis: {{ title: 'Asset' }},
                yaxis: {{ title: 'Mean Squared Error' }},
                height: 400
            }};
            
            Plotly.newPlot('asset-chart', [assetTrace], assetLayout);
        }} else {{
            document.getElementById('asset-chart').innerHTML = '<p>No asset data available</p>';
        }}
        
        // Risk Assessment Chart
        var riskData = {json.dumps(risk_performance)};
        if (riskData.models && riskData.models.length > 0) {{
            var riskTrace = {{
                x: riskData.models,
                y: riskData.violation_rates,
                type: 'bar',
                marker: {{
                    color: riskData.models.map(model => 
                        model.includes('NF') || model.includes('nf') ? '#4caf50' : '#ff9800'
                    )
                }},
                text: riskData.violation_rates.map(val => val.toFixed(3)),
                textposition: 'auto'
            }};
            
            var riskLayout = {{
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
                }}],
                annotations: [{{
                    x: 0.5,
                    y: 0.05,
                    xref: 'paper',
                    yref: 'y',
                    text: '5% Expected Rate',
                    showarrow: true,
                    arrowhead: 2,
                    arrowcolor: 'blue'
                }}]
            }};
            
            Plotly.newPlot('risk-chart', [riskTrace], riskLayout);
        }} else {{
            document.getElementById('risk-chart').innerHTML = '<p>No risk data available</p>';
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
    def _create_model_table_with_types(self, model_performance, garch_comparison):
        """Create model performance table with model types."""
        if not model_performance.get('models'):
            return "<tr><td colspan='4'>No data available</td></tr>"
        
        rows = []
        for i, (model, mse) in enumerate(zip(model_performance['models'], model_performance['mse_values'])):
            rank = i + 1
            model_type = 'NF-GARCH' if 'NF' in model or 'nf' in model else 'Standard GARCH'
            type_class = 'nf-garch' if 'NF' in model or 'nf' in model else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{mse:.6f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def _create_asset_table(self, asset_performance):
        """Create asset performance table."""
        if not asset_performance.get('assets'):
            return "<tr><td colspan='3'>No data available</td></tr>"
        
        fx_assets = ['EURUSD', 'EURZAR', 'GBPCNY', 'GBPUSD', 'GBPZAR', 'USDZAR']
        rows = []
        for asset, mse in zip(asset_performance['assets'], asset_performance['mse_values']):
            asset_type = 'FX' if asset in fx_assets else 'Equity'
            rows.append(f"<tr><td>{asset}</td><td>{mse:.6f}</td><td>{asset_type}</td></tr>")
        return ''.join(rows)
    
    def _create_risk_table_with_types(self, risk_performance, garch_comparison):
        """Create risk performance table with model types."""
        if not risk_performance.get('models'):
            return "<tr><td colspan='4'>No data available</td></tr>"
        
        rows = []
        for i, (model, rate) in enumerate(zip(risk_performance['models'], risk_performance['violation_rates'])):
            rank = i + 1
            model_type = 'NF-GARCH' if 'NF' in model or 'nf' in model else 'Standard GARCH'
            type_class = 'nf-garch' if 'NF' in model or 'nf' in model else 'standard-garch'
            rows.append(f"<tr><td>{model}</td><td><span class='model-type {type_class}'>{model_type}</span></td><td>{rate:.3f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def run(self):
        """Generate the dashboard."""
        print("Creating NF-GARCH vs Standard GARCH research dashboard...")
        
        html_content = self.create_dashboard_html()
        
        # Save HTML file
        html_path = self.docs_dir / "research_dashboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"NF-GARCH dashboard created: {html_path}")
        return html_path

def main():
    """Main entry point."""
    dashboard = NFGARCHDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
