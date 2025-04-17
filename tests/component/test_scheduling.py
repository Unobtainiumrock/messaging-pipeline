"""Tests for scheduling modules."""

import pytest
from unittest.mock import MagicMock, patch
import os
from datetime import datetime

from src.scheduling.calendly import CalendlyScheduler
from src.scheduling.google_calendar import GoogleCalendarScheduler


class TestCalendlyScheduler:
    """Tests for CalendlyScheduler class."""

    @pytest.fixture
    def calendly_scheduler(self):
        """Create a Calendly scheduler for testing."""
        with patch.dict(
            os.environ,
            {
                "CALENDLY_API_KEY": "fake_api_key",
                "CALENDLY_USER": "fake_user",
                "CALENDLY_DEFAULT_LINK": "https://calendly.com/fake/interview",
            },
        ):
            return CalendlyScheduler()

    def test_initialization(self, calendly_scheduler):
        """Test initialization of Calendly scheduler."""
        assert calendly_scheduler.api_key == "fake_api_key"
        assert calendly_scheduler.user == "fake_user"

    def test_get_scheduling_link_default(self, calendly_scheduler):
        """Test getting the default scheduling link."""
        link = calendly_scheduler.get_scheduling_link()
        assert link == "https://calendly.com/fake/interview"

    @patch("requests.get")
    def test_get_scheduled_events(self, mock_get, calendly_scheduler):
        """Test getting scheduled events."""
        # Mock the Calendly API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "event1",
                    "attributes": {
                        "name": "Interview with Candidate",
                        "start_time": "2023-01-15T10:00:00Z",
                        "end_time": "2023-01-15T11:00:00Z",
                        "status": "confirmed",
                        "event_type": "interview",
                        "location": {"location": "Zoom"},
                        "cancellation_url": "https://calendly.com/cancel/event1",
                    },
                },
                {
                    "id": "event2",
                    "attributes": {
                        "name": "Follow-up Meeting",
                        "start_time": "2023-01-16T14:00:00Z",
                        "end_time": "2023-01-16T15:00:00Z",
                        "status": "confirmed",
                        "event_type": "meeting",
                        "location": {"location": "Google Meet"},
                        "cancellation_url": "https://calendly.com/cancel/event2",
                    },
                },
            ]
        }
        mock_get.return_value = mock_response

        # Test
        events = calendly_scheduler.get_scheduled_events()

        # Assertions
        assert len(events) == 2
        assert events[0]["id"] == "event1"
        assert events[0]["name"] == "Interview with Candidate"
        assert events[0]["start_time"] == "2023-01-15T10:00:00Z"
        assert events[0]["end_time"] == "2023-01-15T11:00:00Z"
        assert events[0]["location"] == "Zoom"

        assert events[1]["id"] == "event2"
        assert events[1]["name"] == "Follow-up Meeting"


class TestGoogleCalendarScheduler:
    """Tests for GoogleCalendarScheduler class."""

    @pytest.fixture
    def google_calendar_scheduler(self):
        """Create a Google Calendar scheduler for testing."""
        with patch("src.scheduling.google_calendar.service_account.Credentials.from_service_account_file"):
            with patch("src.scheduling.google_calendar.build") as mock_build:
                mock_service = MagicMock()
                mock_build.return_value = mock_service
                return GoogleCalendarScheduler()

    def test_initialization(self, google_calendar_scheduler):
        """Test initialization of Google Calendar scheduler."""
        assert google_calendar_scheduler.service is not None

    def test_create_event(self, google_calendar_scheduler):
        """Test creating an event."""
        # Mock the Google Calendar API response
        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "event123"}
        google_calendar_scheduler.service.events().insert.return_value = mock_insert

        # Test data
        event_data = {
            "summary": "Interview with Candidate",
            "description": "Interview for Software Engineer role",
            "start_time": "2023-01-20T10:00:00Z",
            "end_time": "2023-01-20T11:00:00Z",
            "attendees": ["candidate@example.com", "interviewer@example.com"],
            "location": "Google Meet",
            "add_conferencing": True,
        }

        # Test
        event_id = google_calendar_scheduler.create_event(event_data)

        # Assertions
        assert event_id == "event123"

        # Verify the mock was called
        assert mock_insert.execute.called

        # Access the call args directly - this is more reliable
        insert_call = google_calendar_scheduler.service.events().insert
        assert insert_call.called

        # Check the arguments if needed
        assert "calendarId" in insert_call.call_args.kwargs
        assert insert_call.call_args.kwargs["calendarId"] == "primary"
        assert "body" in insert_call.call_args.kwargs
        assert insert_call.call_args.kwargs["body"]["summary"] == "Interview with Candidate"

    def test_get_available_slots(self, google_calendar_scheduler):
        """Test getting available time slots."""
        # Mock the freebusy query response
        mock_freebusy_response = {
            "calendars": {
                "primary": {
                    "busy": [
                        {
                            "start": "2023-01-20T09:00:00Z",
                            "end": "2023-01-20T10:00:00Z",
                        },
                        {
                            "start": "2023-01-20T13:00:00Z",
                            "end": "2023-01-20T14:00:00Z",
                        },
                    ]
                }
            }
        }
        google_calendar_scheduler.service.freebusy().query().execute.return_value = mock_freebusy_response

        # Test
        with patch("src.scheduling.google_calendar.datetime") as mock_datetime:
            # Mock current time to have a fixed starting point
            fixed_now = datetime(2023, 1, 20, 8, 0, 0)
            mock_datetime.now.return_value = fixed_now
            mock_datetime.combine.return_value = fixed_now
            mock_datetime.fromisoformat.side_effect = lambda x: datetime.fromisoformat(
                x.replace("Z", "+00:00")
            )

            # Propagate the real datetime methods to our mock
            mock_datetime.side_effect = datetime

            # Run the test
            slots = google_calendar_scheduler.get_available_slots(days_forward=1, duration_minutes=30)

        # Assertions - Should have available slots that don't overlap with busy times
        assert len(slots) > 0
        for slot in slots:
            slot_start = datetime.fromisoformat(slot["start"].replace("Z", "+00:00"))
            slot_end = datetime.fromisoformat(slot["end"].replace("Z", "+00:00"))

            # Check that the slot doesn't overlap with busy periods
            for busy in mock_freebusy_response["calendars"]["primary"]["busy"]:
                busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
                busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))

                # No overlap condition: slot ends before busy starts or slot starts after busy ends
                assert slot_end <= busy_start or slot_start >= busy_end
