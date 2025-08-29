# PyCanZE

PyCanZE is a Python spin-off of the [CanZE](../README.md) project, which
provides a graphical Android/iOS tool for Renault vehicles. This directory
houses a small Python package and companion scripts that use the CSV database
from CanZE to communicate with the car via an ELM327-compatible interface.

## Contents

* `pycanze/` – library with parsers and a minimal UDS client
* `tools/` – command-line utilities such as `scan_car.py`
* `Testing/` – experimental scripts and prototypes

## Goals

The immediate aim is to poll selected diagnostic registers and publish the
decoded values over systems like MQTT. In the longer term a GUI similar to the
original CanZE app may be created.

## Usage

Example: scan all fields for a ZOE using a WiFi ELM327 dongle at the default
address::

    python tools/scan_car.py ZOE

Specify `--host` and `--port` if your dongle uses different settings.

Contributions are welcome!

