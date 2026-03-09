from unittest.mock import patch

import pytest

from hassapi.client.services import ServicesClient
from hassapi.models import ServiceList, StateList

MOCK_STATE = {
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {},
    "context": {"id": "abc", "parent_id": None, "user_id": None},
    "last_changed": "2024-01-01T00:00:00.000000+00:00",
    "last_updated": None,
    "last_reported": None,
}

MOCK_SERVICE = {"domain": "light", "services": {"turn_on": {}, "turn_off": {}}}


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_get_services(*args):
    with patch.object(ServicesClient, "_get", return_value=[MOCK_SERVICE]) as mock_get:
        result = ServicesClient().get_services()
    assert isinstance(result, ServiceList)
    mock_get.assert_called_once_with("services")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_call_service(*args):
    with patch.object(ServicesClient, "_post", return_value=[MOCK_STATE]) as mock_post:
        result = ServicesClient().call_service("turn_on", entity_id="light.living_room")
    assert isinstance(result, StateList)
    mock_post.assert_called_once_with(
        endpoint="/services/light/turn_on", entity_id="light.living_room"
    )


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_call_service_passes_kwargs(*args):
    with patch.object(ServicesClient, "_post", return_value=[MOCK_STATE]) as mock_post:
        ServicesClient().call_service("turn_on", entity_id="light.living_room", brightness=200)
    mock_post.assert_called_once_with(
        endpoint="/services/light/turn_on", entity_id="light.living_room", brightness=200
    )


@pytest.mark.parametrize("method", ["turn_on", "turn_off", "toggle"])
@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_toggle_methods(mock_init, method):
    with patch.object(ServicesClient, "call_service", return_value=StateList()) as mock_call:
        getattr(ServicesClient(), method)("light.living_room")
    mock_call.assert_called_once_with(method, entity_id="light.living_room")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_select_option(*args):
    with patch.object(ServicesClient, "call_service", return_value=StateList()) as mock_call:
        ServicesClient().select_option("input_select.mode", option="Away")
    mock_call.assert_called_once_with(
        "select_option", entity_id="input_select.mode", option="Away"
    )


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_set_value(*args):
    with patch.object(ServicesClient, "call_service", return_value=StateList()) as mock_call:
        ServicesClient().set_value("input_number.brightness", value=75)
    mock_call.assert_called_once_with("set_value", entity_id="input_number.brightness", value=75)


@pytest.mark.parametrize("method", ["open_cover", "close_cover"])
@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_cover_methods(mock_init, method):
    with patch.object(ServicesClient, "call_service", return_value=StateList()) as mock_call:
        getattr(ServicesClient(), method)("cover.garage")
    mock_call.assert_called_once_with(method, entity_id="cover.garage")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_set_cover_position(*args):
    with patch.object(ServicesClient, "call_service", return_value=StateList()) as mock_call:
        ServicesClient().set_cover_position("cover.garage", position=50)
    mock_call.assert_called_once_with("set_cover_position", entity_id="cover.garage", position=50)


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_run_script(*args):
    with patch.object(ServicesClient, "_post", return_value=[]) as mock_post:
        ServicesClient().run_script("good_morning")
    mock_post.assert_called_once_with("/services/script/good_morning")


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_run_shell_command(*args):
    with patch.object(ServicesClient, "_post", return_value=[]) as mock_post:
        ServicesClient().run_shell_command("backup")
    mock_post.assert_called_once_with("/services/shell_command/backup")
