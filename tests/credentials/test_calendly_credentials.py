#!/usr/bin/env python3
"""Tests for Calendly credentials validation."""
import os
import requests
import pytest
import sys
from typing import Optional, Dict, Any, List


def test_calendly_credentials() -> None:
    """Test Calendly API key and user."""
    print("Testing Calendly credentials...")

    # Check environment variables
    api_key: Optional[str] = os.getenv("CALENDLY_API_KEY")
    user: Optional[str] = os.getenv("CALENDLY_USER")

    print(f"- API Key: {'✓ Found' if api_key else '✗ MISSING'}")
    print(f"- Calendly User: {'✓ Found' if user else '✗ MISSING'}")

    if not api_key:
        print("❌ ERROR: Calendly API key missing")
        pytest.skip("Calendly API key not found in environment variables")

    # Test API key format (simple check)
    if api_key:
        assert len(api_key) > 10, "API key seems too short"

    # Test API key with a simple request
    print("\nTesting API key with a request to the Calendly API...")
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        # Get user info to validate API key
        response: requests.Response = requests.get("https://api.calendly.com/users/me", headers=headers)

        assert (
            response.status_code == 200
        ), f"API request failed with status code {response.status_code}: {response.text}"

        data: Dict[str, Any] = response.json()
        print(f"✅ API key is valid! User name: {data.get('resource', {}).get('name', 'unknown')}")

        # Check if retrieved user matches expected user
        calendly_uri: str = data.get("resource", {}).get("uri", "")
        if user and calendly_uri and user not in calendly_uri:
            print(f"⚠️ Warning: Configured user ({user}) doesn't match API key owner ({calendly_uri})")

        # List event types
        print("\nFetching available event types...")
        user_uri: str = data.get("resource", {}).get("uri", "")

        if user_uri:
            event_response: requests.Response = requests.get(
                f"https://api.calendly.com/event_types?user={user_uri}",
                headers=headers,
            )

            if event_response.status_code == 200:
                events: List[Dict[str, Any]] = event_response.json().get("collection", [])
                if events:
                    print(f"✅ Found {len(events)} event types:")
                    for event in events:
                        print(f"  - {event.get('name', 'unknown')} ({event.get('slug', 'unknown')})")
                else:
                    print("⚠️ Warning: No event types found. Create some in your Calendly account.")
            else:
                print(
                    f"⚠️ Warning: Couldn't fetch event types. Status code: {event_response.status_code}"
                )

        print("\n✅ SUCCESS: Calendly credentials are working correctly!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key in the .env file")
        print("2. Make sure your Calendly account is active")
        print("3. Check that you've created at least one event type in Calendly")
        pytest.fail(f"Test failed with exception: {str(e)}")


def run_test() -> bool:
    """Run the test and return boolean result for command line usage."""
    try:
        test_calendly_credentials()
        return True
    except pytest.skip.Exception:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
