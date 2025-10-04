#!/usr/bin/env python3
"""
Artifact Snapshot System
Computes SHA256 hashes for all files in artifacts/ directory.
Creates artifacts_manifest.json with file paths, sizes, hashes, and timestamps.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compute_file_hash(file_path):
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error computing hash for {file_path}: {e}")
        return None

def get_file_info(file_path):
    """Get file information including size, hash, and timestamp."""
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'hash': compute_file_hash(file_path),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return None

def scan_artifacts_directory(artifacts_dir="artifacts"):
    """Scan artifacts directory and create manifest."""
    artifacts_path = Path(artifacts_dir)
    
    if not artifacts_path.exists():
        logger.warning(f"Artifacts directory {artifacts_dir} does not exist")
        return {}
    
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'artifacts_dir': str(artifacts_path.absolute()),
        'files': {}
    }
    
    # Walk through all files in artifacts directory
    for root, dirs, files in os.walk(artifacts_path):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(artifacts_path)
            
            file_info = get_file_info(file_path)
            if file_info:
                manifest['files'][str(relative_path)] = file_info
                logger.info(f"Processed: {relative_path}")
    
    return manifest

def save_manifest(manifest, output_path="artifacts_manifest.json"):
    """Save manifest to JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"Manifest saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving manifest: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Snapshot artifacts with SHA256 hashes")
    parser.add_argument("--artifacts-dir", default="artifacts", 
                       help="Artifacts directory to scan (default: artifacts)")
    parser.add_argument("--output", default="artifacts_manifest.json",
                       help="Output manifest file (default: artifacts_manifest.json)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Scanning artifacts directory: {args.artifacts_dir}")
    
    # Scan artifacts
    manifest = scan_artifacts_directory(args.artifacts_dir)
    
    if not manifest.get('files'):
        logger.warning("No files found in artifacts directory")
        return 1
    
    # Save manifest
    if save_manifest(manifest, args.output):
        logger.info(f"Successfully processed {len(manifest['files'])} files")
        return 0
    else:
        logger.error("Failed to save manifest")
        return 1

if __name__ == "__main__":
    exit(main())
