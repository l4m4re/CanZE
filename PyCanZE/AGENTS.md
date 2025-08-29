# PyCanZE

PyCanZE is an experimental Python port of the CanZE project. It aims to parse the CSV asset files used by the Android app and provide a flexible foundation for polling vehicle data via standard ELM327-compatible interfaces. The long-term goal is to offer command-line and library tools that can publish decoded values to automation systems such as MQTT/Home Assistant.

## Current state

- Basic models and a CSV asset parser are implemented in `parser.py` and `models.py`.
- Raw UDS communication helpers exist in `uds.py` but there is no generic polling client yet.
- No MQTT interface, command-line utility or test suite has been added so far.

Contributions are welcome as this module is under active development.
