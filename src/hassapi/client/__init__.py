"""Home Assistant API Client."""

from .events import EventsClient
from .services import ServicesClient
from .states import StatesClient
from .template import TemplateClient
from .websocket import WebSocketClient


class Hass(StatesClient, ServicesClient, TemplateClient, EventsClient, WebSocketClient):
    """Home Assistant API Client."""
