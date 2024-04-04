"""Data Model for State Object."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, Optional

from hassapi.const import DATE_FORMAT

from .base import Model, ModelList


@dataclass(repr=False)
class Context(Model):
    """Representation of HASS Context JSON-object."""

    id: str
    parent_id: Optional[str]
    user_id: Optional[str]


@dataclass(repr=False)
class State(Model):
    """Representation of HASS State JSON-object."""

    entity_id: str
    state: str
    attributes: Dict
    context: Context
    last_changed: datetime
    last_updated: Optional[datetime] = field(default=None)
    last_reported: Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        """Cast some attributes into more convenient types."""
        self.context = Context(**self.context)  # type: ignore
        self.last_changed = datetime.strptime(self.last_changed, DATE_FORMAT)  # type: ignore
        if self.last_updated:
            self.last_updated = datetime.strptime(self.last_updated, DATE_FORMAT)  # type: ignore
        if self.last_reported:
            self.last_reported = datetime.strptime(self.last_reported, DATE_FORMAT)  # type: ignore


class StateList(ModelList):
    """List of HASS State objects."""

    def __init__(self, states: Iterable = ()):
        """Init StateList."""
        super().__init__(State(**s) for s in states)
