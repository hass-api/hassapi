"""Class for basic API client functionality."""

import json
from typing import Dict, List, Optional, Union

import requests

from hassapi.exceptions import ClientError, get_error

from .auth import AuthenticatedClient

JsonResponseType = Union[Dict, List, str]
HassValueType = Union[int, float, str, bool]


class BaseClient(AuthenticatedClient):
    """Class for basic API client functionality."""

    def __init__(
        self, hassurl: Optional[str] = None, token: Optional[str] = None, verify: bool = True, timeout: float = 3
    ):
        """Create Base Client object.

        Args:
            hassurl: Home Assistant url e.g. http://localhost:8123
            token: Home Assistant token
            verify: True or False verify secure connection
        """
        super().__init__(hassurl, token, verify)
        self._timeout = timeout
        self._assert_api_running()

    def _assert_api_running(self) -> None:
        """Raise error if HASS API is not running."""
        if not self._api_is_running():
            raise ClientError("Home Assistant API is not running.")

    def _api_is_running(self) -> bool:
        """Check if Home Assistant API is running."""
        try:
            return self._get("/")["message"] == "API running."  # type: ignore
        except requests.exceptions.ConnectionError:
            return False

    def _get(
        self, endpoint: str, params: Optional[Dict] = None, **kwargs: HassValueType
    ) -> JsonResponseType:
        """Send GET request to HASS API `endpoint`."""
        return self._process_response(
            requests.get(
                url=self._get_url(endpoint),
                headers=self._headers,
                timeout=self._timeout,
                params={**(params or {}), **kwargs} or None,
                verify=self._verify,
            )
        )

    def _post(
        self, endpoint: str, json: Optional[Dict] = None, **kwargs: HassValueType
    ) -> JsonResponseType:
        """Send POST request to home HASS API `endpoint`."""
        return self._process_response(
            requests.post(
                url=self._get_url(endpoint),
                headers=self._headers,
                timeout=self._timeout,
                json={**(json or {}), **kwargs} or None,
                verify=self._verify,
            )
        )

    def _get_url(self, endpoint: str) -> str:
        """Get full endpoint url."""
        return f"{self._url}/{endpoint.strip('/')}"

    def _process_response(self, response: requests.Response) -> JsonResponseType:  # type: ignore
        """Validate response status and return response dict if ok."""
        if response.ok:
            try:
                return response.json()  # type: ignore
            except json.JSONDecodeError:
                return response.text
        else:
            self._raise_error(response.status_code, response.url)

    def _raise_error(self, status_code: int, url: str) -> None:
        """Raise custom error with description."""
        error = get_error(status_code)
        raise error(f"{status_code} status code returned from {url}",)  # type: ignore
