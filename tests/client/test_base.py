import unittest
from unittest.mock import patch

import pytest
from hassapi.client.base import BaseClient
from hassapi.exceptions import ClientError


class MockResponse:

    url = ""

    def __init__(self, return_value={}, status_code=200):
        self.return_value = return_value
        self.status_code = status_code

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return self.return_value


class MockError(Exception):
    """Mock Error for testing."""


@patch("hassapi.client.base.BaseClient._assert_api_running")
@patch("hassapi.client.base.AuthenticatedClient.__init__")
def test_base_client_init(mock_auth_client_init, mock_assert_api_running):
    assert BaseClient(timeout=2)._timeout == 2
    mock_auth_client_init.assert_called_once()
    mock_assert_api_running.assert_called_once()


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
@patch("hassapi.client.base.BaseClient._api_is_running", return_value=False)
def test_assert_api_running(mock_api_is_running, *args):
    with pytest.raises(ClientError):
        BaseClient()._assert_api_running()


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
@patch("hassapi.client.base.BaseClient._get", return_value={"message": "API running."})
def test_api_is_running(mock_get, *args):
    assert BaseClient()._api_is_running()


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
@patch("hassapi.client.base.BaseClient._get", return_value={"message": ""})
def test_api_is_not_running(mock_get, *args):
    assert not BaseClient()._api_is_running()


@patch("hassapi.client.base.BaseClient._assert_api_running")
@patch("hassapi.client.base.BaseClient._process_response", return_value={"a": "b"})
@patch("hassapi.client.base.requests.get")
@patch("hassapi.client.base.BaseClient._get_url")
def test_base_client_get(*args):
    assert {"a": "b"} == BaseClient()._get("some endpoint")
    for mock in args:
        mock.assert_called_once()


@patch("hassapi.client.base.BaseClient._assert_api_running")
@patch("hassapi.client.base.BaseClient._process_response", return_value={"a": "b"})
@patch("hassapi.client.base.requests.post")
@patch("hassapi.client.base.BaseClient._get_url")
def test_base_client_post(*args):
    assert {"a": "b"} == BaseClient()._post("some endpoint")
    for mock in args:
        mock.assert_called_once()


@patch("hassapi.client.base.BaseClient._assert_api_running")
def test_get_url(*args):
    assert BaseClient(hassurl="URL")._get_url("/ENDPOINT") == "URL/api/ENDPOINT"


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_process_response_ok(*args):
    response = MockResponse({"a": "b"}, status_code=200)
    assert BaseClient()._process_response(response) == {"a": "b"}


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
@patch("hassapi.client.base.BaseClient._raise_error")
def test_process_response_error(mock_raise_error, *args):
    response = MockResponse({"a": "b"}, status_code=400)
    BaseClient()._process_response(response)
    mock_raise_error.assert_called_once()


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
@patch("hassapi.client.base.get_error", return_value=MockError)
def test_raise_error(*args):
    client = BaseClient()
    with pytest.raises(MockError):
        client._raise_error(status_code=666, url="")
