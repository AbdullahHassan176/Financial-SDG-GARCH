#!/usr/bin/env python3
"""
Build Manifest System
Combines Python dep graph, R dep graph, configs, environment files,
batch scripts, dashboards, templates, Makefile, and README.md.
Outputs MANIFEST_REQUIRED.json and human-readable MANIFEST_REQUIRED.txt.
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManifestBuilder:
    """Builder for required files manifest."""
    
    def __init__(self):
        self.required_files = set()
        self.categories = {
            'source_code': set(),
            'configs': set(),
            'environment': set(),
            'scripts': set(),
            'data': set(),
            'artifacts': set(),
            'documentation': set(),
            'tests': set(),
            'tools': set()
        }
    
    def load_dependency_graphs(self):
        """Load Python and R dependency graphs."""
        python_deps = {}
        r_deps = {}
        
        # Load Python dependencies
        python_dep_file = Path("build/depgraph/depgraph_python.json")
        if python_dep_file.exists():
            try:
                with open(python_dep_file, 'r', encoding='utf-8') as f:
                    python_deps = json.load(f)
                logger.info("Loaded Python dependency graph")
            except Exception as e:
                logger.error(f"Error loading Python deps: {e}")
        
        # Load R dependencies
        r_dep_file = Path("build/depgraph/depgraph_r.json")
        if r_dep_file.exists():
            try:
                with open(r_dep_file, 'r', encoding='utf-8') as f:
                    r_deps = json.load(f)
                logger.info("Loaded R dependency graph")
            except Exception as e:
                logger.error(f"Error loading R deps: {e}")
        
        return python_deps, r_deps
    
    def add_source_files(self):
        """Add essential source code files."""
        # Python source files
        for pattern in ["**/*.py"]:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['source_code'].add(str(file_path))
        
        # R source files
        for pattern in ["**/*.R"]:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['source_code'].add(str(file_path))
    
    def add_config_files(self):
        """Add configuration files."""
        config_files = [
            "configs/*.yml", "configs/*.yaml", "configs/*.json",
            "*.yml", "*.yaml", "*.json", "*.toml"
        ]
        
        for pattern in config_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['configs'].add(str(file_path))
    
    def add_environment_files(self):
        """Add environment files."""
        env_files = [
            "environment.yml", "requirements.txt", "requirements*.txt",
            "renv.lock", "Pipfile", "poetry.lock", "pyproject.toml"
        ]
        
        for pattern in env_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['environment'].add(str(file_path))
    
    def add_script_files(self):
        """Add script files."""
        script_files = [
            "*.bat", "*.sh", "*.ps1", "run_*.py", "run_*.R"
        ]
        
        for pattern in script_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['scripts'].add(str(file_path))
    
    def add_data_files(self):
        """Add essential data files."""
        data_files = [
            "data/processed/*", "data/raw/*.csv", "data/raw/*.xlsx"
        ]
        
        for pattern in data_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['data'].add(str(file_path))
    
    def add_artifact_files(self):
        """Add artifact files."""
        artifact_files = [
            "artifacts/**/*", "outputs/**/*", "results/**/*"
        ]
        
        for pattern in artifact_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['artifacts'].add(str(file_path))
    
    def add_documentation_files(self):
        """Add documentation files."""
        doc_files = [
            "README.md", "CLEANROOM_STATUS.md", "LICENSE", "CITATION.cff",
            "docs/**/*.md", "docs/**/*.html", "docs/**/*.pdf"
        ]
        
        for pattern in doc_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['documentation'].add(str(file_path))
    
    def add_test_files(self):
        """Add test files."""
        test_files = [
            "tests/**/*.py", "tests/**/*.R", "test_*.py", "test_*.R"
        ]
        
        for pattern in test_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['tests'].add(str(file_path))
    
    def add_tool_files(self):
        """Add tool files."""
        tool_files = [
            "tools/**/*.py", "tools/**/*.R", "tools/**/*.sh"
        ]
        
        for pattern in tool_files:
            for file_path in Path(".").glob(pattern):
                if self.is_essential_file(file_path):
                    self.required_files.add(str(file_path))
                    self.categories['tools'].add(str(file_path))
    
    def is_essential_file(self, file_path):
        """Check if file is essential for the repository."""
        file_path = Path(file_path)
        
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 
                    'venv', '.venv', 'archive', 'build'}
        
        for part in file_path.parts:
            if part in skip_dirs:
                return False
        
        # Skip certain file types
        skip_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe'}
        if file_path.suffix in skip_extensions:
            return False
        
        # Skip temporary files
        if file_path.name.startswith('.') and file_path.name not in {'.gitignore', '.pre-commit-config.yaml'}:
            return False
        
        return True
    
    def build_manifest(self):
        """Build the complete manifest."""
        logger.info("Building required files manifest")
        
        # Load dependency graphs
        python_deps, r_deps = self.load_dependency_graphs()
        
        # Add files by category
        self.add_source_files()
        self.add_config_files()
        self.add_environment_files()
        self.add_script_files()
        self.add_data_files()
        self.add_artifact_files()
        self.add_documentation_files()
        self.add_test_files()
        self.add_tool_files()
        
        # Add essential root files
        essential_root_files = [
            "Makefile", "README.md", "CLEANROOM_STATUS.md", 
            ".gitignore", ".pre-commit-config.yaml"
        ]
        
        for file_name in essential_root_files:
            file_path = Path(file_name)
            if file_path.exists():
                self.required_files.add(str(file_path))
                self.categories['documentation'].add(str(file_path))
        
        # Create manifest structure
        manifest = {
            'metadata': {
                'generated_at': str(Path().cwd()),
                'total_files': len(self.required_files),
                'categories': {k: len(v) for k, v in self.categories.items()}
            },
            'required_files': sorted(list(self.required_files)),
            'categories': {k: sorted(list(v)) for k, v in self.categories.items()},
            'dependency_info': {
                'python_deps': python_deps.get('metadata', {}),
                'r_deps': r_deps.get('metadata', {})
            }
        }
        
        return manifest
    
    def save_manifest(self, manifest, json_file="MANIFEST_REQUIRED.json", txt_file="MANIFEST_REQUIRED.txt"):
        """Save manifest to JSON and text files."""
        # Save JSON manifest
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON manifest saved to {json_file}")
        except Exception as e:
            logger.error(f"Error saving JSON manifest: {e}")
            return False
        
        # Save human-readable text manifest
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("NF-GARCH Repository Required Files Manifest\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {manifest['metadata']['generated_at']}\n")
                f.write(f"Total files: {manifest['metadata']['total_files']}\n\n")
                
                f.write("Categories:\n")
                for category, count in manifest['metadata']['categories'].items():
                    f.write(f"  {category}: {count} files\n")
                f.write("\n")
                
                f.write("Required Files:\n")
                f.write("-" * 20 + "\n")
                for file_path in manifest['required_files']:
                    f.write(f"{file_path}\n")
                
                f.write("\nFiles by Category:\n")
                f.write("-" * 20 + "\n")
                for category, files in manifest['categories'].items():
                    if files:
                        f.write(f"\n{category.upper()}:\n")
                        for file_path in files:
                            f.write(f"  {file_path}\n")
            
            logger.info(f"Text manifest saved to {txt_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving text manifest: {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build required files manifest")
    parser.add_argument("--json-output", default="MANIFEST_REQUIRED.json",
                       help="JSON output file (default: MANIFEST_REQUIRED.json)")
    parser.add_argument("--txt-output", default="MANIFEST_REQUIRED.txt",
                       help="Text output file (default: MANIFEST_REQUIRED.txt)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Building required files manifest")
    
    # Create manifest builder
    builder = ManifestBuilder()
    
    # Build manifest
    manifest = builder.build_manifest()
    
    # Save manifest
    if builder.save_manifest(manifest, args.json_output, args.txt_output):
        logger.info(f"✅ Manifest created successfully")
        logger.info(f"Total files: {manifest['metadata']['total_files']}")
        for category, count in manifest['metadata']['categories'].items():
            if count > 0:
                logger.info(f"  {category}: {count} files")
        return 0
    else:
        logger.error("❌ Failed to create manifest")
        return 1

if __name__ == "__main__":
    exit(main())
