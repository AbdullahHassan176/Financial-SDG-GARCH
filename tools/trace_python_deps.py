#!/usr/bin/env python3
"""
Python Dependency Tracer
Statically parses AST for all .py files and follows imports.
Dynamically traces run_all.py and run_modular.py to list reachable modules.
"""

import ast
import json
import argparse
import logging
from pathlib import Path
import sys
import importlib.util
import os
from typing import Set, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PythonDependencyTracer:
    """Tracer for Python dependencies."""
    
    def __init__(self, src_dir="src", scripts_dir="."):
        self.src_dir = Path(src_dir)
        self.scripts_dir = Path(scripts_dir)
        self.dependencies = {
            'static_imports': set(),
            'dynamic_imports': set(),
            'local_modules': set(),
            'external_packages': set(),
            'reachable_modules': set()
        }
    
    def extract_imports_from_ast(self, file_path):
        """Extract imports from AST of a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            return imports
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return set()
    
    def is_local_import(self, import_name):
        """Check if import is local to the project."""
        # Check if it's a relative import or local module
        if import_name.startswith('.'):
            return True
        
        # Check if it exists in src directory
        if self.src_dir.exists():
            module_path = self.src_dir / f"{import_name.replace('.', '/')}.py"
            if module_path.exists():
                return True
        
        return False
    
    def trace_static_dependencies(self):
        """Trace static dependencies from all Python files."""
        logger.info("Tracing static dependencies")
        
        # Find all Python files
        python_files = []
        for pattern in ["**/*.py"]:
            python_files.extend(self.scripts_dir.glob(pattern))
        
        if self.src_dir.exists():
            for pattern in ["**/*.py"]:
                python_files.extend(self.src_dir.glob(pattern))
        
        logger.info(f"Found {len(python_files)} Python files")
        
        for py_file in python_files:
            imports = self.extract_imports_from_ast(py_file)
            
            for import_name in imports:
                self.dependencies['static_imports'].add(import_name)
                
                if self.is_local_import(import_name):
                    self.dependencies['local_modules'].add(import_name)
                else:
                    self.dependencies['external_packages'].add(import_name)
    
    def trace_dynamic_dependencies(self, script_files):
        """Trace dynamic dependencies from main scripts."""
        logger.info("Tracing dynamic dependencies")
        
        for script_file in script_files:
            if not Path(script_file).exists():
                logger.warning(f"Script file {script_file} not found")
                continue
            
            logger.info(f"Tracing {script_file}")
            
            # Simple dynamic tracing by analyzing import statements
            # This is a simplified approach - in practice, you might use
            # coverage.py or other tools for more sophisticated tracing
            imports = self.extract_imports_from_ast(script_file)
            
            for import_name in imports:
                self.dependencies['dynamic_imports'].add(import_name)
                self.dependencies['reachable_modules'].add(import_name)
    
    def categorize_dependencies(self):
        """Categorize dependencies into different types."""
        categorized = {
            'standard_library': set(),
            'third_party': set(),
            'local_project': set(),
            'unknown': set()
        }
        
        # Common standard library modules
        stdlib_modules = {
            'os', 'sys', 'json', 'pathlib', 'datetime', 'logging', 'argparse',
            'numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn', 'plotly'
        }
        
        for module in self.dependencies['external_packages']:
            if module in stdlib_modules:
                categorized['standard_library'].add(module)
            else:
                categorized['third_party'].add(module)
        
        for module in self.dependencies['local_modules']:
            categorized['local_project'].add(module)
        
        return categorized
    
    def generate_dependency_graph(self):
        """Generate dependency graph JSON."""
        categorized = self.categorize_dependencies()
        
        graph = {
            'metadata': {
                'src_dir': str(self.src_dir),
                'scripts_dir': str(self.scripts_dir),
                'total_files_analyzed': len(list(self.scripts_dir.glob("**/*.py")))
            },
            'dependencies': {
                'static_imports': sorted(list(self.dependencies['static_imports'])),
                'dynamic_imports': sorted(list(self.dependencies['dynamic_imports'])),
                'local_modules': sorted(list(self.dependencies['local_modules'])),
                'external_packages': sorted(list(self.dependencies['external_packages'])),
                'reachable_modules': sorted(list(self.dependencies['reachable_modules']))
            },
            'categorized': {
                'standard_library': sorted(list(categorized['standard_library'])),
                'third_party': sorted(list(categorized['third_party'])),
                'local_project': sorted(list(categorized['local_project'])),
                'unknown': sorted(list(categorized['unknown']))
            }
        }
        
        return graph

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Trace Python dependencies")
    parser.add_argument("--src-dir", default="src",
                       help="Source directory (default: src)")
    parser.add_argument("--scripts-dir", default=".",
                       help="Scripts directory (default: .)")
    parser.add_argument("--output", default="build/depgraph/depgraph_python.json",
                       help="Output JSON file (default: build/depgraph/depgraph_python.json)")
    parser.add_argument("--scripts", nargs="+", default=["run_all.py", "run_modular.py"],
                       help="Main script files to trace (default: run_all.py run_modular.py)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting Python dependency tracing")
    logger.info(f"Source directory: {args.src_dir}")
    logger.info(f"Scripts directory: {args.scripts_dir}")
    logger.info(f"Scripts to trace: {args.scripts}")
    
    # Create tracer
    tracer = PythonDependencyTracer(args.src_dir, args.scripts_dir)
    
    # Trace dependencies
    tracer.trace_static_dependencies()
    tracer.trace_dynamic_dependencies(args.scripts)
    
    # Generate graph
    graph = tracer.generate_dependency_graph()
    
    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dependency graph saved to {output_path}")
        logger.info(f"Found {len(graph['dependencies']['static_imports'])} static imports")
        logger.info(f"Found {len(graph['dependencies']['dynamic_imports'])} dynamic imports")
        logger.info(f"Found {len(graph['dependencies']['local_modules'])} local modules")
        logger.info(f"Found {len(graph['dependencies']['external_packages'])} external packages")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error saving dependency graph: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
