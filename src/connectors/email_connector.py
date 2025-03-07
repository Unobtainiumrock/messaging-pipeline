"""
Email connector module for interacting with email providers like Gmail and Outlook.

Provides functionality to fetch messages and send replies through a unified interface,
abstracting away the differences between email service providers.
"""
import os
import base64
import logging
import time
import json
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class EmailConnector:
    """Connector for email services (Gmail, Outlook)."""

    def __init__(self) -> None:
        """Initialize the email connector based on configured email type."""
        self.email_type = os.getenv("EMAIL_TYPE", "gmail")
        self.email_username = os.getenv("EMAIL_USERNAME")

        if self.email_type == "gmail":
            self._init_gmail()
        elif self.email_type == "outlook":
            self._init_outlook()
        else:
            raise ValueError(f"Unsupported email type: {self.email_type}")

    def _init_gmail(self) -> None:
        """Initialize Gmail API connection."""
        creds = None
        token_path = "config/credentials/gmail_token.json"
        creds_path = "config/credentials/gmail_credentials.json"

        # Load or refresh credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(token_path).read()),
                ["https://www.googleapis.com/auth/gmail.modify"],
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, ["https://www.googleapis.com/auth/gmail.modify"]
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                token.write(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API initialized successfully")

    def _init_outlook(self) -> None:
        """Initialize Outlook API connection."""
        # Implement Outlook API connection
        # This is a placeholder for Microsoft Graph API integration
        logger.info("Outlook API initialized successfully")

    def fetch_messages(self, days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch messages from the email account.

        Args:
            days_back: Optional number of days to look back for messages

        Returns:
            List of message dictionaries
        """
        try:
            # Get messages from Gmail API
            if days_back is not None:
                # Add query parameter for date range
                query = f"after:{int(time.time() - days_back * 24 * 60 * 60)}"
                messages = self.service.users().messages().list(userId="me", q=query).execute()
            else:
                messages = self.service.users().messages().list(userId="me").execute()

            results = []
            for msg in messages.get("messages", []):
                message_data = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )

                # Process headers to get metadata
                headers = {h["name"]: h["value"] for h in message_data["payload"]["headers"]}

                # Get body
                body = self._get_gmail_body(message_data["payload"])

                # Standardize format
                processed_message = {
                    "id": msg["id"],
                    "source": "gmail",
                    "sender_name": headers.get("From", "").split("<")[0].strip(),
                    "sender_email": self._extract_email(headers.get("From", "")),
                    "timestamp": message_data["internalDate"],
                    "subject": headers.get("Subject", ""),
                    "content": body,
                    "raw_data": message_data,
                }

                results.append(processed_message)

            logger.info(f"Fetched {len(results)} messages from Gmail")
            return results

        except Exception as e:
            logger.error(f"Error fetching Gmail messages: {str(e)}", exc_info=True)
            return []

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        if "<" in from_header and ">" in from_header:
            return from_header.split("<")[1].split(">")[0]
        return from_header

    def _get_gmail_body(self, payload: Dict[str, Any]) -> str:
        """
        Recursively extract the text from a Gmail message payload.

        Args:
            payload: The Gmail message payload

        Returns:
            The message body as text
        """
        if "body" in payload and payload["body"].get("data"):
            # Base case: this part has data
            return base64.urlsafe_b64decode(payload["body"]["data"].encode("ASCII")).decode("utf-8")

        # Recursive case: check parts
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        return base64.urlsafe_b64decode(part["body"]["data"].encode("ASCII")).decode(
                            "utf-8"
                        )

            # If no text/plain, try the first part
            return self._get_gmail_body(payload["parts"][0])

        return ""

    def _fetch_outlook_messages(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch messages from Outlook."""
        # Implement Outlook message fetching
        logger.info("Fetching messages from Outlook (not implemented)")
        return []

    def send_reply(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send a reply email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text

        Returns:
            True if successful, False otherwise
        """
        if self.email_type == "gmail":
            return self._send_gmail_reply(to_email, subject, body)
        elif self.email_type == "outlook":
            return self._send_outlook_reply(to_email, subject, body)
        else:
            return False

    def _send_gmail_reply(self, to_email: str, subject: str, body: str) -> bool:
        """Send a reply via Gmail."""
        try:
            message = MIMEText(body)
            message["to"] = to_email
            message["subject"] = subject

            raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8")).decode("utf-8")

            self.service.users().messages().send(userId="me", body={"raw": raw_message}).execute()

            logger.info(f"Sent reply to {to_email} via Gmail")
            return True

        except Exception as e:
            logger.error(f"Error sending Gmail reply: {str(e)}", exc_info=True)
            return False

    def _send_outlook_reply(self, to_email: str, subject: str, body: str) -> bool:
        """Send a reply via Outlook."""
        # Implement Outlook email sending
        logger.info(f"Sending reply to {to_email} via Outlook (not implemented)")
        return False
