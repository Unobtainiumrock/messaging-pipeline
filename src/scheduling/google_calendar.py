"""
Google Calendar integration for scheduling interviews.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class GoogleCalendarScheduler:
    """Scheduler using Google Calendar API."""
    
    def __init__(self) -> None:
        """Initialize the Google Calendar scheduler."""
        self.credentials_path = os.getenv(
            'GOOGLE_APPLICATION_CREDENTIALS', 
            'config/credentials/google_credentials.json'
        )
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        try:
            # Initialize Google Calendar API
            self._init_calendar()
            
        except Exception as e:
            logger.error(f"Error initializing Google Calendar: {str(e)}", exc_info=True)
            self.service = None
    
    def _init_calendar(self) -> None:
        """Initialize Google Calendar API client."""
        scopes = ['https://www.googleapis.com/auth/calendar']
        
        try:
            # Use service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=scopes
            )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar API initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Google Calendar API: {str(e)}", exc_info=True)
            self.service = None
    
    def create_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a calendar event.
        
        Args:
            event_data: Dictionary with event details
                - summary: Event title
                - description: Event description
                - start_time: Start time (ISO format)
                - end_time: End time (ISO format)
                - attendees: List of email addresses
                - location: Optional location
                
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Google Calendar service not initialized")
            return None
        
        try:
            # Format the event
            event = {
                'summary': event_data.get('summary', 'Interview'),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data.get('start_time'),
                    'timeZone': event_data.get('timezone', 'UTC'),
                },
                'end': {
                    'dateTime': event_data.get('end_time'),
                    'timeZone': event_data.get('timezone', 'UTC'),
                }
            }
            
            # Add attendees if available
            if 'attendees' in event_data and event_data['attendees']:
                event['attendees'] = [{'email': email} for email in event_data['attendees']]
            
            # Add location if available
            if 'location' in event_data and event_data['location']:
                event['location'] = event_data['location']
            
            # Add conference details if needed
            if event_data.get('add_conferencing', True):
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': f"interview-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                conferenceDataVersion=1 if event_data.get('add_conferencing', True) else 0,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Created Google Calendar event: {created_event['id']}")
            return created_event['id']
            
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}", exc_info=True)
            return None
    
    def get_available_slots(self, days_forward: int = 7, duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Get available time slots for scheduling.
        
        Args:
            days_forward: Number of days to look ahead
            duration_minutes: Duration of the meeting in minutes
            
        Returns:
            List of available time slots with start and end times
        """
        if not self.service:
            logger.error("Google Calendar service not initialized")
            return []
        
        try:
            # Define time boundaries
            now = datetime.now(pytz.UTC)
            end_date = now + timedelta(days=days_forward)
            
            # Get busy times
            freebusy_query = {
                'timeMin': now.isoformat(),
                'timeMax': end_date.isoformat(),
                'items': [{'id': self.calendar_id}]
            }
            
            freebusy_response = self.service.freebusy().query(body=freebusy_query).execute()
            busy_times = freebusy_response['calendars'][self.calendar_id]['busy']
            
            # Convert busy times to datetime objects
            busy_periods = []
            for period in busy_times:
                start = datetime.fromisoformat(period['start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(period['end'].replace('Z', '+00:00'))
                busy_periods.append((start, end))
            
            # Define working hours (9 AM to 5 PM, M-F)
            working_start_hour = 9
            working_end_hour = 17
            
            # Generate all possible slots
            available_slots = []
            current_date = now.replace(hour=working_start_hour, minute=0, second=0, microsecond=0)
            
            if current_date < now:
                # If we're past the start of working hours, start from the next hour
                current_date = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            
            while current_date < end_date:
                # Skip weekends
                if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                    current_date = current_date.replace(hour=working_start_hour) + timedelta(days=1)
                    continue
                
                # Skip outside of working hours
                if current_date.hour < working_start_hour or current_date.hour >= working_end_hour:
                    # Go to next day's working start hour
                    next_day = current_date.date() + timedelta(days=1)
                    current_date = datetime.combine(
                        next_day, 
                        datetime.min.time(), 
                        tzinfo=current_date.tzinfo
                    ).replace(hour=working_start_hour)
                    continue
                
                # Calculate slot end time
                slot_end = current_date + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with any busy period
                is_available = True
                for busy_start, busy_end in busy_periods:
                    # Check for overlap
                    if (current_date < busy_end and slot_end > busy_start):
                        is_available = False
                        # Skip to end of this busy period
                        current_date = busy_end
                        break
                
                if is_available:
                    available_slots.append({
                        'start': current_date.isoformat(),
                        'end': slot_end.isoformat()
                    })
                    # Move to next slot
                    current_date = slot_end
                
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}", exc_info=True)
            return [] 