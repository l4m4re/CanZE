# PyCanZE

PyCanZE is a Python spin-off of the CanZE project, an Android/iOS graphical
tool for Renault vehicles. The CSV data files from the original app are copied
here to support Python command-line tooling and experimentation.

The immediate aim is to poll selected vehicle registers and publish decoded
values over MQTT. A GUI similar to the original app may be built later.

## Current state

- Dataclasses and CSV parsers live in `models.py` and `parser.py`.
- A minimal UDS client in `uds.py` powers example utilities in `tools/` and
  `Testing/`.
- No MQTT interface or test suite is available yet.

Contributions are welcome as this module is under active development.

