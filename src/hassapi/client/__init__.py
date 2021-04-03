"""Home Assistant API Client."""

from .events import EventsClient
from .services import ServicesClient
from .states import StatesClient
from .template import TemplateClient


class Hass(StatesClient, ServicesClient, TemplateClient, EventsClient):
    """Home Assistant API Client."""
