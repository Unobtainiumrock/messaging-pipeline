"""Google Calendar integration for scheduling interviews."""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz
from googleapiclient.discovery import build
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class GoogleCalendarScheduler:
    """Scheduler using Google Calendar API."""

    def __init__(self) -> None:
        """Initialize the Google Calendar scheduler."""
        self.credentials_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS",
            "config/credentials/google_credentials.json",
        )
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

        try:
            # Initialize Google Calendar API
            self._init_calendar()

        except Exception as e:
            logger.error(f"Error initializing Google Calendar: {str(e)}", exc_info=True)
            self.service = None

    def _init_calendar(self) -> None:
        """Initialize Google Calendar API client."""
        scopes = ["https://www.googleapis.com/auth/calendar"]

        try:
            # Use service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=scopes
            )

            self.service = build("calendar", "v3", credentials=credentials)
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
                "summary": event_data.get("summary", "Interview"),
                "description": event_data.get("description", ""),
                "start": {
                    "dateTime": event_data.get("start_time"),
                    "timeZone": event_data.get("timezone", "UTC"),
                },
                "end": {
                    "dateTime": event_data.get("end_time"),
                    "timeZone": event_data.get("timezone", "UTC"),
                },
            }

            # Add attendees if available
            if "attendees" in event_data and event_data["attendees"]:
                event["attendees"] = [{"email": email} for email in event_data["attendees"]]

            # Add location if available
            if "location" in event_data and event_data["location"]:
                event["location"] = event_data["location"]

            # Add conference details if needed
            if event_data.get("add_conferencing", True):
                event["conferenceData"] = {
                    "createRequest": {
                        "requestId": f"interview-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                }

            # Create the event
            conf_version = 1 if event_data.get("add_conferencing", True) else 0
            created_event = (
                self.service.events()
                .insert(
                    calendarId=self.calendar_id,
                    body=event,
                    conferenceDataVersion=conf_version,
                    sendUpdates="all",
                )
                .execute()
            )

            logger.info(f"Created Google Calendar event: {created_event['id']}")
            return created_event["id"]

        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}", exc_info=True)
            return None

    def get_available_slots(
        self, days_forward: int = 7, duration_minutes: int = 60
    ) -> List[Dict[str, str]]:
        """
        Get available time slots for scheduling.

        Args:
            days_forward: Number of days to look forward
            duration_minutes: Duration of each slot in minutes

        Returns:
            List of time slot dictionaries with start and end times
        """
        try:
            # Check if service is initialized
            if self.service is None:
                logger.error("Google Calendar service not initialized")
                return []

            # Use timezone-aware datetimes consistently
            now = datetime.now().replace(tzinfo=pytz.UTC)
            start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
            end_time = (now + timedelta(days=days_forward)).replace(
                hour=18, minute=0, second=0, microsecond=0
            )

            # Format times for Calendar API
            start_str = start_time.isoformat()
            end_str = end_time.isoformat()

            # Get busy periods from calendar
            freebusy_query = {
                "timeMin": start_str,
                "timeMax": end_str,
                "items": [{"id": "primary"}],
            }

            freebusy_response = self.service.freebusy().query(body=freebusy_query).execute()
            busy_periods = freebusy_response.get("calendars", {}).get("primary", {}).get("busy", [])

            # Generate all possible slots
            all_slots = []
            slot_duration = timedelta(minutes=duration_minutes)

            # Look through each day
            current_day = start_time
            while current_day.date() <= end_time.date():
                # Start at 8 AM, end at 6 PM for each day
                day_start = datetime.combine(current_day.date(), datetime.min.time()).replace(
                    hour=8, tzinfo=pytz.UTC
                )

                day_end = datetime.combine(current_day.date(), datetime.min.time()).replace(
                    hour=18, tzinfo=pytz.UTC
                )

                # Skip if this day is already past
                if day_end < now:
                    current_day += timedelta(days=1)
                    continue

                # Adjust day_start if it's earlier than now
                if day_start < now:
                    day_start = now

                # Create slots throughout the day
                slot_start = day_start
                while slot_start + slot_duration <= day_end:
                    slot_end = slot_start + slot_duration

                    # Check if this slot overlaps with any busy period
                    is_free = True
                    for busy in busy_periods:
                        # Parse busy times with timezone info
                        busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
                        busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))

                        # Now both times have timezone info, so comparison works
                        if not (slot_end <= busy_start or slot_start >= busy_end):
                            is_free = False
                            break

                    # Add this slot if it's free
                    if is_free:
                        all_slots.append(
                            {
                                "start": slot_start.isoformat(),
                                "end": slot_end.isoformat(),
                            }
                        )

                    # Move to next slot
                    slot_start += timedelta(minutes=30)  # 30-minute increments

                # Move to next day
                current_day += timedelta(days=1)

            return all_slots

        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}", exc_info=True)
            return []

    def get_free_busy(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get busy time periods from the primary Google Calendar between start and end times.

        Args:
            start_time: Start datetime to check availability
            end_time: End datetime to check availability

        Returns:
            List of dicts containing busy periods with 'start' and 'end' datetime strings

        Raises:
            ValueError: If Google Calendar service is not initialized
        """
        if self.service is None:
            raise ValueError("Google Calendar service not initialized")

        query = {
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "items": [{"id": "primary"}],
        }

        free_busy_request = self.service.freebusy().query(body=query).execute()
        busy_periods = free_busy_request.get("calendars", {}).get("primary", {}).get("busy", [])

        return busy_periods

    def create_calendar(self) -> Optional[str]:
        """
        Create a new Google Calendar for the application.

        Returns:
            ID of the newly created calendar, or None if creation fails
        """
        if not self.service:
            logger.error("Google Calendar service not initialized")
            return None

        try:
            # Format the calendar
            calendar = {
                "summary": "Application Calendar",
                "description": "This calendar is used for scheduling interviews and events.",
            }

            # Create the calendar
            created_calendar = self.service.calendars().insert(body=calendar).execute()

            logger.info(f"Created Google Calendar: {created_calendar['id']}")
            return created_calendar["id"]

        except Exception as e:
            logger.error(f"Error creating Google Calendar: {str(e)}", exc_info=True)
            return None
