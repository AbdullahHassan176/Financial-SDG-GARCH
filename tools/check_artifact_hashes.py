#!/usr/bin/env python3
"""
Artifact Hash Checker
Compares current artifacts_manifest.json against expected baseline.
Warns on differences but does not fail (for flexibility).
"""

import json
import argparse
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArtifactHashChecker:
    """Checker for artifact hash consistency."""
    
    def __init__(self):
        self.warnings = []
        self.differences = []
    
    def compare_manifests(self, current_manifest, expected_manifest):
        """Compare current and expected manifests."""
        logger.info("Comparing artifact manifests")
        
        # Compare file lists
        current_files = set(current_manifest.get('files', {}).keys())
        expected_files = set(expected_manifest.get('files', {}).keys())
        
        # Files in current but not expected
        new_files = current_files - expected_files
        if new_files:
            self.warnings.append(f"New files found: {sorted(new_files)}")
        
        # Files in expected but not current
        missing_files = expected_files - current_files
        if missing_files:
            self.warnings.append(f"Missing files: {sorted(missing_files)}")
        
        # Compare common files
        common_files = current_files & expected_files
        for file_path in sorted(common_files):
            current_info = current_manifest['files'][file_path]
            expected_info = expected_manifest['files'][file_path]
            
            # Compare hash
            if current_info.get('hash') != expected_info.get('hash'):
                self.differences.append(f"{file_path}: Hash changed")
            
            # Compare size
            if current_info.get('size') != expected_info.get('size'):
                self.differences.append(f"{file_path}: Size changed ({current_info.get('size')} vs {expected_info.get('size')})")
        
        return len(self.warnings) == 0 and len(self.differences) == 0
    
    def load_manifest(self, manifest_path):
        """Load manifest from JSON file."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading manifest {manifest_path}: {e}")
            return None
    
    def check_artifacts(self, current_manifest_path="artifacts_manifest.json", 
                       expected_manifest_path="expected/artifacts_manifest.json"):
        """Check artifacts against expected baseline."""
        logger.info(f"Loading current manifest: {current_manifest_path}")
        current_manifest = self.load_manifest(current_manifest_path)
        if current_manifest is None:
            return False
        
        logger.info(f"Loading expected manifest: {expected_manifest_path}")
        expected_manifest = self.load_manifest(expected_manifest_path)
        if expected_manifest is None:
            logger.warning("No expected manifest found - this is normal for first run")
            return True
        
        # Compare manifests
        return self.compare_manifests(current_manifest, expected_manifest)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check artifact hashes against baseline")
    parser.add_argument("--current", default="artifacts_manifest.json",
                       help="Current manifest file (default: artifacts_manifest.json)")
    parser.add_argument("--baseline", default="expected/artifacts_manifest.json",
                       help="Expected manifest file (default: expected/artifacts_manifest.json)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting artifact hash check")
    
    checker = ArtifactHashChecker()
    
    # Perform check
    passed = checker.check_artifacts(args.current, args.baseline)
    
    # Report results
    if checker.warnings:
        logger.warning("Warnings found:")
        for warning in checker.warnings:
            logger.warning(f"  - {warning}")
    
    if checker.differences:
        logger.warning("Differences found:")
        for diff in checker.differences:
            logger.warning(f"  - {diff}")
    
    if passed:
        logger.info("✅ Artifact hash check passed")
        return 0
    else:
        logger.warning("⚠️ Artifact hash check found differences (non-fatal)")
        return 0  # Non-fatal as per requirements

if __name__ == "__main__":
    exit(main())
