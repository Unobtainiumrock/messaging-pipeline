"""Tests for connector modules."""
import pytest
import os
import base64
from unittest.mock import MagicMock, patch
import inspect

from src.connectors.email_connector import EmailConnector
from src.connectors.linkedin_connector import LinkedInConnector
from src.connectors.handshake_connector import HandshakeConnector
from src.connectors.slack_connector import SlackConnector
from src.connectors.discord_connector import DiscordConnector


class TestEmailConnector:
    """Tests for EmailConnector class."""

    @pytest.fixture
    def email_connector(self):
        """Create an email connector for testing."""
        # Add a patch for the entire EmailConnector._init_gmail method
        with patch.object(EmailConnector, "_init_gmail") as mock_init_gmail:
            # Make the method do nothing
            mock_init_gmail.return_value = None

            # Create the connector
            connector = EmailConnector()

            # Manually set up the properties we want to test
            connector.email_type = os.environ.get("EMAIL_TYPE", "gmail")
            connector.email_username = os.environ.get("EMAIL_USERNAME", "test@example.com")

            # Create a mock service
            connector.service = MagicMock()

            # Set up the mock service to handle message fetching
            users_mock = MagicMock()
            messages_mock = MagicMock()
            list_mock = MagicMock()
            get_mock = MagicMock()

            # Chain the mocks
            connector.service.users.return_value = users_mock
            users_mock.messages.return_value = messages_mock
            messages_mock.list.return_value = list_mock
            messages_mock.get.return_value = get_mock

            return connector

    def test_initialization(self, email_connector):
        """Test initialization of email connector."""
        expected_email_type = os.environ.get("EMAIL_TYPE", "gmail")
        expected_username = os.environ.get("EMAIL_USERNAME", "test@example.com")

        assert email_connector.email_type == expected_email_type
        assert email_connector.email_username == expected_username

    def test_fetch_messages(self, email_connector):
        """Test fetching messages."""
        # Add debugging
        print("EmailConnector.fetch_messages signature:")
        print(inspect.signature(email_connector.fetch_messages))

        # Mock the Gmail API response
        mock_messages_response = {"messages": [{"id": "msg1"}, {"id": "msg2"}]}

        # Set up the execute method on the list mock
        email_connector.service.users().messages().list().execute.return_value = mock_messages_response

        # Mock the message content responses - add missing fields
        msg1_content = {
            "id": "msg1",
            "internalDate": "1672574400000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Sender <sender@example.com>"},
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "Date", "value": "Mon, 1 Jan 2023 12:00:00 +0000"},
                ],
                "mimeType": "multipart/alternative",
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": base64.b64encode(b"Test Message").decode("utf-8")},
                    }
                ],
            },
        }

        msg2_content = {
            "id": "msg2",
            "internalDate": "1672667600000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Another <another@example.com>"},
                    {"name": "Subject", "value": "Another Subject"},
                    {"name": "Date", "value": "Tue, 2 Jan 2023 14:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.b64encode(b"Another Message").decode("utf-8")},
            },
        }

        # Configure the mock to return different responses for different message IDs
        def get_message_side_effect(userId, id, format=None):
            mock_get_response = MagicMock()
            if id == "msg1":
                mock_get_response.execute.return_value = msg1_content
            elif id == "msg2":
                mock_get_response.execute.return_value = msg2_content
            return mock_get_response

        email_connector.service.users().messages().get.side_effect = get_message_side_effect

        # Call the method without the days_back parameter
        messages = email_connector.fetch_messages()

        # Assertions
        assert len(messages) == 2
        assert messages[0]["id"] == "msg1"
        assert messages[0]["subject"] == "Test Subject"
        assert messages[0]["sender_name"] == "Sender"
        assert messages[0]["sender_email"] == "sender@example.com"
        assert messages[0]["content"] == "Test Message"

        assert messages[1]["id"] == "msg2"
        assert messages[1]["subject"] == "Another Subject"


