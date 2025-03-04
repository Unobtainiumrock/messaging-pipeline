#!/usr/bin/env python3
"""
Run all tests for the Communication Centralizer.
"""
import os
import sys
import subprocess

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("COMMUNICATION CENTRALIZER - TEST SUITE")
    print("=" * 60)
    
    # Get the paths to the test runners
    test_dir = os.path.dirname(os.path.abspath(__file__))
    credential_runner = os.path.join(test_dir, "run_credential_tests.py")
    component_runner = os.path.join(test_dir, "run_component_tests.py")
    
    # Make them executable
    os.chmod(credential_runner, 0o755)
    os.chmod(component_runner, 0o755)
    
    # Run credential tests
    print("\n" + "=" * 60)
    print("RUNNING CREDENTIAL TESTS")
    print("=" * 60)
    credential_result = subprocess.run(["python", credential_runner], capture_output=False)
    
    # Run component tests
    print("\n" + "=" * 60)
    print("RUNNING COMPONENT TESTS")
    print("=" * 60)
    component_result = subprocess.run(["python", component_runner], capture_output=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Credential Tests: {'PASSED' if credential_result.returncode == 0 else 'FAILED'}")
    print(f"Component Tests: {'PASSED' if component_result.returncode == 0 else 'FAILED'}")
    
    all_passed = credential_result.returncode == 0 and component_result.returncode == 0
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Please address the issues before proceeding.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 