#!/usr/bin/env python3
"""
Create a simple, focused research dashboard with key insights.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any

class SimpleDashboard:
    """Create a simple, focused research dashboard."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Load key data
        self.acc_data = self.load_csv("outputs/model_eval/tables/forecast_accuracy_summary.csv")
        self.var_data = self.load_csv("outputs/var_backtest/tables/var_backtest_summary.csv")
        self.rank_data = self.load_csv("outputs/model_eval/tables/model_ranking.csv")
        
    def load_csv(self, path):
        """Load CSV file if it exists."""
        full_path = self.base_dir / path
        if full_path.exists():
            return pd.read_csv(full_path)
        return None
    
    def create_model_comparison_chart(self):
        """Create simple model comparison chart."""
        if self.acc_data is None:
            return None
            
        # Model performance by MSE
        model_mse = self.acc_data.groupby('Model')['MSE'].mean().sort_values()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=model_mse.index,
            y=model_mse.values,
            marker_color=['green' if 'eGARCH' in str(model) else 'orange' for model in model_mse.index],
            text=[f'{val:.6f}' for val in model_mse.values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Model Performance Comparison (Lower MSE = Better)",
            xaxis_title="Model",
            yaxis_title="Mean Squared Error",
            height=400
        )
        
        return fig
    
    def create_asset_performance_chart(self):
        """Create asset performance chart."""
        if self.acc_data is None:
            return None
            
        # Asset performance
        asset_mse = self.acc_data.groupby('Asset')['MSE'].mean().sort_values()
        
        # Classify as FX or Equity
        fx_assets = ['EURUSD', 'EURZAR', 'GBPCNY', 'GBPUSD', 'GBPZAR', 'USDZAR']
        colors = ['blue' if asset in fx_assets else 'red' for asset in asset_mse.index]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=asset_mse.index,
            y=asset_mse.values,
            marker_color=colors,
            text=[f'{val:.6f}' for val in asset_mse.values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Asset Performance (Blue=FX, Red=Equity)",
            xaxis_title="Asset",
            yaxis_title="Mean Squared Error",
            height=400
        )
        
        return fig
    
    def create_risk_analysis_chart(self):
        """Create risk analysis chart."""
        if self.var_data is None:
            return None
            
        # Violation rates by model
        model_violations = self.var_data.groupby('Model')['Violation_Rate'].mean().sort_values()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=model_violations.index,
            y=model_violations.values,
            marker_color='red',
            text=[f'{val:.3f}' for val in model_violations.values],
            textposition='auto'
        ))
        
        # Add expected rate line
        fig.add_hline(y=0.05, line_dash="dash", line_color="blue", 
                     annotation_text="5% Expected Rate")
        
        fig.update_layout(
            title="VaR Backtesting Results (Lower Violation Rate = Better)",
            xaxis_title="Model",
            yaxis_title="Violation Rate",
            height=400
        )
        
        return fig
    
    def create_key_insights(self):
        """Create key insights summary."""
        insights = {}
        
        if self.acc_data is not None:
            # Best and worst models
            model_mse = self.acc_data.groupby('Model')['MSE'].mean()
            insights['best_model'] = model_mse.idxmin()
            insights['worst_model'] = model_mse.idxmax()
            insights['best_mse'] = model_mse.min()
            insights['worst_mse'] = model_mse.max()
            insights['improvement_ratio'] = model_mse.max() / model_mse.min()
            
            # Best and worst assets
            asset_mse = self.acc_data.groupby('Asset')['MSE'].mean()
            insights['best_asset'] = asset_mse.idxmin()
            insights['worst_asset'] = asset_mse.idxmax()
        
        if self.var_data is not None:
            # Risk assessment
            model_violations = self.var_data.groupby('Model')['Violation_Rate'].mean()
            insights['best_risk_model'] = model_violations.idxmin()
            insights['worst_risk_model'] = model_violations.idxmax()
            insights['best_violation_rate'] = model_violations.min()
            insights['worst_violation_rate'] = model_violations.max()
            
            # Statistical significance
            significant_tests = len(self.var_data[self.var_data['Kupiec_PValue'] < 0.05])
            insights['significant_tests'] = significant_tests
            insights['total_tests'] = len(self.var_data)
            insights['significance_rate'] = significant_tests / len(self.var_data) * 100
        
        return insights
    
    def create_dashboard_html(self):
        """Create the dashboard HTML."""
        # Generate charts
        model_chart = self.create_model_comparison_chart()
        asset_chart = self.create_asset_performance_chart()
        risk_chart = self.create_risk_analysis_chart()
        
        # Get insights
        insights = self.create_key_insights()
        
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
                        <div class="insight-value">{insights.get('best_model', 'N/A')}</div>
                        <div class="insight-label">Best Performing Model</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-value">{insights.get('best_asset', 'N/A')}</div>
                        <div class="insight-label">Best Performing Asset</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-value">{insights.get('improvement_ratio', 'N/A'):.1f}x</div>
                        <div class="insight-label">Performance Improvement</div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-value">{insights.get('significance_rate', 'N/A'):.1f}%</div>
                        <div class="insight-label">Statistical Significance</div>
                    </div>
                </div>
            </div>
            
            <!-- Model Performance -->
            <div class="section">
                <h2>📊 Model Performance Comparison</h2>
                <div class="chart-container" id="model-chart"></div>
            </div>
            
            <!-- Asset Performance -->
            <div class="section">
                <h2>🏢 Asset Performance Analysis</h2>
                <div class="chart-container" id="asset-chart"></div>
            </div>
            
            <!-- Risk Assessment -->
            <div class="section">
                <h2>⚠️ Risk Assessment Results</h2>
                <div class="chart-container" id="risk-chart"></div>
            </div>
            
            <!-- Research Summary -->
            <div class="section">
                <h2>🎯 Research Summary</h2>
                <p><strong>Key Findings:</strong></p>
                <ul>
                    <li><strong>Best Model:</strong> {insights.get('best_model', 'N/A')} with MSE of {insights.get('best_mse', 'N/A'):.6f}</li>
                    <li><strong>Best Asset:</strong> {insights.get('best_asset', 'N/A')} shows lowest prediction error</li>
                    <li><strong>Performance Range:</strong> {insights.get('improvement_ratio', 'N/A'):.1f}x difference between best and worst models</li>
                    <li><strong>Risk Assessment:</strong> {insights.get('best_risk_model', 'N/A')} shows most reliable VaR estimates</li>
                    <li><strong>Statistical Validation:</strong> {insights.get('significant_tests', 'N/A')} out of {insights.get('total_tests', 'N/A')} tests show significant results</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // Model Chart
        {self._chart_to_js(model_chart, 'model-chart')}
        
        // Asset Chart
        {self._chart_to_js(asset_chart, 'asset-chart')}
        
        // Risk Chart
        {self._chart_to_js(risk_chart, 'risk-chart')}
    </script>
</body>
</html>"""
        
        return html_content
    
    def _chart_to_js(self, fig, container_id):
        """Convert Plotly figure to JavaScript."""
        if fig is None:
            return f"document.getElementById('{container_id}').innerHTML = '<p>No data available for this chart.</p>';"
        
        # Convert to JSON and create JavaScript
        fig_json = fig.to_json()
        return f"""
        var {container_id}_data = {fig_json};
        Plotly.newPlot('{container_id}', {container_id}_data.data, {container_id}_data.layout);
        """
    
    def run(self):
        """Generate the dashboard."""
        print("Creating simple research dashboard...")
        
        html_content = self.create_dashboard_html()
        
        # Save HTML file
        html_path = self.docs_dir / "research_dashboard.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Simple dashboard created: {html_path}")
        return html_path

def main():
    """Main entry point."""
    dashboard = SimpleDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
