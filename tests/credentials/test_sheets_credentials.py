#!/usr/bin/env python3
"""Test Google Sheets access with current configuration."""
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys
import pytest
from typing import Optional, List


def test_sheets_credentials() -> None:
    """Test Google Sheets access with current configuration."""
    print("Testing Google Sheets connectivity...")

    # Get configuration
    sheet_id: Optional[str] = os.getenv("GOOGLE_SHEET_ID")
    credentials_path: str = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "config/credentials/google_credentials.json"
    )

    # Verify environment variables
    print(f"- Sheet ID: {'✓ Found' if sheet_id else '✗ MISSING'}")
    print(f"- Credentials path: {credentials_path}")
    print(f"  Credentials file exists: {'✓ Yes' if os.path.exists(credentials_path) else '✗ NO'}")

    if not (credentials_path and os.path.exists(credentials_path)):
        print("❌ ERROR: Google Sheets credentials file missing")
        pytest.skip("Google Sheets credentials file not found")

    try:
        # Authenticate
        print("\nAttempting to authenticate...")
        scopes: List[str] = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials: Credentials = Credentials.from_service_account_file(
            credentials_path, scopes=scopes
        )
        client: gspread.Client = gspread.authorize(credentials)
        print("✓ Authentication successful!")

        # Try to access the spreadsheet
        print(f"\nAttempting to access spreadsheet with ID: {sheet_id}...")
        sheet: gspread.Spreadsheet = client.open_by_key(sheet_id)
        print(f"✓ Successfully opened spreadsheet: '{sheet.title}'")

        # List worksheets
        worksheets: List[gspread.Worksheet] = sheet.worksheets()
        print("\nWorksheets in this spreadsheet:")
        for ws in worksheets:
            print(f"- {ws.title} ({ws.row_count}x{ws.col_count})")

        # Add a test entry to verify write access
        print("\nAdding a test entry to verify write access...")
        if "Messages" in [ws.title for ws in worksheets]:
            messages_sheet: gspread.Worksheet = sheet.worksheet("Messages")

            # Check if we have headers
            headers: List[str] = messages_sheet.row_values(1)
            if not headers or len(headers) < 3:
                print("Adding headers to Messages worksheet...")
                headers = ["ID", "Source", "Timestamp", "Message", "Test"]
                messages_sheet.append_row(headers)

            # Add test row
            test_id: str = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            test_row: List[str] = [
                test_id,
                "test_script",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "This is a test entry to verify write access.",
                "Please delete me",
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
        pytest.fail(f"Test failed with exception: {str(e)}")


def run_test() -> bool:
    """Run the test and return boolean result for command line usage."""
    try:
        test_sheets_credentials()
        return True
    except pytest.skip.Exception:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
