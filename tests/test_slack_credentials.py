#!/usr/bin/env python3
"""
Test script to verify Slack API credentials.
"""
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

def test_slack_credentials():
    """Test Slack Bot Token."""
    print("Testing Slack credentials...")
    
    # Check environment variables
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    
    print(f"- Bot Token: {'✓ Found' if bot_token else '✗ MISSING'}")
    
    if not bot_token:
        print("❌ ERROR: Slack Bot Token missing")
        return False
    
    # Test token with a simple request
    print("\nTesting connection to Slack API...")
    client = WebClient(token=bot_token)
    
    try:
        # Test auth to verify token
        response = client.auth_test()
        
        if response['ok']:
            print(f"✅ Authentication successful!")
            print(f"  - Bot Name: {response.get('user', 'unknown')}")
            print(f"  - Team: {response.get('team', 'unknown')}")
            
            # Test listing channels
            channels_response = client.conversations_list(types="public_channel")
            channels = channels_response.get('channels', [])
            
            if channels:
                print(f"\nFound {len(channels)} channels. First few:")
                for i, channel in enumerate(channels[:5]):
                    print(f"  - #{channel.get('name', 'unknown')}")
                    if i >= 4:
                        break
            else:
                print("\nNo channels found, or bot doesn't have permission to list channels.")
            
            print("\n✅ SUCCESS: Slack credentials are working correctly!")
            return True
            
        else:
            print(f"❌ Authentication failed: {response.get('error', 'Unknown error')}")
            return False
        
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
        return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_slack_credentials() 