#!/usr/bin/env python3
"""
Create a working research dashboard with embedded data.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class WorkingDashboard:
    """Create a working research dashboard with embedded data."""
    
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
    
    def create_dashboard_html(self):
        """Create the dashboard HTML with embedded data."""
        
        # Process data
        model_performance = {}
        asset_performance = {}
        risk_performance = {}
        
        if self.acc_data is not None:
            # Model performance
            model_mse = self.acc_data.groupby('Model')['MSE'].mean().sort_values()
            model_performance = {
                'models': list(model_mse.index),
                'mse_values': [float(x) for x in model_mse.values],
                'best_model': model_mse.idxmin(),
                'best_mse': float(model_mse.min()),
                'worst_mse': float(model_mse.max()),
                'improvement_ratio': float(model_mse.max() / model_mse.min())
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
    <title>NF-GARCH Research Dashboard</title>
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
            <h1>NF-GARCH Research Dashboard</h1>
            <p>Key Findings and Model Performance Analysis</p>
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
                        <div class="insight-value">{model_performance.get('improvement_ratio', 0):.1f}x</div>
                        <div class="insight-label">Performance Improvement</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-value">{significance_rate:.1f}%</div>
                        <div class="insight-label">Statistical Significance</div>
                    </div>
                </div>
            </div>
            
            <!-- Model Performance -->
            <div class="section">
                <h2>📊 Model Performance Comparison</h2>
                <div class="chart-container" id="model-chart"></div>
                <table class="data-table">
                    <tr><th>Model</th><th>Average MSE</th><th>Performance Rank</th></tr>
                    {self._create_model_table(model_performance)}
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
                    <tr><th>Model</th><th>Violation Rate</th><th>Risk Rank</th></tr>
                    {self._create_risk_table(risk_performance)}
                </table>
            </div>
            
            <!-- Research Summary -->
            <div class="section">
                <h2>🎯 Research Summary</h2>
                <p><strong>Key Findings:</strong></p>
                <ul>
                    <li><strong>Best Model:</strong> {model_performance.get('best_model', 'N/A')} with MSE of {model_performance.get('best_mse', 'N/A'):.6f}</li>
                    <li><strong>Best Asset:</strong> {asset_performance.get('best_asset', 'N/A')} shows lowest prediction error</li>
                    <li><strong>Performance Range:</strong> {model_performance.get('improvement_ratio', 'N/A'):.1f}x difference between best and worst models</li>
                    <li><strong>Risk Assessment:</strong> {risk_performance.get('best_risk_model', 'N/A')} shows most reliable VaR estimates</li>
                    <li><strong>Statistical Validation:</strong> {significant_tests} out of {total_tests} tests show significant results</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // Model Performance Chart
        var modelData = {json.dumps(model_performance)};
        if (modelData.models && modelData.models.length > 0) {{
            var modelTrace = {{
                x: modelData.models,
                y: modelData.mse_values,
                type: 'bar',
                marker: {{
                    color: modelData.mse_values.map((val, i) => 
                        val === Math.min(...modelData.mse_values) ? 'green' : 'orange'
                    )
                }},
                text: modelData.mse_values.map(val => val.toFixed(6)),
                textposition: 'auto'
            }};
            
            var modelLayout = {{
                title: 'Model Performance Comparison (Lower MSE = Better)',
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
                marker: {{ color: 'red' }},
                text: riskData.violation_rates.map(val => val.toFixed(3)),
                textposition: 'auto'
            }};
            
            var riskLayout = {{
                title: 'VaR Backtesting Results (Lower Violation Rate = Better)',
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
    
    def _create_model_table(self, model_performance):
        """Create model performance table."""
        if not model_performance.get('models'):
            return "<tr><td colspan='3'>No data available</td></tr>"
        
        rows = []
        for i, (model, mse) in enumerate(zip(model_performance['models'], model_performance['mse_values'])):
            rank = i + 1
            rows.append(f"<tr><td>{model}</td><td>{mse:.6f}</td><td>{rank}</td></tr>")
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
    
    def _create_risk_table(self, risk_performance):
        """Create risk performance table."""
        if not risk_performance.get('models'):
            return "<tr><td colspan='3'>No data available</td></tr>"
        
        rows = []
        for i, (model, rate) in enumerate(zip(risk_performance['models'], risk_performance['violation_rates'])):
            rank = i + 1
            rows.append(f"<tr><td>{model}</td><td>{rate:.3f}</td><td>{rank}</td></tr>")
        return ''.join(rows)
    
    def run(self):
        """Generate the dashboard."""
        print("Creating working research dashboard...")
        
        html_content = self.create_dashboard_html()
        
        # Save HTML file
        html_path = self.docs_dir / "research_dashboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Working dashboard created: {html_path}")
        return html_path

def main():
    """Main entry point."""
    dashboard = WorkingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
