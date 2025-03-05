#!/usr/bin/env python3
"""
Test script to verify all credentials for the Communication Centralizer.
"""
import os
import sys
import importlib.util

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def import_test_module(name):
    """Import a test module by name."""
    module_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        f"credentials/test_{name}_credentials.py"  # Updated path
    )
    
    if not os.path.exists(module_path):
        print(f"⚠️ Warning: Test module for {name} not found at {module_path}")
        return None
    
    spec = importlib.util.spec_from_file_location(f"test_{name}_credentials", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    """Run all credential tests."""
    print("=" * 60)
    print("COMMUNICATION CENTRALIZER - CREDENTIAL VERIFICATION")
    print("=" * 60)
    
    # List of integrations to test
    integrations = [
        "sheets", 
        "email", 
        "phantombuster",
        "calendly", 
        "slack", 
        "discord",
        "openai"
    ]
    
    results = {}
    
    for integration in integrations:
        print("\n" + "=" * 60)
        print(f"TESTING {integration.upper()} CREDENTIALS")
        print("=" * 60)
        
        # Import dynamic test module
        test_module = import_test_module(integration)
        if test_module is None:
            results[integration] = "SKIPPED (no test found)"
            continue
        
        # Get the test function
        test_function_name = f"test_{integration}_credentials"
        test_function = getattr(test_module, test_function_name, None)
        
        if test_function is None:
            print(f"⚠️ Warning: Test function {test_function_name} not found in module")
            results[integration] = "SKIPPED (no test function found)"
            continue
        
        # Run the test
        try:
            success = test_function()
            results[integration] = "PASSED" if success else "FAILED"
        except Exception as e:
            print(f"❌ ERROR running test: {str(e)}")
            results[integration] = f"ERROR: {str(e)}"
    
    # Print summary
    print("\n" + "=" * 60)
    print("CREDENTIAL VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for integration, result in results.items():
        status_symbol = "✅" if result == "PASSED" else "❌"
        print(f"{status_symbol} {integration.upper()}: {result}")
        if result != "PASSED":
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CREDENTIALS VERIFIED SUCCESSFULLY!")
    else:
        print("⚠️ SOME CREDENTIAL VERIFICATIONS FAILED")
        print("Please address the issues above before proceeding.")
    print("=" * 60)

if __name__ == "__main__":
    main() 