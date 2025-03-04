 #!/usr/bin/env python3
"""
Test script to verify Google Sheets access is configured correctly.
"""
import os
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Load environment variables
load_dotenv()

def test_google_sheets_access():
    """Test Google Sheets access with current configuration."""
    print("Testing Google Sheets connectivity...")
    
    # Get configuration
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 
                                'config/credentials/google_credentials.json')
    
    # Verify environment variables
    print(f"- Sheet ID: {'✓ Found' if sheet_id else '✗ MISSING'}")
    print(f"- Credentials path: {credentials_path}")
    print(f"  Credentials file exists: {'✓ Yes' if os.path.exists(credentials_path) else '✗ NO'}")
    
    try:
        # Authenticate
        print("\nAttempting to authenticate...")
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        client = gspread.authorize(credentials)
        print("✓ Authentication successful!")
        
        # Try to access the spreadsheet
        print(f"\nAttempting to access spreadsheet with ID: {sheet_id}...")
        sheet = client.open_by_key(sheet_id)
        print(f"✓ Successfully opened spreadsheet: '{sheet.title}'")
        
        # List worksheets
        worksheets = sheet.worksheets()
        print(f"\nWorksheets in this spreadsheet:")
        for ws in worksheets:
            print(f"- {ws.title} ({ws.row_count}x{ws.col_count})")
        
        # Add a test entry to verify write access
        print("\nAdding a test entry to verify write access...")
        if "Messages" in [ws.title for ws in worksheets]:
            messages_sheet = sheet.worksheet("Messages")
            
            # Check if we have headers
            headers = messages_sheet.row_values(1)
            if not headers or len(headers) < 3:
                print("Adding headers to Messages worksheet...")
                headers = ["ID", "Source", "Timestamp", "Message", "Test"]
                messages_sheet.append_row(headers)
            
            # Add test row
            test_id = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            test_row = [
                test_id,
                "test_script",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "This is a test entry to verify write access.",
                "Please delete me"
            ]
            messages_sheet.append_row(test_row)
            print(f"✓ Successfully added test entry with ID: {test_id}")
        else:
            print("! No 'Messages' worksheet found. You may need to initialize worksheets.")
        
        print("\n✅ SUCCESS: Google Sheets integration is working correctly!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your credentials JSON file is correctly formatted")
        print("2. Make sure you've shared the spreadsheet with the service account email")
        print("3. Check that you've enabled the Google Sheets and Google Drive APIs")
        print("4. Ensure your Sheet ID is correct")
        return False
        
    return True

if __name__ == "__main__":
    test_google_sheets_access()