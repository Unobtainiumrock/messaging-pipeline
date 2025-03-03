"""
Calendly integration for scheduling interviews.
"""
import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CalendlyScheduler:
    """Scheduler using Calendly API."""
    
    def __init__(self) -> None:
        """Initialize the Calendly scheduler."""
        self.api_key = os.getenv('CALENDLY_API_KEY')
        self.user = os.getenv('CALENDLY_USER')
        
        if not self.api_key:
            logger.warning("Calendly API key not found in environment variables")
    
    def get_scheduling_link(self, event_type: str = None) -> str:
        """
        Get a scheduling link for a specific event type.
        
        Args:
            event_type: Optional event type name (uses default if not specified)
            
        Returns:
            Calendly scheduling link
        """
        try:
            if event_type:
                # If a specific event type is requested, fetch its link
                return self._get_event_link(event_type)
            else:
                # Otherwise return the default interview event link
                default_link = os.getenv('CALENDLY_DEFAULT_LINK')
                if default_link:
                    return default_link
                
                # If no default link is configured, try to get the first event type
                return self._get_first_event_link()
                
        except Exception as e:
            logger.error(f"Error getting Calendly scheduling link: {str(e)}", exc_info=True)
            # Return a fallback or empty string if there's an error
            return os.getenv('CALENDLY_FALLBACK_LINK', '')
    
    def _get_event_link(self, event_type_name: str) -> str:
        """
        Get a scheduling link for a specific named event type.
        
        Args:
            event_type_name: Name of the event type
            
        Returns:
            Calendly scheduling link
        """
        if not self.api_key or not self.user:
            logger.error("Missing Calendly credentials")
            return ''
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Get user's event types
        url = f'https://api.calendly.com/event_types?user={self.user}'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Calendly event types: {response.text}")
            return ''
        
        data = response.json()
        
        # Find the event type by name
        for event_type in data.get('data', []):
            if event_type.get('attributes', {}).get('name') == event_type_name:
                return event_type.get('attributes', {}).get('scheduling_url', '')
        
        logger.warning(f"No Calendly event type found with name: {event_type_name}")
        return ''
    
    def _get_first_event_link(self) -> str:
        """
        Get the first available event type link.
        
        Returns:
            Calendly scheduling link for the first event type
        """
        if not self.api_key or not self.user:
            logger.error("Missing Calendly credentials")
            return ''
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Get user's event types
        url = f'https://api.calendly.com/event_types?user={self.user}'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Calendly event types: {response.text}")
            return ''
        
        data = response.json()
        
        # Return the first event type scheduling URL
        if data.get('data') and len(data['data']) > 0:
            return data['data'][0].get('attributes', {}).get('scheduling_url', '')
        
        logger.warning("No Calendly event types found")
        return ''
    
    def get_scheduled_events(self, days_forward: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming scheduled events.
        
        Args:
            days_forward: Number of days to look ahead
            
        Returns:
            List of scheduled events
        """
        if not self.api_key or not self.user:
            logger.error("Missing Calendly credentials")
            return []
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Calculate min and max times for range
        min_time = datetime.now().isoformat()
        max_time = (datetime.now() + timedelta(days=days_forward)).isoformat()
        
        # Get scheduled events
        url = f'https://api.calendly.com/scheduled_events?user={self.user}&min_start_time={min_time}&max_start_time={max_time}'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch Calendly events: {response.text}")
            return []
        
        data = response.json()
        
        # Process and return events
        events = []
        for event in data.get('data', []):
            attrs = event.get('attributes', {})
            
            processed_event = {
                'id': event.get('id', ''),
                'name': attrs.get('name', ''),
                'start_time': attrs.get('start_time', ''),
                'end_time': attrs.get('end_time', ''),
                'status': attrs.get('status', ''),
                'event_type': attrs.get('event_type', ''),
                'location': attrs.get('location', {}).get('location', ''),
                'invitee_email': '',  # We need to make another request to get this
                'cancellation_url': attrs.get('cancellation_url', '')
            }
            
            events.append(processed_event)
        
        return events 