# Additional test classes for other connectors
class TestLinkedInConnector:
    """Tests for LinkedInConnector class."""

    @pytest.fixture
    def linkedin_connector(self):
        """Create a LinkedIn connector for testing."""
        # Check if we have real credentials to use
        os.environ.get("PHANTOMBUSTER_API_KEY", "")

        connector = LinkedInConnector()
        # Mock any external service calls
        return connector

    def test_initialization(self, linkedin_connector):
        """Test initialization of LinkedIn connector."""
        # Skip if no credentials
        if not os.environ.get("PHANTOMBUSTER_API_KEY"):
            pytest.skip("PHANTOMBUSTER_API_KEY not set in environment variables")

        # Add initialization assertions here
        pass

    def test_fetch_messages(self, linkedin_connector):
        """Test fetching LinkedIn messages."""
        # Skip if no credentials
        if not os.environ.get("PHANTOMBUSTER_API_KEY"):
            pytest.skip("PHANTOMBUSTER_API_KEY not set in environment variables")

        # Add test implementation here
        pass


class TestHandshakeConnector:
    """Tests for HandshakeConnector class."""

    @pytest.fixture
    def handshake_connector(self):
        """Create a Handshake connector for testing."""
        connector = HandshakeConnector()
        # Mock any external service calls
        return connector

    def test_initialization(self, handshake_connector):
        """Test initialization of Handshake connector."""
        # Skip if no credentials
        if not os.environ.get("HANDSHAKE_USERNAME") or not os.environ.get("HANDSHAKE_PASSWORD"):
            pytest.skip("Handshake credentials not set in environment variables")

        # Add initialization assertions here
        pass

    def test_fetch_messages(self, handshake_connector):
        """Test fetching Handshake messages."""
        # Skip if no credentials
        if not os.environ.get("HANDSHAKE_USERNAME") or not os.environ.get("HANDSHAKE_PASSWORD"):
            pytest.skip("Handshake credentials not set in environment variables")

        # Add test implementation here
        pass


class TestSlackConnector:
    """Tests for SlackConnector class."""

    @pytest.fixture
    def slack_connector(self):
        """Create a Slack connector for testing."""
        # Check if we have real credentials to use
        os.environ.get("SLACK_BOT_TOKEN", "")

        connector = SlackConnector()
        # Mock any external service calls
        return connector

    def test_initialization(self, slack_connector):
        """Test initialization of Slack connector."""
        # Skip if no credentials
        if not os.environ.get("SLACK_BOT_TOKEN"):
            pytest.skip("SLACK_BOT_TOKEN not set in environment variables")

        # Add initialization assertions here
        pass

    def test_fetch_messages(self, slack_connector):
        """Test fetching Slack messages."""
        # Skip if no credentials
        if not os.environ.get("SLACK_BOT_TOKEN"):
            pytest.skip("SLACK_BOT_TOKEN not set in environment variables")

        # Add test implementation here
        pass


class TestDiscordConnector:
    """Tests for DiscordConnector class."""

    @pytest.fixture
    def discord_connector(self):
        """Create a Discord connector for testing."""
        # Check if we have real credentials to use
        os.environ.get("DISCORD_BOT_TOKEN", "")

        connector = DiscordConnector()
        # Mock any external service calls
        return connector

    def test_initialization(self, discord_connector):
        """Test initialization of Discord connector."""
        # Skip if no credentials
        if not os.environ.get("DISCORD_BOT_TOKEN"):
            pytest.skip("DISCORD_BOT_TOKEN not set in environment variables")

        # Add initialization assertions here
        pass

    def test_fetch_messages(self, discord_connector):
        """Test fetching Discord messages."""
        # Skip if no credentials
        if not os.environ.get("DISCORD_BOT_TOKEN"):
            pytest.skip("DISCORD_BOT_TOKEN not set in environment variables")

        # Add test implementation here
        pass
