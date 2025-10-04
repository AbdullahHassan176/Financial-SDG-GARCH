#!/usr/bin/env python3
"""
Test Manifests
Validates MANIFEST_REQUIRED.json schema and presence.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_manifest_schema():
    """Test that manifest has required schema."""
    manifest_file = Path("MANIFEST_REQUIRED.json")
    
    if not manifest_file.exists():
        print("❌ MANIFEST_REQUIRED.json not found")
        return False
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest: {e}")
        return False
    
    # Check required fields
    required_fields = ['metadata', 'required_files', 'categories']
    for field in required_fields:
        if field not in manifest:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check metadata fields
    metadata = manifest['metadata']
    required_metadata = ['total_files', 'categories']
    for field in required_metadata:
        if field not in metadata:
            print(f"❌ Missing metadata field: {field}")
            return False
    
    print("✅ Manifest schema test passed")
    return True

def test_manifest_files_exist():
    """Test that all files in manifest exist."""
    manifest_file = Path("MANIFEST_REQUIRED.json")
    
    if not manifest_file.exists():
        print("❌ MANIFEST_REQUIRED.json not found")
        return False
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest: {e}")
        return False
    
    required_files = manifest.get('required_files', [])
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print(f"✅ All {len(required_files)} required files exist")
    return True

def test_manifest_categories():
    """Test that categories are properly structured."""
    manifest_file = Path("MANIFEST_REQUIRED.json")
    
    if not manifest_file.exists():
        print("❌ MANIFEST_REQUIRED.json not found")
        return False
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest: {e}")
        return False
    
    categories = manifest.get('categories', {})
    expected_categories = [
        'source_code', 'configs', 'environment', 'scripts', 
        'data', 'artifacts', 'documentation', 'tests', 'tools'
    ]
    
    for category in expected_categories:
        if category not in categories:
            print(f"❌ Missing category: {category}")
            return False
        
        if not isinstance(categories[category], list):
            print(f"❌ Category {category} is not a list")
            return False
    
    print("✅ Manifest categories test passed")
    return True

def test_manifest_consistency():
    """Test that manifest is internally consistent."""
    manifest_file = Path("MANIFEST_REQUIRED.json")
    
    if not manifest_file.exists():
        print("❌ MANIFEST_REQUIRED.json not found")
        return False
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest: {e}")
        return False
    
    # Check that total_files matches actual count
    total_files = manifest['metadata']['total_files']
    required_files = manifest['required_files']
    
    if total_files != len(required_files):
        print(f"❌ Total files mismatch: metadata says {total_files}, actual {len(required_files)}")
        return False
    
    # Check that category counts match
    metadata_categories = manifest['metadata']['categories']
    categories = manifest['categories']
    
    for category, count in metadata_categories.items():
        if count != len(categories[category]):
            print(f"❌ Category {category} count mismatch: metadata says {count}, actual {len(categories[category])}")
            return False
    
    print("✅ Manifest consistency test passed")
    return True

def main():
    """Run all manifest tests."""
    print("Testing manifests...")
    print("=" * 20)
    
    tests = [
        test_manifest_schema,
        test_manifest_files_exist,
        test_manifest_categories,
        test_manifest_consistency
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ {test.__name__} failed")
    
    print(f"\n✅ Manifest tests: {passed}/{total} passed")
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
