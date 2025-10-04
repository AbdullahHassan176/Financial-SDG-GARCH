#!/usr/bin/env python3
"""
Archive Non-Essential Files
Reads MANIFEST_REQUIRED.json and moves non-essential files to /archive/.
Maintains folder structure and creates archive/README.md.
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Set, List, Dict
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArchiveManager:
    """Manager for archiving non-essential files."""
    
    def __init__(self, manifest_file="MANIFEST_REQUIRED.json"):
        self.manifest_file = Path(manifest_file)
        self.required_files = set()
        self.archive_plan = []
        self.dry_run = True
    
    def load_manifest(self):
        """Load required files manifest."""
        if not self.manifest_file.exists():
            logger.error(f"Manifest file {self.manifest_file} not found")
            return False
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            self.required_files = set(manifest.get('required_files', []))
            logger.info(f"Loaded {len(self.required_files)} required files from manifest")
            return True
            
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return False
    
    def should_archive_file(self, file_path):
        """Check if file should be archived."""
        file_path = Path(file_path)
        
        # Skip if file is required
        if str(file_path) in self.required_files:
            return False
        
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 
                    'venv', '.venv', 'archive', 'build', 'expected'}
        
        for part in file_path.parts:
            if part in skip_dirs:
                return False
        
        # Skip certain file types
        skip_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.log'}
        if file_path.suffix in skip_extensions:
            return False
        
        # Skip temporary files
        if file_path.name.startswith('.') and file_path.name not in {'.gitignore', '.pre-commit-config.yaml'}:
            return False
        
        return True
    
    def find_files_to_archive(self):
        """Find all files that should be archived."""
        logger.info("Scanning for files to archive")
        
        files_to_archive = []
        
        # Walk through all files
        for file_path in Path(".").rglob("*"):
            if file_path.is_file() and self.should_archive_file(file_path):
                files_to_archive.append(file_path)
        
        logger.info(f"Found {len(files_to_archive)} files to archive")
        return files_to_archive
    
    def create_archive_plan(self, files_to_archive):
        """Create archive plan with folder structure preservation."""
        logger.info("Creating archive plan")
        
        archive_plan = []
        
        for file_path in files_to_archive:
            # Create archive path preserving folder structure
            archive_path = Path("archive") / file_path
            
            # Ensure archive directory exists
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            archive_plan.append({
                'source': str(file_path),
                'destination': str(archive_path),
                'size': file_path.stat().st_size if file_path.exists() else 0
            })
        
        self.archive_plan = archive_plan
        return archive_plan
    
    def save_archive_plan(self, plan_file="build/archive_plan.txt"):
        """Save archive plan to file."""
        plan_path = Path(plan_file)
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write("Archive Plan for Non-Essential Files\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Total files to archive: {len(self.archive_plan)}\n")
                f.write(f"Total size: {sum(item['size'] for item in self.archive_plan)} bytes\n\n")
                
                f.write("Files to be archived:\n")
                f.write("-" * 20 + "\n")
                for item in self.archive_plan:
                    f.write(f"{item['source']} -> {item['destination']}\n")
            
            logger.info(f"Archive plan saved to {plan_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving archive plan: {e}")
            return False
    
    def execute_archive(self):
        """Execute the archive plan."""
        if self.dry_run:
            logger.info("Dry run mode - no files will be moved")
            return True
        
        logger.info("Executing archive plan")
        
        moved_files = 0
        errors = 0
        
        for item in self.archive_plan:
            source_path = Path(item['source'])
            dest_path = Path(item['destination'])
            
            try:
                if source_path.exists():
                    # Create destination directory
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(source_path), str(dest_path))
                    moved_files += 1
                    logger.info(f"Moved: {source_path} -> {dest_path}")
                else:
                    logger.warning(f"Source file not found: {source_path}")
                    
            except Exception as e:
                logger.error(f"Error moving {source_path}: {e}")
                errors += 1
        
        logger.info(f"Archive complete: {moved_files} files moved, {errors} errors")
        return errors == 0
    
    def create_archive_readme(self):
        """Create README.md for archive directory."""
        readme_path = Path("archive/README.md")
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("# Archive Directory\n\n")
                f.write("This directory contains non-essential files that were moved during the repository clean room process.\n\n")
                f.write("## Contents\n\n")
                f.write("The following types of files were archived:\n")
                f.write("- Temporary files and logs\n")
                f.write("- Development artifacts\n")
                f.write("- Non-essential documentation\n")
                f.write("- Backup files\n")
                f.write("- Old versions of files\n\n")
                f.write("## Restoration\n\n")
                f.write("If you need to restore any files from this archive, you can move them back to their original locations.\n\n")
                f.write("## Archive Plan\n\n")
                f.write("The original archive plan was saved to `build/archive_plan.txt`.\n")
            
            logger.info("Created archive/README.md")
            return True
            
        except Exception as e:
            logger.error(f"Error creating archive README: {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Archive non-essential files")
    parser.add_argument("--manifest", default="MANIFEST_REQUIRED.json",
                       help="Manifest file (default: MANIFEST_REQUIRED.json)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Dry run mode (default: True)")
    parser.add_argument("--execute", action="store_true",
                       help="Execute archive (overrides --dry-run)")
    parser.add_argument("--plan-file", default="build/archive_plan.txt",
                       help="Archive plan file (default: build/archive_plan.txt)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine if dry run
    dry_run = args.dry_run and not args.execute
    
    logger.info("Starting archive process")
    logger.info(f"Manifest file: {args.manifest}")
    logger.info(f"Dry run: {dry_run}")
    
    # Create archive manager
    manager = ArchiveManager(args.manifest)
    manager.dry_run = dry_run
    
    # Load manifest
    if not manager.load_manifest():
        return 1
    
    # Find files to archive
    files_to_archive = manager.find_files_to_archive()
    
    if not files_to_archive:
        logger.info("No files to archive")
        return 0
    
    # Create archive plan
    archive_plan = manager.create_archive_plan(files_to_archive)
    
    # Save plan
    if not manager.save_archive_plan(args.plan_file):
        return 1
    
    # Execute archive if not dry run
    if not dry_run:
        if manager.execute_archive():
            manager.create_archive_readme()
            logger.info("✅ Archive complete")
            return 0
        else:
            logger.error("❌ Archive failed")
            return 1
    else:
        logger.info("✅ Archive plan created - use --execute to move files")
        return 0

if __name__ == "__main__":
    exit(main())
