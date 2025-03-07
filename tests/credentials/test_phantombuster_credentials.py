#!/usr/bin/env python3
"""Test script to verify PhantomBuster API credentials."""
import os
import requests
import pytest
import sys


def test_phantombuster_credentials():
    """Test PhantomBuster API key and agent ID."""
    print("Testing PhantomBuster credentials...")

    # Check environment variables
    api_key = os.getenv("PHANTOMBUSTER_API_KEY")
    agent_id = os.getenv("PHANTOMBUSTER_MESSAGE_AGENT_ID")

    print(f"- API Key: {'✓ Found' if api_key else '✗ MISSING'}")
    print(f"- Agent ID: {'✓ Found' if agent_id else '✗ MISSING'}")

    if not api_key:
        print("❌ ERROR: PhantomBuster API key missing")
        pytest.skip("PhantomBuster API key not found in environment variables")

    # Test API key with a simple request
    print("\nTesting API key with a request to the PhantomBuster API...")
    headers = {"X-Phantombuster-Key": api_key, "Content-Type": "application/json"}

    try:
        # Get account info as a simple validation
        response = requests.get("https://api.phantombuster.com/api/v1/user", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API key is valid! Account email: {data.get('email', 'unknown')}")
        else:
            print(f"❌ API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            pytest.fail(f"API request failed with status code {response.status_code}")

        # If agent ID is provided, check if it exists
        if agent_id:
            print(f"\nChecking agent with ID {agent_id}...")
            response = requests.get(
                f"https://api.phantombuster.com/api/v1/agent/{agent_id}",
                headers=headers,
            )

            if response.status_code == 200:
                agent_data = response.json()
                print(f"✅ Agent exists! Name: {agent_data.get('name', 'unknown')}")
            else:
                print(f"❌ Agent check failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                pytest.fail(f"Agent check failed with status code {response.status_code}")

        print("\n✅ SUCCESS: PhantomBuster credentials are working correctly!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key in the .env file")
        print("2. Check your internet connection")
        print("3. Make sure your PhantomBuster account is active")
        pytest.fail(f"Test failed with exception: {str(e)}")


def run_test() -> bool:
    """Run the test and return boolean result for command line usage."""
    try:
        test_phantombuster_credentials()
        return True
    except pytest.skip.Exception:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
