"""Client for functionality related to HASS events."""

from typing import Dict, Optional

from hassapi.models import EventList

from .base import BaseClient


class EventsClient(BaseClient):
    """Events Client."""

    def get_events(self) -> EventList:
        """Get list of HASS events."""
        return EventList(self._get("events"))

    def fire_event(self, event_type: str, event_data: Optional[Dict] = None) -> str:
        """Fire HASS event."""
        return self._post(f"events/{event_type}", json=event_data)["message"]  # type: ignore
