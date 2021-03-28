"""Class for HASS API authentication."""


import os
from typing import Dict, Optional


class AuthenticatedClient:
    """Class for HASS API authentication."""

    def __init__(self, hassurl: Optional[str] = None, token: Optional[str] = None):
        """Create Authenticated client."""
        self._url = self._resolve_api_url(hassurl or os.environ["HASS_URL"])
        self._headers = self._get_headers(token or os.environ["HASS_TOKEN"])

    def _resolve_api_url(self, hassurl: str) -> str:
        """Resolve if needed and get full API url."""
        hassurl = hassurl.strip("/")
        if hassurl.endswith("api"):
            return hassurl
        return f"{hassurl}/api"

    def _get_headers(self, token: str) -> Dict:
        """Get request headers."""
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
