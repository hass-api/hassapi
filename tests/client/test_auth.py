from unittest.mock import patch

import pytest
from hassapi.client.auth import AuthenticatedClient


@patch("hassapi.client.auth.AuthenticatedClient._get_headers", return_value={"a": "b"})
@patch("hassapi.client.auth.AuthenticatedClient._resolve_api_url", return_value="MOCK URL")
def test_base_client_init(mock_get_headers, mock_resolve_api_url):
    client = AuthenticatedClient(hassurl="MOCK URL", token="MOCK TOKEN")
    assert client._url == "MOCK URL"
    assert client._headers == {"a": "b"}


@pytest.mark.parametrize(
    "given, expected",
    [
        ("ADDRESS:8123/", "ADDRESS:8123/api"),
        ("ADDRESS:8123/api/", "ADDRESS:8123/api"),
        ("ADDRESS:8123/api", "ADDRESS:8123/api"),
    ],
)
def test__resolve_api_url(given, expected):
    assert AuthenticatedClient()._resolve_api_url(given) == expected


def test_get_headers(*args):
    assert AuthenticatedClient()._get_headers("MOCK TOKEN") == {
        "Authorization": f"Bearer MOCK TOKEN",
        "Content-Type": "application/json",
    }
