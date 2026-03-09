import json
import time
from unittest.mock import MagicMock, patch

import pytest
import websocket

from hassapi.client.websocket import _MAX_RETRIES, _RESET_AFTER, WebSocketClient
from hassapi.exceptions import ClientError


def make_client():
    """Create a WebSocketClient with auth bypassed."""
    with patch("hassapi.client.auth.AuthenticatedClient.__init__", return_value=None):
        client = WebSocketClient()
    client._token = "test_token"
    client._url = "http://192.168.1.1:8123/api"
    return client


# --- URL conversion ---


def test_get_ws_url_http():
    assert make_client()._get_ws_url() == "ws://192.168.1.1:8123/api/websocket"


def test_get_ws_url_https():
    client = make_client()
    client._url = "https://192.168.1.1:8123/api"
    assert client._get_ws_url() == "wss://192.168.1.1:8123/api/websocket"


# --- create_ws_app ---


def test_create_ws_app_returns_websocket_app():
    client = make_client()
    app = client._create_ws_app()
    assert isinstance(app, websocket.WebSocketApp)


# --- subscribe_to_events ---


def test_subscribe_to_events_registers_subscription():
    client = make_client()
    callback = MagicMock()
    with patch.object(client, "_ensure_connected"):
        client.subscribe_to_events(callback)
    sub = list(client._subscriptions.values())[0]
    assert sub["callback"] is callback
    assert sub["entity_id"] is None
    assert sub["msg"]["type"] == "subscribe_events"
    assert "event_type" not in sub["msg"]


def test_subscribe_to_events_with_event_type():
    client = make_client()
    with patch.object(client, "_ensure_connected"):
        client.subscribe_to_events(MagicMock(), event_type="call_service")
    sub = list(client._subscriptions.values())[0]
    assert sub["msg"]["event_type"] == "call_service"


def test_subscribe_to_events_assigns_incrementing_ids():
    client = make_client()
    with patch.object(client, "_ensure_connected"):
        client.subscribe_to_events(MagicMock())
        client.subscribe_to_events(MagicMock())
    ids = list(client._subscriptions.keys())
    assert ids == [1, 2]


# --- subscribe_to_state_changes ---


def test_subscribe_to_state_changes_registers_subscription():
    client = make_client()
    with patch.object(client, "_ensure_connected"):
        client.subscribe_to_state_changes(MagicMock())
    sub = list(client._subscriptions.values())[0]
    assert sub["msg"]["event_type"] == "state_changed"
    assert sub["entity_id"] is None


def test_subscribe_to_state_changes_with_entity_id():
    client = make_client()
    with patch.object(client, "_ensure_connected"):
        client.subscribe_to_state_changes(MagicMock(), entity_id="light.living_room")
    sub = list(client._subscriptions.values())[0]
    assert sub["entity_id"] == "light.living_room"


def test_add_subscription_sends_immediately_when_authenticated():
    client = make_client()
    client._authenticated = True
    client._ws = MagicMock()
    with patch.object(client, "_ensure_connected"):
        client.subscribe_to_events(MagicMock())
    client._ws.send.assert_called_once()
    sent = json.loads(client._ws.send.call_args[0][0])
    assert sent["type"] == "subscribe_events"


# --- ensure_connected ---


def test_ensure_connected_starts_thread_when_none():
    client = make_client()
    with patch.object(client, "_create_ws_app", return_value=MagicMock()), patch(
        "hassapi.client.websocket.threading.Thread"
    ) as MockThread:
        mock_thread = MagicMock()
        MockThread.return_value = mock_thread
        client._ensure_connected()
    mock_thread.start.assert_called_once()


def test_ensure_connected_does_not_restart_alive_thread():
    client = make_client()
    mock_thread = MagicMock()
    mock_thread.is_alive.return_value = True
    client._thread = mock_thread
    with patch("hassapi.client.websocket.threading.Thread") as MockThread:
        client._ensure_connected()
    MockThread.assert_not_called()


# --- unsubscribe ---


def test_unsubscribe_sends_unsubscribe_messages():
    client = make_client()
    client._ws = MagicMock()
    client._authenticated = True
    client._subscriptions = {1: {"msg": {"id": 1, "type": "subscribe_events"}}}
    client.unsubscribe()
    client._ws.send.assert_called_once()
    sent = json.loads(client._ws.send.call_args[0][0])
    assert sent["type"] == "unsubscribe_events"
    assert sent["subscription"] == 1


def test_unsubscribe_closes_ws():
    client = make_client()
    client._ws = MagicMock()
    client._authenticated = True
    client._subscriptions = {1: {"msg": {}}}
    client.unsubscribe()
    client._ws.close.assert_called_once()


def test_unsubscribe_clears_subscriptions():
    client = make_client()
    client._ws = MagicMock()
    client._subscriptions = {1: {}, 2: {}}
    client.unsubscribe()
    assert len(client._subscriptions) == 0


def test_unsubscribe_skips_send_when_not_authenticated():
    client = make_client()
    client._ws = MagicMock()
    client._authenticated = False
    client._subscriptions = {1: {"msg": {}}}
    client.unsubscribe()
    client._ws.send.assert_not_called()
    client._ws.close.assert_called_once()


