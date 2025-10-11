#!/usr/bin/env python3
"""
Main build script for NF-GARCH results consolidation and dashboard.
Single command to rebuild Excel consolidation and interactive dashboard.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
import logging

# Add the tools directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collect_results import ResultsCollector
from build_dashboard import DashboardBuilder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BuildManager:
    """Main class for orchestrating the build process."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.artifacts_dir = self.base_dir / "artifacts"
        self.docs_dir = self.base_dir / "docs"
        
        # Ensure directories exist
        self.artifacts_dir.mkdir(exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)
    
    def run_collection(self) -> Dict[str, Any]:
        """Run the results collection process."""
        logger.info("Starting results collection...")
        
        collector = ResultsCollector(str(self.base_dir))
        report = collector.run()
        
        if report['status'] == 'success':
            logger.info("✓ Results collection completed successfully")
        else:
            logger.error(f"✗ Results collection failed: {report.get('reason', 'Unknown error')}")
        
        return report
    
    def run_dashboard_build(self) -> Dict[str, Any]:
        """Run the dashboard build process."""
        logger.info("Starting dashboard build...")
        
        builder = DashboardBuilder(str(self.base_dir))
        report = builder.run()
        
        if report['status'] == 'success':
            logger.info("✓ Dashboard build completed successfully")
        else:
            logger.error(f"✗ Dashboard build failed: {report.get('error', 'Unknown error')}")
        
        return report
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        required_packages = [
            'pandas', 'numpy', 'openpyxl', 'plotly'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing required packages: {missing_packages}")
            logger.error("Please install with: pip install " + " ".join(missing_packages))
            return False
        
        return True
    
    def create_github_pages_workflow(self):
        """Create GitHub Pages workflow if it doesn't exist."""
        workflow_dir = self.base_dir / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflow_dir / "pages.yml"
        
        if not workflow_file.exists():
            workflow_content = """name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          pip install pandas numpy openpyxl plotly jinja2 pyyaml
          
      - name: Build results and dashboard
        run: |
          python tools/build_results.py
          
      - name: Setup Pages
        uses: actions/configure-pages@v3
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: './docs'
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
"""
            
            with open(workflow_file, 'w') as f:
                f.write(workflow_content)
            
            logger.info("Created GitHub Pages workflow")
        else:
            logger.info("GitHub Pages workflow already exists")
    
    def print_hosting_instructions(self):
        """Print instructions for hosting the dashboard."""
        print("\n" + "="*60)
        print("HOSTING INSTRUCTIONS")
        print("="*60)
        print("To host your dashboard on GitHub Pages:")
        print("1. Push your code to GitHub")
        print("2. Go to your repository Settings")
        print("3. Navigate to Pages section")
        print("4. Set Source to 'Deploy from a branch'")
        print("5. Select branch 'main' and folder '/docs'")
        print("6. Click Save")
        print("7. Your dashboard will be available at:")
        print("   https://[username].github.io/[repository-name]/")
        print("\nAlternatively, you can serve locally:")
        print("  cd docs && python -m http.server 8000")
        print("  Then open http://localhost:8000 in your browser")
        print("="*60)
    
    def run(self) -> Dict[str, Any]:
        """Main execution method."""
        logger.info("Starting NF-GARCH results build process...")
        
        # Check dependencies
        if not self.check_dependencies():
            return {'status': 'failed', 'reason': 'Missing dependencies'}
        
        # Run collection
        collection_report = self.run_collection()
        if collection_report['status'] != 'success':
            return collection_report
        
        # Run dashboard build
        dashboard_report = self.run_dashboard_build()
        if dashboard_report['status'] != 'success':
            return dashboard_report
        
        # Create GitHub Pages workflow
        self.create_github_pages_workflow()
        
        # Print hosting instructions
        self.print_hosting_instructions()
        
        # Final report
        final_report = {
            'status': 'success',
            'collection': collection_report,
            'dashboard': dashboard_report,
            'excel_file': str(self.artifacts_dir / "results_consolidated.xlsx"),
            'dashboard_url': str(self.docs_dir / "index.html"),
            'total_records': collection_report.get('total_records', 0),
            'plots_copied': dashboard_report.get('plots_copied', 0)
        }
        
        logger.info("Build process completed successfully!")
        return final_report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build NF-GARCH results consolidation and dashboard')
    parser.add_argument('--base-dir', default='.', help='Base directory for the project')
    parser.add_argument('--collection-only', action='store_true', help='Run only results collection')
    parser.add_argument('--dashboard-only', action='store_true', help='Run only dashboard build')
    
    args = parser.parse_args()
    
    manager = BuildManager(args.base_dir)
    
    if args.collection_only:
        report = manager.run_collection()
    elif args.dashboard_only:
        report = manager.run_dashboard_build()
    else:
        report = manager.run()
    
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)
    print(f"Status: {report['status']}")
    
    if report['status'] == 'success':
        print(f"Excel File: {report.get('excel_file', 'N/A')}")
        print(f"Dashboard: {report.get('dashboard_url', 'N/A')}")
        print(f"Total Records: {report.get('total_records', 0)}")
        print(f"Plots Copied: {report.get('plots_copied', 0)}")
        
        if 'collection' in report:
            print(f"Files Processed: {report['collection'].get('files_processed', 0)}")
            print(f"Files Skipped: {report['collection'].get('files_skipped', 0)}")
    else:
        print(f"Error: {report.get('reason', report.get('error', 'Unknown error'))}")
    
    print("="*60)
    
    return 0 if report['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())
