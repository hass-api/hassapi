## [Home Assistant](https://www.home-assistant.io/) Web API Client for Python

## Examples
```python
from hassapi import Hass

hass = Hass(hassurl="http://IP_ADDRESS:8123/", token="YOUR_HASS_TOKEN")

hass.turn_on("light.bedroom_light")
hass.run_script("good_morning")
```
## Installation
```
pip install hassapi
```
