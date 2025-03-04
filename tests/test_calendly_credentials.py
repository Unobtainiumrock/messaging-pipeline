#!/usr/bin/env python3
"""
Test script to verify Calendly API credentials.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_calendly_credentials():
    """Test Calendly API key and user."""
    print("Testing Calendly credentials...")
    
    # Check environment variables
    api_key = os.getenv('CALENDLY_API_KEY')
    user = os.getenv('CALENDLY_USER')
    
    print(f"- API Key: {'✓ Found' if api_key else '✗ MISSING'}")
    print(f"- Calendly User: {'✓ Found' if user else '✗ MISSING'}")
    
    if not api_key:
        print("❌ ERROR: Calendly API key missing")
        return False
    
    # Test API key with a simple request
    print("\nTesting API key with a request to the Calendly API...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get user info to validate API key
        response = requests.get(
            "https://api.calendly.com/users/me",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API key is valid! User name: {data.get('resource', {}).get('name', 'unknown')}")
            
            # Check if retrieved user matches expected user
            calendly_uri = data.get('resource', {}).get('uri', '')
            if user and calendly_uri and user not in calendly_uri:
                print(f"⚠️ Warning: Configured user ({user}) doesn't match API key owner ({calendly_uri})")
            
            # List event types
            print("\nFetching available event types...")
            user_uri = data.get('resource', {}).get('uri', '')
            
            if user_uri:
                event_response = requests.get(
                    f"https://api.calendly.com/event_types?user={user_uri}",
                    headers=headers
                )
                
                if event_response.status_code == 200:
                    events = event_response.json().get('collection', [])
                    if events:
                        print(f"✅ Found {len(events)} event types:")
                        for event in events:
                            print(f"  - {event.get('name', 'unknown')} ({event.get('slug', 'unknown')})")
                    else:
                        print("⚠️ Warning: No event types found. Create some in your Calendly account.")
                else:
                    print(f"⚠️ Warning: Couldn't fetch event types. Status code: {event_response.status_code}")
            
        else:
            print(f"❌ API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("\n✅ SUCCESS: Calendly credentials are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key in the .env file")
        print("2. Make sure your Calendly account is active")
        print("3. Check that you've created at least one event type in Calendly")
        return False

if __name__ == "__main__":
    test_calendly_credentials() 