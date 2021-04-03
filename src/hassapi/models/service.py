"""Data Model for Service Object."""

from dataclasses import dataclass
from typing import Dict, Iterable

from .base import Model, ModelList


@dataclass(repr=False)
class Service(Model):
    """Representation of HASS Service JSON-object."""

    domain: str
    services: Dict


class ServiceList(ModelList):
    """List of HASS Service objects."""

    def __init__(self, services: Iterable = ()):
        """Init ServiceList."""
        super().__init__(Service(**s) for s in services)
