#!/usr/bin/env python3
"""Test script to verify Slack API credentials."""
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import sys
import pytest
from typing import Optional, Dict, Any, List


def test_slack_credentials() -> None:
    """Test Slack Bot Token."""
    print("Testing Slack credentials...")

    # Check environment variables
    bot_token: Optional[str] = os.getenv("SLACK_BOT_TOKEN")

    print(f"- Bot Token: {'✓ Found' if bot_token else '✗ MISSING'}")

    if not bot_token:
        print("❌ ERROR: Slack Bot token missing")
        pytest.skip("Slack Bot token not found in environment variables")

    # Test token with a simple request
    print("\nTesting connection to Slack API...")
    client: WebClient = WebClient(token=bot_token)

    try:
        # Test auth to verify token
        response: Dict[str, Any] = client.auth_test()

        if response["ok"]:
            print("✅ Authentication successful!")
            print(f"  - Bot Name: {response.get('user', 'unknown')}")
            print(f"  - Team: {response.get('team', 'unknown')}")

            # Test listing channels
            channels_response: Dict[str, Any] = client.conversations_list(types="public_channel")
            channels: List[Dict[str, Any]] = channels_response.get("channels", [])

            if channels:
                print(f"\nFound {len(channels)} channels. First few:")
                for i, channel in enumerate(channels[:5]):
                    print(f"  - #{channel.get('name', 'unknown')}")
                    if i >= 4:
                        break
            else:
                print("\nNo channels found, or bot doesn't have permission to list channels.")

            print("\n✅ SUCCESS: Slack credentials are working correctly!")
        else:
            print(f"❌ Authentication failed: {response.get('error', 'Unknown error')}")
            pytest.fail(f"Authentication failed: {response.get('error', 'Unknown error')}")

    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        print("\nTroubleshooting tips:")
        print("1. Verify your bot token in the .env file")
        print("2. Make sure your Slack app has the necessary scopes:")
        print("   - channels:read")
        print("   - chat:write")
        print("   - im:read")
        print("   - im:write")
        print("3. Check that your bot has been added to your workspace")
        pytest.fail(f"Slack API Error: {e.response['error']}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        pytest.fail(f"Test failed with exception: {str(e)}")


def run_test() -> bool:
    """Run the test and return boolean result for command line usage."""
    try:
        test_slack_credentials()
        return True
    except pytest.skip.Exception:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
