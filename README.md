## [Home Assistant](https://www.home-assistant.io/) Web API Client for Python
[![PyPI - Downloads](https://img.shields.io/pypi/dm/hassapi?style=flat-square)](https://pypistats.org/packages/hassapi)

## Examples
```python
from hassapi import Hass

hass = Hass(hassurl="http://IP_ADDRESS:8123/", token="YOUR_HASS_TOKEN")

hass.turn_on("light.bedroom_light")
hass.run_script("good_morning")

# If you want to bypass certificate verification. Default set to True
hass = Hass(hassurl="http://IP_ADDRESS:8123/", token="YOUR_HASS_TOKEN", verify=False)
```
## Installation
```
pip install hassapi
```
