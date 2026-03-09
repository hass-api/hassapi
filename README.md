# hassapi — Home Assistant Python API Client

[![CI](https://github.com/hass-api/hassapi/actions/workflows/ci.yml/badge.svg)](https://github.com/hass-api/hassapi/actions/workflows/ci.yml)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/hassapi?style=flat-square)](https://pypistats.org/packages/hassapi)
[![PyPI - Version](https://img.shields.io/pypi/v/hassapi?style=flat-square)](https://pypi.org/project/hassapi/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hassapi?style=flat-square)](https://pypi.org/project/hassapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

A Python client for the [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest).

---

## Installation

```bash
pip install hassapi
```

## Quick Start

```python
from hassapi import Hass

hass = Hass(hassurl="http://192.168.1.10:8123", token="YOUR_LONG_LIVED_TOKEN")

# Control devices
hass.turn_on("light.living_room")
hass.turn_off("switch.coffee_machine")
hass.toggle("light.bedroom")

# Read state
state = hass.get_state("sensor.temperature")
print(state.state)           # e.g. "21.5"
print(state.attributes)      # dict of entity attributes
print(state.last_changed)    # datetime

# Run a script
hass.run_script("good_morning")
```

## Configuration

### Constructor arguments

```python
hass = Hass(
    hassurl="http://IP_ADDRESS:8123",
    token="YOUR_HASS_TOKEN",
    verify=True,   # Set to False to skip TLS certificate verification (e.g. self-signed certs)
    timeout=3,     # Request timeout in seconds
)
```

### Environment variables

If `hassurl` or `token` are not passed, the client reads from environment variables:

```bash
export HASS_URL=http://192.168.1.10:8123
export HASS_TOKEN=your_long_lived_token
```

```python
hass = Hass()  # reads from env
```

---

## API Reference

### States

```python
# Get the state of a single entity
state: State = hass.get_state("light.living_room")

# Get states of all entities
states: StateList = hass.get_states()

# Set state and optionally attributes of an entity
state: State = hass.set_state("sensor.my_sensor", state="42", attributes={"unit": "°C"})
```

**`State` object fields:**

| Field | Type | Description |
|---|---|---|
| `entity_id` | `str` | Entity identifier |
| `state` | `str` | Current state value |
| `attributes` | `dict` | Entity attributes |
| `last_changed` | `datetime` | When state last changed |
| `last_updated` | `datetime` | When state was last updated |
| `context` | `Context` | Context (id, parent_id, user_id) |

---

### Services

```python
# Call any service
hass.call_service("turn_on", entity_id="light.living_room", brightness=200)

# Convenience methods
hass.turn_on("light.living_room")
hass.turn_off("switch.fan")
hass.toggle("light.bedroom")

# Covers
hass.open_cover("cover.garage")
hass.close_cover("cover.garage")
hass.set_cover_position("cover.garage", position=50)

# Input entities
hass.select_option("input_select.mode", option="Away")
hass.set_value("input_number.brightness", value=75)

# Scripts and shell commands
hass.run_script("good_morning")
hass.run_shell_command("backup")

# List all available services
services: ServiceList = hass.get_services()
```

---

### Events

```python
# List all registered event listeners
events: EventList = hass.get_events()

# Fire an event
hass.fire_event("MY_CUSTOM_EVENT")
hass.fire_event("MY_CUSTOM_EVENT", event_data={"key": "value"})
```

---

### Templates

```python
# Render a Jinja2 template
result: str = hass.render_template("{{ states('sensor.temperature') }}")
```

---

## Getting a Long-Lived Access Token

1. Open Home Assistant in your browser
2. Go to your profile: **Settings → Your profile → Security**
3. Scroll to **Long-lived access tokens** and create one

---

## Contributing

```bash
# Install dev dependencies and run all checks
pip install tox
tox
```

Individual environments:

```bash
tox -e pytest        # run tests
tox -e flake8        # lint
tox -e mypy          # type check
tox -e format        # auto-format code
tox -e format-check  # check formatting without modifying
```

---

## License

[MIT](LICENSE)
