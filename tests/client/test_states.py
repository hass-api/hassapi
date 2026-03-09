from unittest.mock import patch

from hassapi.client.states import StatesClient
from hassapi.models import State, StateList

MOCK_STATE = {
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {"brightness": 200},
    "context": {"id": "abc", "parent_id": None, "user_id": None},
    "last_changed": "2024-01-01T00:00:00.000000+00:00",
    "last_updated": "2024-01-01T00:00:00.000000+00:00",
    "last_reported": None,
}


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_get_state(*args):
    with patch.object(StatesClient, "_get", return_value=MOCK_STATE) as mock_get:
        result = StatesClient().get_state("light.living_room")
    assert isinstance(result, State)
    assert result.entity_id == "light.living_room"
    assert result.state == "on"
    mock_get.assert_called_once_with("states/light.living_room")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_get_states(*args):
    with patch.object(StatesClient, "_get", return_value=[MOCK_STATE]) as mock_get:
        result = StatesClient().get_states()
    assert isinstance(result, StateList)
    assert len(result) == 1
    mock_get.assert_called_once_with("states")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_set_state(*args):
    with patch.object(StatesClient, "_post", return_value=MOCK_STATE) as mock_post:
        result = StatesClient().set_state("light.living_room", "on")
    assert isinstance(result, State)
    mock_post.assert_called_once_with("states/light.living_room", state="on")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_set_state_with_attributes(*args):
    attrs = {"brightness": 200}
    with patch.object(StatesClient, "_post", return_value=MOCK_STATE) as mock_post:
        result = StatesClient().set_state("light.living_room", "on", attributes=attrs)
    assert isinstance(result, State)
    mock_post.assert_called_once_with(
        "states/light.living_room", json={"state": "on", "attributes": attrs}
    )
