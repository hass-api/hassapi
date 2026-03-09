"""Client for real-time HA event subscriptions via WebSocket."""

import json
import logging
import threading
import time
from typing import Callable, Dict, Optional

import websocket

from hassapi.exceptions import ClientError

from .auth import AuthenticatedClient

_LOGGER = logging.getLogger(__name__)

CallbackType = Callable[[Dict], None]

_MAX_RETRIES = 5
_BASE_DELAY = 1.0
_MAX_DELAY = 60.0
_RESET_AFTER = 30.0  # reset retry counter if connection lived this long (seconds)


class WebSocketClient(AuthenticatedClient):
    """Client for real-time HA event subscriptions via WebSocket."""

    def __init__(
        self,
        hassurl: Optional[str] = None,
        token: Optional[str] = None,
        verify: bool = True,
        timeout: float = 3,
    ):
        """Create WebSocket client."""
        super().__init__(hassurl, token, verify)
        self._subscriptions: Dict[int, Dict] = {}
        self._next_id: int = 1
        self._ws: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._stopping: bool = False
        self._authenticated: bool = False
        self._connected_at: Optional[float] = None

    def subscribe_to_events(
        self, callback: CallbackType, event_type: Optional[str] = None
    ) -> None:
        """Subscribe to HA events. Non-blocking — runs in a background thread.

        Args:
            callback: Function called with the event dict on each event.
            event_type: Optional event type filter e.g. 'state_changed'. Subscribes
                to all events if omitted.
        """
        msg: Dict = {"type": "subscribe_events"}
        if event_type:
            msg["event_type"] = event_type
        self._add_subscription(msg=msg, callback=callback, entity_id=None)

    def subscribe_to_state_changes(
        self, callback: CallbackType, entity_id: Optional[str] = None
    ) -> None:
        """Subscribe to state_changed events. Non-blocking — runs in a background thread.

        Args:
            callback: Function called with the event dict on each state change.
            entity_id: Optional entity to filter on e.g. 'light.living_room'. Subscribes
                to all state changes if omitted.
        """
        msg: Dict = {"type": "subscribe_events", "event_type": "state_changed"}
        self._add_subscription(msg=msg, callback=callback, entity_id=entity_id)

    def unsubscribe(self) -> None:
        """Unsubscribe all subscriptions and close the WebSocket connection."""
        self._stopping = True
        with self._lock:
            if self._ws and self._authenticated:
                for sub_id in self._subscriptions:
                    try:
                        self._ws.send(
                            json.dumps(
                                {
                                    "id": self._next_id,
                                    "type": "unsubscribe_events",
                                    "subscription": sub_id,
                                }
                            )
                        )
                        self._next_id += 1
                    except Exception:
                        pass
            if self._ws:
                self._ws.close()
        self._subscriptions.clear()
        self._authenticated = False

    def _add_subscription(
        self, msg: Dict, callback: CallbackType, entity_id: Optional[str]
    ) -> None:
        """Register a subscription and send it if already authenticated."""
        with self._lock:
            sub_id = self._next_id
            self._next_id += 1
            msg["id"] = sub_id
            self._subscriptions[sub_id] = {
                "msg": msg,
                "callback": callback,
                "entity_id": entity_id,
            }
            if self._authenticated and self._ws:
                self._ws.send(json.dumps(msg))
        self._ensure_connected()

    def _ensure_connected(self) -> None:
        """Start the WebSocket background thread if not already running."""
        if self._thread is None or not self._thread.is_alive():
            self._stopping = False
            self._ws = self._create_ws_app()
            self._thread = threading.Thread(target=self._run_with_retry, daemon=True)
            self._thread.start()

    def _create_ws_app(self) -> websocket.WebSocketApp:
        """Create a new WebSocketApp instance."""
        return websocket.WebSocketApp(
            self._get_ws_url(),
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

    def _run_with_retry(self) -> None:
        """Run WebSocket connection with exponential backoff retry on failure."""
        attempt = 0
        while not self._stopping:
            self._connected_at = None
            self._ws.run_forever()  # type: ignore[union-attr]

            if self._stopping:
                break

            alive_for = (
                time.monotonic() - self._connected_at if self._connected_at is not None else 0.0
            )
            if alive_for >= _RESET_AFTER:
                attempt = 0

            if attempt >= _MAX_RETRIES:
                _LOGGER.error("WebSocket: giving up after %d retries.", _MAX_RETRIES)
                break

            delay = min(_BASE_DELAY * (2**attempt), _MAX_DELAY)
            _LOGGER.warning(
                "WebSocket disconnected. Retrying in %.1fs (attempt %d/%d).",
                delay,
                attempt + 1,
                _MAX_RETRIES,
            )
            time.sleep(delay)
            attempt += 1
            self._authenticated = False
            self._ws = self._create_ws_app()

    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        """Handle WebSocket connection opened."""
        self._connected_at = time.monotonic()
        _LOGGER.debug("WebSocket connection opened.")

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """Handle incoming WebSocket message."""
        data = json.loads(message)
        msg_type = data.get("type")

        if msg_type == "auth_required":
            ws.send(json.dumps({"type": "auth", "access_token": self._token}))
        elif msg_type == "auth_ok":
            _LOGGER.debug("WebSocket authenticated.")
            with self._lock:
                self._authenticated = True
                for sub in self._subscriptions.values():
                    ws.send(json.dumps(sub["msg"]))
        elif msg_type == "auth_invalid":
            _LOGGER.error("WebSocket authentication failed — check your token.")
            self._stopping = True
            ws.close()
            raise ClientError("WebSocket authentication failed.")
        elif msg_type == "event":
            self._dispatch(data)

    def _dispatch(self, data: Dict) -> None:
        """Dispatch an incoming event to the matching callback."""
        sub_id = data.get("id")
        with self._lock:
            sub = self._subscriptions.get(sub_id)  # type: ignore[arg-type]
        if sub is None:
            return
        event = data["event"]
        entity_id_filter = sub.get("entity_id")
        if entity_id_filter and event.get("data", {}).get("entity_id") != entity_id_filter:
            return
        sub["callback"](event)

    def _on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:
        """Handle WebSocket error."""
        _LOGGER.error("WebSocket error: %s", error)

    def _on_close(
        self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str
    ) -> None:
        """Handle WebSocket connection closed."""
        _LOGGER.debug("WebSocket closed (code=%s): %s", close_status_code, close_msg)
        self._authenticated = False

    def _get_ws_url(self) -> str:
        """Convert the HTTP API URL to a WebSocket URL."""
        url = self._url.replace("https://", "wss://").replace("http://", "ws://")
        return f"{url}/websocket"
