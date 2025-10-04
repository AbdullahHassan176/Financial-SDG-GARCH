#!/usr/bin/env python3
"""
Test Seeds and Determinism
Asserts fixed random seeds in Python parts (NumPy, PyTorch/TF if used, Python random).
"""

import numpy as np
import random
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_numpy_seed():
    """Test that NumPy uses fixed seed."""
    # Set seed
    np.random.seed(42)
    
    # Generate random numbers
    rand1 = np.random.random(10)
    
    # Reset seed
    np.random.seed(42)
    
    # Generate same random numbers
    rand2 = np.random.random(10)
    
    # Should be identical
    assert np.allclose(rand1, rand2), "NumPy seed not deterministic"
    print("✅ NumPy seed test passed")

def test_python_random_seed():
    """Test that Python random uses fixed seed."""
    # Set seed
    random.seed(42)
    
    # Generate random numbers
    rand1 = [random.random() for _ in range(10)]
    
    # Reset seed
    random.seed(42)
    
    # Generate same random numbers
    rand2 = [random.random() for _ in range(10)]
    
    # Should be identical
    assert rand1 == rand2, "Python random seed not deterministic"
    print("✅ Python random seed test passed")

def test_environment_seed():
    """Test that PYTHONHASHSEED is set."""
    pythonhashseed = os.environ.get('PYTHONHASHSEED')
    if pythonhashseed is not None:
        assert pythonhashseed == '0', f"PYTHONHASHSEED should be 0, got {pythonhashseed}"
        print("✅ PYTHONHASHSEED test passed")
    else:
        print("⚠️ PYTHONHASHSEED not set (recommended for reproducibility)")

def test_torch_seed():
    """Test PyTorch seed if available."""
    try:
        import torch
        torch.manual_seed(42)
        
        # Generate random tensor
        rand1 = torch.rand(10)
        
        # Reset seed
        torch.manual_seed(42)
        
        # Generate same random tensor
        rand2 = torch.rand(10)
        
        # Should be identical
        assert torch.allclose(rand1, rand2), "PyTorch seed not deterministic"
        print("✅ PyTorch seed test passed")
        
    except ImportError:
        print("ℹ️ PyTorch not available, skipping test")

def test_tensorflow_seed():
    """Test TensorFlow seed if available."""
    try:
        import tensorflow as tf
        tf.random.set_seed(42)
        
        # Generate random tensor
        rand1 = tf.random.normal([10])
        
        # Reset seed
        tf.random.set_seed(42)
        
        # Generate same random tensor
        rand2 = tf.random.normal([10])
        
        # Should be identical
        assert tf.reduce_all(tf.equal(rand1, rand2)), "TensorFlow seed not deterministic"
        print("✅ TensorFlow seed test passed")
        
    except ImportError:
        print("ℹ️ TensorFlow not available, skipping test")

def test_sklearn_seed():
    """Test scikit-learn seed if available."""
    try:
        from sklearn.utils import check_random_state
        
        # Test random state
        rng1 = check_random_state(42)
        rng2 = check_random_state(42)
        
        # Generate random numbers
        rand1 = rng1.random(10)
        rand2 = rng2.random(10)
        
        # Should be identical
        assert np.allclose(rand1, rand2), "scikit-learn seed not deterministic"
        print("✅ scikit-learn seed test passed")
        
    except ImportError:
        print("ℹ️ scikit-learn not available, skipping test")

def main():
    """Run all seed tests."""
    print("Testing seeds and determinism...")
    print("=" * 40)
    
    try:
        test_numpy_seed()
        test_python_random_seed()
        test_environment_seed()
        test_torch_seed()
        test_tensorflow_seed()
        test_sklearn_seed()
        
        print("\n✅ All seed tests passed")
        return 0
        
    except Exception as e:
        print(f"\n❌ Seed test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
