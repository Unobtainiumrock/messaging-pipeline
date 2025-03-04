"""
Tests for storage modules.
"""
import pytest
from unittest.mock import MagicMock, patch
import os

from src.storage.google_sheets import GoogleSheetsStorage

class TestGoogleSheetsStorage:
    """Tests for GoogleSheetsStorage class."""
    
    @pytest.fixture
    def google_sheets_storage(self):
        """Create a Google Sheets storage for testing."""
        with patch('src.storage.google_sheets.gspread.service_account') as mock_service_account:
            with patch.dict(os.environ, {'GOOGLE_SHEET_ID': 'fake_sheet_id'}):
                # Mock the gspread client
                mock_client = MagicMock()
                mock_sheet = MagicMock()
                mock_worksheet_messages = MagicMock()
                mock_worksheet_stats = MagicMock()
                
                # Configure the mocks
                mock_service_account.return_value = mock_client
                mock_client.open_by_key.return_value = mock_sheet
                mock_sheet.worksheet.side_effect = lambda name: (
                    mock_worksheet_messages if name == 'Messages' else mock_worksheet_stats
                )
                
                return GoogleSheetsStorage()
    
    def test_initialization(self, google_sheets_storage):
        """Test initialization of Google Sheets storage."""
        assert google_sheets_storage.sheet_id == 'fake_sheet_id'
        assert google_sheets_storage.sheet is not None
    
    def test_store_message(self, google_sheets_storage):
        """Test storing a message."""
        # Mock worksheet methods
        messages_worksheet = google_sheets_storage.sheet.worksheet('Messages')
        
        # Test data
        message = {
            'id': 'msg123',
            'source': 'email',
            'sender_name': 'Test Sender',
            'sender_email': 'sender@example.com',
            'timestamp': '2023-01-10T12:00:00Z',
            'subject': 'Test Subject',
            'content': 'This is a test message.',
            'intent': 'interview_request'
        }
        
        # Test
        result = google_sheets_storage.store_message(message)
        
        # Assertions
        assert result is True
        messages_worksheet.append_row.assert_called_once()
        
        # Check that the right data was sent
        call_args = messages_worksheet.append_row.call_args[0][0]
        assert call_args[0] == 'msg123'  # ID
        assert call_args[1] == 'email'   # Source
        assert call_args[2] == 'Test Sender'  # Sender name
        assert 'interview_request' in call_args  # Intent
    
    def test_get_messages(self, google_sheets_storage):
        """Test getting messages by source."""
        # Mock the worksheet's get_all_records method
        messages_worksheet = google_sheets_storage.sheet.worksheet('Messages')
        messages_worksheet.get_all_records.return_value = [
            {
                'ID': 'msg1',
                'Source': 'email',
                'Sender Name': 'Person 1',
                'Sender Email': 'person1@example.com',
                'Timestamp': '2023-01-05T10:00:00Z',
                'Subject': 'Email Subject',
                'Content': 'Email content',
                'Intent': 'information_request'
            },
            {
                'ID': 'msg2',
                'Source': 'linkedin',
                'Sender Name': 'Person 2',
                'Sender Email': 'person2@example.com',
                'Timestamp': '2023-01-06T11:00:00Z',
                'Subject': '',
                'Content': 'LinkedIn message',
                'Intent': 'interview_request'
            },
            {
                'ID': 'msg3',
                'Source': 'email',
                'Sender Name': 'Person 3',
                'Sender Email': 'person3@example.com',
                'Timestamp': '2023-01-07T12:00:00Z',
                'Subject': 'Another Email',
                'Content': 'Another email content',
                'Intent': 'follow_up'
            }
        ]
        
        # Test
        email_messages = google_sheets_storage.get_messages(source='email')
        linkedin_messages = google_sheets_storage.get_messages(source='linkedin')
        all_messages = google_sheets_storage.get_messages()
        
        # Assertions
        assert len(email_messages) == 2
        assert len(linkedin_messages) == 1
        assert len(all_messages) == 3
        
        assert email_messages[0]['id'] == 'msg1'
        assert email_messages[1]['id'] == 'msg3'
        assert linkedin_messages[0]['id'] == 'msg2' 