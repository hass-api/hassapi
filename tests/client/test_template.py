from unittest.mock import patch

from hassapi.client.template import TemplateClient


@patch("hassapi.client.base.BaseClient.__init__", return_value=None)
def test_render_template(*args):
    with patch.object(TemplateClient, "_post", return_value="21.5") as mock_post:
        result = TemplateClient().render_template("{{ states('sensor.temp') }}")
    assert result == "21.5"
    mock_post.assert_called_once_with("template", template="{{ states('sensor.temp') }}")
