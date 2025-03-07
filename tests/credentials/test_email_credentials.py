#!/usr/bin/env python3
"""Test script to verify email credentials are configured correctly."""
import os
import imaplib
import smtplib
import sys
import pytest
from typing import Optional, List
from tests.conftest import print_env_vars


def test_email_credentials() -> None:
    """Test email credentials for IMAP and SMTP access."""
    print("Testing Email credentials...")

    # Print environment variables to debug
    print_env_vars()

    # Check environment variables
    email_type: str = os.getenv("EMAIL_TYPE", "").lower()
    email_username: Optional[str] = os.getenv("EMAIL_USERNAME")
    email_password: Optional[str] = os.getenv("EMAIL_PASSWORD")

    print(f"- Email type: {email_type if email_type else '✗ MISSING'}")
    print(f"- Email username: {'✓ Found' if email_username else '✗ MISSING'}")
    print(f"- Email password: {'✓ Found' if email_password else '✗ MISSING'}")

    if not all([email_type, email_username, email_password]):
        print("❌ ERROR: Missing required email environment variables")
        pytest.skip("Email credentials not found in environment variables")

    # Set up connection details based on email type
    imap_server_host: str = ""
    smtp_server_host: str = ""
    smtp_port_num: int = 0

    if email_type == "gmail":
        imap_server_host = "imap.gmail.com"
        smtp_server_host = "smtp.gmail.com"
        smtp_port_num = 587
    elif email_type == "outlook":
        imap_server_host = "outlook.office365.com"
        smtp_server_host = "smtp.office365.com"
        smtp_port_num = 587
    else:
        print(f"❌ ERROR: Unsupported email type '{email_type}'. Must be 'gmail' or 'outlook'")
        pytest.skip("Unsupported email type")

    # Test IMAP connection
    print(f"\nTesting IMAP connection to {imap_server_host}...")
    try:
        mail: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL(imap_server_host)
        if email_username is None or email_password is None:
            raise ValueError("Username or password is missing")
        mail.login(email_username, email_password)
        print("✅ IMAP authentication successful!")
        mail.select("INBOX")
        messages: List[bytes]
        status, messages = mail.search(None, "ALL")  # Correctly typed tuple unpacking
        message_count: int = len(messages[0].split())
        print(f"  Found {message_count} messages in inbox")
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"❌ IMAP Error: {str(e)}")
        print("\nTroubleshooting tips for Gmail:")
        print("1. Make sure you've enabled IMAP in Gmail settings")
        print("2. If using Gmail, you need an App Password if 2FA is enabled")
        print("3. Check your credentials in the .env file")
        pytest.fail("IMAP authentication failed")

    # Test SMTP connection
    print(f"\nTesting SMTP connection to {smtp_server_host}:{smtp_port_num}...")
    try:
        server: smtplib.SMTP = smtplib.SMTP(smtp_server_host, smtp_port_num)
        server.ehlo()
        server.starttls()
        if email_username is None or email_password is None:
            raise ValueError("Username or password is missing")
        server.login(email_username, email_password)
        print("✅ SMTP authentication successful!")
        server.quit()
    except Exception as e:
        print(f"❌ SMTP Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you've allowed less secure apps or created an App Password")
        print("2. Check your credentials in the .env file")
        pytest.fail("SMTP authentication failed")

    print("\n✅ SUCCESS: Email credentials are working correctly!")


def run_test() -> bool:
    """Run the test and return boolean result for command line usage."""
    try:
        test_email_credentials()
        return True
    except pytest.skip.Exception:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
