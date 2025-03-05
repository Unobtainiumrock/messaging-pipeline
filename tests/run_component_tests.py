#!/usr/bin/env python3
"""
Test script to run all component tests.
"""
import os
import sys
import pytest

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_component_tests():
    """Run all component tests."""
    print("=" * 60)
    print("COMMUNICATION CENTRALIZER - COMPONENT TESTS")
    print("=" * 60)
    
    # Get the path to the component tests directory
    component_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "component"
    )
    
    # Run pytest on the component directory
    result = pytest.main([component_dir, "-v"])
    
    return result == 0  # 0 means all tests passed

if __name__ == "__main__":
    success = run_component_tests()
    sys.exit(0 if success else 1) 