# --- _on_open ---


def test_on_open_sets_connected_at():
    client = make_client()
    assert client._connected_at is None
    client._on_open(MagicMock())
    assert client._connected_at is not None


# --- _on_message ---


def test_on_message_auth_required_sends_auth():
    client = make_client()
    mock_ws = MagicMock()
    client._on_message(mock_ws, json.dumps({"type": "auth_required"}))
    mock_ws.send.assert_called_once()
    sent = json.loads(mock_ws.send.call_args[0][0])
    assert sent["type"] == "auth"
    assert sent["access_token"] == "test_token"


def test_on_message_auth_ok_sets_authenticated_and_sends_subscriptions():
    client = make_client()
    mock_ws = MagicMock()
    msg = {"id": 1, "type": "subscribe_events"}
    client._subscriptions = {1: {"msg": msg, "callback": MagicMock(), "entity_id": None}}
    client._on_message(mock_ws, json.dumps({"type": "auth_ok"}))
    assert client._authenticated is True
    mock_ws.send.assert_called_once_with(json.dumps(msg))


def test_on_message_auth_invalid_raises_and_stops():
    client = make_client()
    mock_ws = MagicMock()
    with pytest.raises(ClientError):
        client._on_message(mock_ws, json.dumps({"type": "auth_invalid"}))
    assert client._stopping is True
    mock_ws.close.assert_called_once()


def test_on_message_event_calls_dispatch():
    client = make_client()
    event = {"event_type": "state_changed", "data": {}}
    msg = json.dumps({"type": "event", "id": 1, "event": event})
    with patch.object(client, "_dispatch") as mock_dispatch:
        client._on_message(MagicMock(), msg)
    mock_dispatch.assert_called_once()


# --- _dispatch ---


def test_dispatch_calls_callback():
    client = make_client()
    callback = MagicMock()
    event = {"event_type": "state_changed", "data": {}}
    client._subscriptions = {1: {"callback": callback, "entity_id": None}}
    client._dispatch({"id": 1, "event": event})
    callback.assert_called_once_with(event)


def test_dispatch_entity_id_filter_match():
    client = make_client()
    callback = MagicMock()
    event = {"data": {"entity_id": "light.living_room"}}
    client._subscriptions = {1: {"callback": callback, "entity_id": "light.living_room"}}
    client._dispatch({"id": 1, "event": event})
    callback.assert_called_once()


def test_dispatch_entity_id_filter_no_match():
    client = make_client()
    callback = MagicMock()
    event = {"data": {"entity_id": "light.bedroom"}}
    client._subscriptions = {1: {"callback": callback, "entity_id": "light.living_room"}}
    client._dispatch({"id": 1, "event": event})
    callback.assert_not_called()


def test_dispatch_unknown_subscription_id_is_ignored():
    client = make_client()
    client._subscriptions = {}
    client._dispatch({"id": 99, "event": {}})  # should not raise


# --- _on_error / _on_close ---


def test_on_error_does_not_raise():
    client = make_client()
    client._on_error(MagicMock(), Exception("Connection refused"))


def test_on_close_resets_authenticated():
    client = make_client()
    client._authenticated = True
    client._on_close(MagicMock(), 1000, "Normal closure")
    assert client._authenticated is False


# --- _run_with_retry ---


def test_run_with_retry_does_not_run_when_already_stopping():
    client = make_client()
    mock_ws = MagicMock()
    client._ws = mock_ws
    client._stopping = True
    client._run_with_retry()
    mock_ws.run_forever.assert_not_called()


def test_run_with_retry_retries_on_disconnect():
    client = make_client()
    mock_ws = MagicMock()
    calls = [0]

    def run_forever():
        calls[0] += 1
        if calls[0] >= 3:
            client._stopping = True

    mock_ws.run_forever.side_effect = run_forever
    client._ws = mock_ws
    with patch.object(client, "_create_ws_app", return_value=mock_ws), patch(
        "hassapi.client.websocket.time.sleep"
    ):
        client._run_with_retry()
    assert mock_ws.run_forever.call_count == 3


def test_run_with_retry_gives_up_after_max_retries():
    client = make_client()
    mock_ws = MagicMock()
    client._ws = mock_ws
    with patch.object(client, "_create_ws_app", return_value=mock_ws), patch(
        "hassapi.client.websocket.time.sleep"
    ):
        client._run_with_retry()
    assert mock_ws.run_forever.call_count == _MAX_RETRIES + 1


def test_run_with_retry_resets_counter_on_long_connection():
    client = make_client()
    mock_ws = MagicMock()
    calls = [0]

    def run_forever():
        calls[0] += 1
        # Simulate a long-lived connection on the 4th call
        if calls[0] == 4:
            client._connected_at = time.monotonic() - _RESET_AFTER - 1

    mock_ws.run_forever.side_effect = run_forever
    client._ws = mock_ws
    with patch.object(client, "_create_ws_app", return_value=mock_ws), patch(
        "hassapi.client.websocket.time.sleep"
    ):
        client._run_with_retry()
    # Without reset: _MAX_RETRIES + 1 = 6. With reset at call 4: 9.
    assert mock_ws.run_forever.call_count > _MAX_RETRIES + 1
