#!/usr/bin/env python3
"""
Test script to verify email credentials are configured correctly.
"""
import os
from dotenv import load_dotenv
import imaplib
import smtplib

# Load environment variables
load_dotenv()

def test_email_credentials():
    """Test email credentials for IMAP and SMTP access."""
    print("Testing Email credentials...")
    
    # Check environment variables
    email_type = os.getenv('EMAIL_TYPE', '').lower()
    email_username = os.getenv('EMAIL_USERNAME')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"- Email type: {email_type if email_type else '✗ MISSING'}")
    print(f"- Email username: {'✓ Found' if email_username else '✗ MISSING'}")
    print(f"- Email password: {'✓ Found' if email_password else '✗ MISSING'}")
    
    if not all([email_type, email_username, email_password]):
        print("❌ ERROR: Missing required email environment variables")
        return False
    
    # Set up connection details based on email type
    if email_type == 'gmail':
        imap_server = 'imap.gmail.com'
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
    elif email_type == 'outlook':
        imap_server = 'outlook.office365.com'
        smtp_server = 'smtp.office365.com'
        smtp_port = 587
    else:
        print(f"❌ ERROR: Unsupported email type '{email_type}'. Must be 'gmail' or 'outlook'")
        return False
    
    # Test IMAP connection
    print(f"\nTesting IMAP connection to {imap_server}...")
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_username, email_password)
        print("✅ IMAP authentication successful!")
        mail.select('INBOX')
        status, messages = mail.search(None, 'ALL')
        message_count = len(messages[0].split())
        print(f"  Found {message_count} messages in inbox")
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"❌ IMAP Error: {str(e)}")
        print("\nTroubleshooting tips for Gmail:")
        print("1. Make sure you've enabled IMAP in Gmail settings")
        print("2. If using Gmail, you need an App Password if 2FA is enabled")
        print("3. Check your credentials in the .env file")
        return False
    
    # Test SMTP connection
    print(f"\nTesting SMTP connection to {smtp_server}:{smtp_port}...")
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(email_username, email_password)
        print("✅ SMTP authentication successful!")
        server.quit()
    except Exception as e:
        print(f"❌ SMTP Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you've allowed less secure apps or created an App Password")
        print("2. Check your credentials in the .env file")
        return False
    
    print("\n✅ SUCCESS: Email credentials are working correctly!")
    return True

if __name__ == "__main__":
    test_email_credentials() 