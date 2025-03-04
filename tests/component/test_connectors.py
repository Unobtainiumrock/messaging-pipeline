"""
Tests for connector modules.
"""
import pytest
import os
from unittest.mock import MagicMock, patch

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
        with patch.dict(os.environ, {
            'EMAIL_TYPE': 'gmail',
            'EMAIL_USERNAME': 'test@example.com',
            'EMAIL_PASSWORD': 'test_password'
        }):
            connector = EmailConnector()
            # Mock the service
            connector.service = MagicMock()
            return connector
    
    def test_initialization(self, email_connector):
        """Test initialization of email connector."""
        assert email_connector.email_type == 'gmail'
        assert email_connector.email_username == 'test@example.com'
    
    def test_fetch_messages(self, email_connector):
        """Test fetching messages."""
        # Mock the Gmail API response
        mock_messages_response = {
            'messages': [
                {'id': 'msg1'}, 
                {'id': 'msg2'}
            ]
        }
        email_connector.service.users().messages().list().execute.return_value = mock_messages_response
        
        # Mock the message content responses
        msg1_content = {
            'id': 'msg1',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'Sender <sender@example.com>'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Mon, 1 Jan 2023 12:00:00 +0000'}
                ],
                'parts': [{'body': {'data': 'VGVzdCBNZXNzYWdl'}}]  # Base64 "Test Message"
            }
        }
        
        msg2_content = {
            'id': 'msg2',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'Another <another@example.com>'},
                    {'name': 'Subject', 'value': 'Another Subject'},
                    {'name': 'Date', 'value': 'Tue, 2 Jan 2023 14:00:00 +0000'}
                ],
                'body': {'data': 'QW5vdGhlciBNZXNzYWdl'}  # Base64 "Another Message"
            }
        }
        
        # Configure the mock to return different responses for different message IDs
        def get_message_side_effect(userId, id, format=None):
            if id == 'msg1':
                mock_response = MagicMock()
                mock_response.execute.return_value = msg1_content
                return mock_response
            elif id == 'msg2':
                mock_response = MagicMock()
                mock_response.execute.return_value = msg2_content
                return mock_response
        
        email_connector.service.users().messages().get.side_effect = get_message_side_effect
        
        # Call the method
        messages = email_connector.fetch_messages(days_back=7)
        
        # Assertions
        assert len(messages) == 2
        assert messages[0]['id'] == 'msg1'
        assert messages[0]['subject'] == 'Test Subject'
        assert messages[0]['sender_name'] == 'Sender'
        assert messages[0]['sender_email'] == 'sender@example.com'
        assert messages[0]['content'] == 'Test Message'
        
        assert messages[1]['id'] == 'msg2'
        assert messages[1]['subject'] == 'Another Subject'

# Additional test classes for other connectors
class TestLinkedInConnector:
    """Tests for LinkedInConnector class."""
    pass

class TestHandshakeConnector:
    """Tests for HandshakeConnector class."""
    pass

class TestSlackConnector:
    """Tests for SlackConnector class."""
    pass

class TestDiscordConnector:
    """Tests for DiscordConnector class."""
    pass 