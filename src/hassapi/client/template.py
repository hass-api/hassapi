"""Client for functionality related to HASS templates."""

from .base import BaseClient


class TemplateClient(BaseClient):
    """Template Client."""

    def render_template(self, template: str) -> str:
        """Render Jinja2 template."""
        return self._post("template", template=template)  # type: ignore
