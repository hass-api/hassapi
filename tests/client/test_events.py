from unittest.mock import patch

from hassapi.client.events import EventsClient
from hassapi.models import EventList

MOCK_EVENT = {"event": "state_changed", "listener_count": 5}


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_get_events(*args):
    with patch.object(EventsClient, "_get", return_value=[MOCK_EVENT]) as mock_get:
        result = EventsClient().get_events()
    assert isinstance(result, EventList)
    mock_get.assert_called_once_with("events")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_fire_event(*args):
    with patch.object(
        EventsClient, "_post", return_value={"message": "Event fired."}
    ) as mock_post:
        result = EventsClient().fire_event("MY_EVENT")
    assert result == "Event fired."
    mock_post.assert_called_once_with("events/MY_EVENT", json=None)


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_fire_event_with_data(*args):
    data = {"key": "value"}
    with patch.object(
        EventsClient, "_post", return_value={"message": "Event fired."}
    ) as mock_post:
        EventsClient().fire_event("MY_EVENT", event_data=data)
    mock_post.assert_called_once_with("events/MY_EVENT", json=data)
