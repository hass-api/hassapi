"""Data Model for Service Object."""

from dataclasses import dataclass
from typing import Iterable

from .base import Model, ModelList


@dataclass(repr=False)
class Event(Model):
    """Representation of HASS Event JSON-object."""

    event: str
    listener_count: int


class EventList(ModelList):
    """List of HASS Event objects."""

    def __init__(self, services: Iterable = ()):
        """Init EventList."""
        super().__init__(Event(**s) for s in services)
