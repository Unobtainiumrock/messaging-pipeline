"""Calendly integration for scheduling interviews."""
import os
import logging
import requests
import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class CalendlyScheduler:
    """Scheduler using Calendly API."""

    def __init__(self) -> None:
        """Initialize the Calendly scheduler."""
        self.api_key = os.getenv("CALENDLY_API_KEY")
        self.organization = os.getenv("CALENDLY_ORGANIZATION", "")
        self.user = os.getenv("CALENDLY_USER", "")

        # Base URLs and endpoints
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Default scheduling links
        self.default_link = "https://calendly.com/fake/interview"

        # Cache for event types
        self.event_types: Optional[List[Dict[str, Any]]] = None

        if not self.api_key:
            logger.warning("Calendly API key not found in environment variables")

    def get_scheduling_link(self, event_type: str = "interview") -> str:
        """
        Get a scheduling link for a specific event type.

        Args:
            event_type: Type of event (interview, follow-up, etc.)

        Returns:
            Scheduling link URL
        """
        # For now, return the default link
        # In a real implementation, you'd look up the right link based on event type
        return self.default_link

    def get_event_types(self) -> List[Dict[str, Any]]:
        """
        Get available event types from Calendly.

        Returns:
            List of event type dictionaries
        """
        if not self.api_key or not self.user:
            logger.warning("Calendly API credentials not configured")
            return []

        # Even though we have type annotation on self.event_types, we need to be more explicit
        if isinstance(self.event_types, list):
            return self.event_types

        try:
            url = f"{self.base_url}/event_types?user={self.user}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                # Extract data and ensure it's a list
                event_types_data = data.get("data", []) if isinstance(data, dict) else []
                # Explicitly set to a list, never None
                self.event_types = event_types_data
                return self.event_types
            else:
                logger.error(f"Error fetching Calendly event types: {response.status_code}")
                self.event_types = []  # Explicitly set to empty list on error
                return []

        except Exception as e:
            logger.error(f"Error communicating with Calendly API: {str(e)}", exc_info=True)
            self.event_types = []  # Explicitly set to empty list on error
            return []

    def get_scheduled_events(
        self,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get scheduled events within a time range.

        Args:
            start_time: Start of time range (defaults to now)
            end_time: End of time range (defaults to 30 days from now)

        Returns:
            List of scheduled event dictionaries
        """
        if not self.api_key or not self.user:
            logger.warning("Calendly API credentials not configured")
            return []

        # Set default date range if not provided
        if start_time is None:
            start_time = datetime.datetime.now()

        if end_time is None:
            end_time = start_time + datetime.timedelta(days=30)

        # Format dates for Calendly API
        min_start_time = start_time.isoformat() + "Z"
        max_start_time = end_time.isoformat() + "Z"

        try:
            url = f"{self.base_url}/scheduled_events"
            params = {
                "user": self.user,
                "min_start_time": min_start_time,
                "max_start_time": max_start_time,
                "status": "active",
            }

            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                data = response.json()
                raw_events = data.get("data", [])

                # Transform events to expected format
                events = []
                for event in raw_events:
                    # Extract event attributes
                    attrs = event.get("attributes", {})
                    location_obj = attrs.get("location", {})

                    # Extract location string if available, otherwise use empty string
                    location_str = (
                        location_obj.get("location", "")
                        if isinstance(location_obj, dict)
                        else str(location_obj)
                    )

                    # Create flattened event object with attributes at top level
                    processed_event = {
                        "id": event.get("id", ""),
                        "name": attrs.get("name", ""),
                        "start_time": attrs.get("start_time", ""),
                        "end_time": attrs.get("end_time", ""),
                        "status": attrs.get("status", ""),
                        "event_type": attrs.get("event_type", ""),
                        "location": location_str,
                        "cancellation_url": attrs.get("cancellation_url", ""),
                    }
                    events.append(processed_event)

                return events
            else:
                logger.error(f"Error fetching Calendly events: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching scheduled events: {str(e)}", exc_info=True)
            return []

    def get_available_slots(self) -> List[Dict[str, Any]]:
        """
        Get available time slots for scheduling.

        Returns:
            List of available time slot dictionaries with start and end times
        """
        if not self.api_key or not self.user:
            logger.warning("Calendly API credentials not configured")
            return []  # Return empty list instead of None

        try:
            # This would normally use the Calendly API to fetch available slots
            # For now we're just implementing the stub to fix the type issue

            # Example implementation:
            # url = f"{self.base_url}/available_times"
            # params = {
            #     "user": self.user,
            #     "start_time": datetime.datetime.now().isoformat(),
            #     "end_time": (datetime.datetime.now() + datetime.timedelta(days=14)).isoformat()
            # }
            # response = requests.get(url, headers=self.headers, params=params)
            #
            # if response.status_code == 200:
            #     data = response.json()
            #     return data.get("available_slots", [])

            logger.warning("Calendly get_available_slots not fully implemented")
            return []

        except Exception as e:
            logger.error(f"Error fetching available slots: {str(e)}", exc_info=True)
            return []  # Always return a list, never None
