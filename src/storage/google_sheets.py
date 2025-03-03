"""
Google Sheets storage for message data.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsStorage:
    """Storage class for Google Sheets integration."""
    
    def __init__(self) -> None:
        """Initialize Google Sheets connection."""
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        if not self.sheet_id:
            logger.warning("Google Sheet ID not found in environment variables")
            
        try:
            # Authenticate with Google
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials_path = os.getenv(
                'GOOGLE_APPLICATION_CREDENTIALS', 
                'config/credentials/google_credentials.json'
            )
            
            credentials = Credentials.from_service_account_file(
                credentials_path, 
                scopes=scopes
            )
            
            self.client = gspread.authorize(credentials)
            self.sheet = self.client.open_by_key(self.sheet_id)
            
            # Ensure required worksheets exist
            self._ensure_worksheets_exist()
            
            logger.info("Google Sheets storage initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {str(e)}", exc_info=True)
            self.client = None
            self.sheet = None
    
    def _ensure_worksheets_exist(self) -> None:
        """Ensure that all required worksheets exist, create if not."""
        required_worksheets = ['Messages', 'Interviews', 'Stats']
        
        existing_worksheets = [ws.title for ws in self.sheet.worksheets()]
        
        for worksheet_name in required_worksheets:
            if worksheet_name not in existing_worksheets:
                logger.info(f"Creating worksheet '{worksheet_name}'")
                self.sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
                
                # Set up headers for new worksheets
                worksheet = self.sheet.worksheet(worksheet_name)
                
                if worksheet_name == 'Messages':
                    headers = [
                        'ID', 'Source', 'Sender Name', 'Sender Email', 
                        'Timestamp', 'Subject', 'Preview', 'Intent', 
                        'Processed', 'Link'
                    ]
                    worksheet.append_row(headers)
                    
                elif worksheet_name == 'Interviews':
                    headers = [
                        'ID', 'Message ID', 'Candidate Name', 'Email',
                        'Scheduled Date', 'Status', 'Calendar Link', 'Notes'
                    ]
                    worksheet.append_row(headers)
                    
                elif worksheet_name == 'Stats':
                    headers = [
                        'Date', 'Emails', 'LinkedIn', 'Handshake', 
                        'Other', 'Total', 'Interview Requests'
                    ]
                    worksheet.append_row(headers)
    
    def store_message(self, message: Dict[str, Any]) -> bool:
        """
        Store a message in the Google Sheet.
        
        Args:
            message: The message data to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sheet:
            logger.error("Google Sheets not initialized")
            return False
        
        try:
            messages_sheet = self.sheet.worksheet('Messages')
            
            # Check if message already exists
            existing_ids = messages_sheet.col_values(1)[1:]  # Skip header
            if message['id'] in existing_ids:
                logger.info(f"Message {message['id']} already exists, skipping")
                return True
            
            # Format message data for sheet
            content_preview = message['content'][:100] + '...' if len(message['content']) > 100 else message['content']
            timestamp = message.get('timestamp', '')
            
            # Convert timestamp to readable format if it's a Unix timestamp
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(int(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')
            
            row_data = [
                message['id'],
                message['source'],
                message.get('sender_name', ''),
                message.get('sender_email', ''),
                timestamp,
                message.get('subject', ''),
                content_preview,
                message.get('intent', 'unknown'),
                'false',  # Processed flag, initially false
                ''  # Link placeholder
            ]
            
            # Add to sheet
            messages_sheet.append_row(row_data)
            
            # Update stats
            self._update_stats(message['source'])
            
            logger.info(f"Stored message {message['id']} from {message['source']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing message in Google Sheets: {str(e)}", exc_info=True)
            return False
    
    def _update_stats(self, source: str) -> None:
        """
        Update stats worksheet with new message count.
        
        Args:
            source: The source of the message (gmail, linkedin, etc.)
        """
        try:
            stats_sheet = self.sheet.worksheet('Stats')
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Get today's row if it exists
            date_column = stats_sheet.col_values(1)
            row_index = None
            
            if today in date_column:
                row_index = date_column.index(today) + 1
            
            if row_index:
                # Update existing row
                row_data = stats_sheet.row_values(row_index)
                
                # Map source to column index
                source_column = {
                    'gmail': 2,
                    'outlook': 2,  # Both count as emails
                    'linkedin': 3,
                    'handshake': 4,
                    'slack': 5,
                    'discord': 5
                }.get(source, 5)  # Default to "Other" column
                
                # Increment the appropriate column
                if len(row_data) >= source_column:
                    current_value = int(row_data[source_column - 1] or 0)
                    stats_sheet.update_cell(row_index, source_column, current_value + 1)
                
                # Update total
                if len(row_data) >= 6:
                    total = int(row_data[5] or 0)
                    stats_sheet.update_cell(row_index, 6, total + 1)
            else:
                # Create new row for today
                new_row = [today, 0, 0, 0, 0, 1, 0]  # Start with 1 total
                
                # Set the source column
                if source in ['gmail', 'outlook']:
                    new_row[1] = 1  # Emails
                elif source == 'linkedin':
                    new_row[2] = 1  # LinkedIn
                elif source == 'handshake':
                    new_row[3] = 1  # Handshake
                else:
                    new_row[4] = 1  # Other
                
                stats_sheet.append_row(new_row)
                
        except Exception as e:
            logger.error(f"Error updating stats: {str(e)}")
    
    def mark_as_processed(self, message_id: str, intent: str = None) -> None:
        """
        Mark a message as processed and update its intent if provided.
        
        Args:
            message_id: The ID of the message to update
            intent: Optional intent classification to update
        """
        if not self.sheet:
            logger.error("Google Sheets not initialized")
            return
        
        try:
            messages_sheet = self.sheet.worksheet('Messages')
            
            # Find message row
            id_column = messages_sheet.col_values(1)
            if message_id in id_column:
                row_index = id_column.index(message_id) + 1
                
                # Update processed flag
                messages_sheet.update_cell(row_index, 9, 'true')
                
                # Update intent if provided
                if intent:
                    messages_sheet.update_cell(row_index, 8, intent)
                
                logger.info(f"Marked message {message_id} as processed")
            else:
                logger.warning(f"Message {message_id} not found in sheet")
                
        except Exception as e:
            logger.error(f"Error marking message as processed: {str(e)}")
    
    def store_interview(self, interview_data: Dict[str, Any]) -> bool:
        """
        Store interview scheduling information.
        
        Args:
            interview_data: Dictionary with interview details
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sheet:
            logger.error("Google Sheets not initialized")
            return False
        
        try:
            interviews_sheet = self.sheet.worksheet('Interviews')
            
            # Generate ID
            interview_id = f"INT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            row_data = [
                interview_id,
                interview_data.get('message_id', ''),
                interview_data.get('candidate_name', ''),
                interview_data.get('email', ''),
                interview_data.get('scheduled_date', ''),
                interview_data.get('status', 'scheduled'),
                interview_data.get('calendar_link', ''),
                interview_data.get('notes', '')
            ]
            
            # Add to sheet
            interviews_sheet.append_row(row_data)
            
            # Update stats - increment interview requests
            stats_sheet = self.sheet.worksheet('Stats')
            today = datetime.now().strftime('%Y-%m-%d')
            date_column = stats_sheet.col_values(1)
            
            if today in date_column:
                row_index = date_column.index(today) + 1
                row_data = stats_sheet.row_values(row_index)
                
                if len(row_data) >= 7:
                    current_value = int(row_data[6] or 0)
                    stats_sheet.update_cell(row_index, 7, current_value + 1)
            
            logger.info(f"Stored interview {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing interview: {str(e)}", exc_info=True)
            return False 