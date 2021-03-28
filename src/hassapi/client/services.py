"""Client for functionality related to calling HASS services."""

from typing import Union

from .base import BaseClient, HassValueType, JsonResponseType


class ServicesClient(BaseClient):
    """Services Client."""

    def call_service(
        self, service: str, entity_id: str, **kwargs: HassValueType
    ) -> JsonResponseType:
        """Call Home Assistant Service.

        Args:
            service: HASS service e.g. turn_on, toggle
            entity_id: HASS entity e.g. light.living_room
            kwargs: additional service data
        """
        domain = entity_id.split(".")[0]

        return self._post(
            endpoint=f"/services/{domain}/{service}", entity_id=entity_id, **kwargs  # type: ignore
        )

    def turn_on(self, entity_id: str) -> JsonResponseType:
        """Call 'turn_on' service for `entity_id`."""
        return self.call_service("turn_on", entity_id=entity_id)

    def turn_off(self, entity_id: str) -> JsonResponseType:
        """Call 'turn_off' service for `entity_id`."""
        return self.call_service("turn_off", entity_id=entity_id)

    def toggle(self, entity_id: str) -> JsonResponseType:
        """Call 'toggle' service for `entity_id`."""
        return self.call_service("toggle", entity_id=entity_id)

    def select_option(self, entity_id: str, option: str) -> JsonResponseType:
        """Call 'select_option' service for `entity_id`."""
        return self.call_service("select_option", entity_id=entity_id, option=option)

    def set_value(self, entity_id: str, value: Union[int, float, str]) -> JsonResponseType:
        """Call 'set_value' service for `entity_id`."""
        return self.call_service("set_value", entity_id=entity_id, value=value)

    def open_cover(self, entity_id: str) -> JsonResponseType:
        """Call 'open_cover' service for `entity_id`."""
        return self.call_service("open_cover", entity_id=entity_id)

    def close_cover(self, entity_id: str) -> JsonResponseType:
        """Call 'close_cover' service for `entity_id`."""
        return self.call_service("close_cover", entity_id=entity_id)

    def set_cover_position(self, entity_id: str, position: int) -> JsonResponseType:
        """Call 'set_cover_position' service for `entity_id`."""
        return self.call_service("close_cover", entity_id=entity_id, position=position)

    def run_script(self, script_id: str) -> JsonResponseType:
        """Run HASS-defined script."""
        return self._post(f"/services/script/{script_id}")

    def run_shell_command(self, command: str) -> JsonResponseType:
        """Run HASS-defined shell command."""
        return self._post(f"/services/shell_command/{command}")
