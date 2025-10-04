#!/usr/bin/env python3
"""
Test Metrics Baseline
Invokes the regression checker to validate metrics against baseline.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_regression_check():
    """Test regression check against baseline."""
    try:
        from tools.check_regression import main as regression_main
        
        # Run regression check
        result = regression_main()
        
        if result == 0:
            print("✅ Regression check passed")
            return True
        else:
            print("❌ Regression check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running regression check: {e}")
        return False

def test_baseline_exists():
    """Test that baseline file exists."""
    baseline_file = Path("expected/metrics_baseline.csv")
    
    if not baseline_file.exists():
        print("❌ Baseline file expected/metrics_baseline.csv not found")
        return False
    
    print("✅ Baseline file exists")
    return True

def test_current_metrics_exist():
    """Test that current metrics directory exists."""
    metrics_dir = Path("outputs/standardized")
    
    if not metrics_dir.exists():
        print("❌ Current metrics directory outputs/standardized not found")
        return False
    
    # Check for some metric files
    metric_files = list(metrics_dir.glob("*.csv")) + list(metrics_dir.glob("*.xlsx"))
    
    if not metric_files:
        print("❌ No metric files found in outputs/standardized")
        return False
    
    print(f"✅ Found {len(metric_files)} metric files")
    return True

def test_artifact_hashes():
    """Test artifact hash check."""
    try:
        from tools.check_artifact_hashes import main as hash_main
        
        # Run artifact hash check
        result = hash_main()
        
        if result == 0:
            print("✅ Artifact hash check passed")
            return True
        else:
            print("❌ Artifact hash check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running artifact hash check: {e}")
        return False

def main():
    """Run all metrics baseline tests."""
    print("Testing metrics baseline...")
    print("=" * 30)
    
    tests = [
        test_baseline_exists,
        test_current_metrics_exist,
        test_regression_check,
        test_artifact_hashes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ {test.__name__} failed")
    
    print(f"\n✅ Metrics baseline tests: {passed}/{total} passed")
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
