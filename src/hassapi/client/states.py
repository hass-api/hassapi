"""Client for functionality related to HASS states."""

from typing import Optional

from hassapi.models import State, StateList

from .base import BaseClient, HassDictType, HassValueType


class StatesClient(BaseClient):
    """States Client."""

    def get_state(self, entity_id: str) -> State:
        """Get ``entity_id`` state."""
        return State(**self._get(f"states/{entity_id}"))  # type: ignore

    def set_state(
        self, entity_id: str, state: HassValueType, attributes: Optional[HassDictType] = None
    ) -> State:
        """Set ``entity_id`` state and optionally attributes."""
        if attributes:
            return State(**self._post(f"states/{entity_id}", state=state, attributes=attributes))  # type: ignore
        return State(**self._post(f"states/{entity_id}", state=state))  # type: ignore

    def get_states(self) -> StateList:
        """Get states of all entities."""
        return StateList(self._get("states"))
