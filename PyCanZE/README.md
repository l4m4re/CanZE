# PyCanZE

PyCanZE is a Python spin-off of the [CanZE](../README.md) project, which
provides a graphical Android/iOS tool for Renault vehicles. This directory
houses a small Python package and companion scripts that use the CSV database
from CanZE to communicate with the car via an ELM327-compatible interface.

## Contents

* `pycanze/` – library with parsers and a minimal UDS client
* `tools/` – command-line utilities such as `scan_car.py` and
  `battery_health.py`
* `Testing/` – experimental scripts and prototypes including sweep harnesses

## Goals

The immediate aim is to poll selected diagnostic registers and publish the
decoded values over systems like MQTT. In the longer term a GUI similar to the
original CanZE app may be created. The Python UDS client mirrors the Android
app's AT initialisation sequence and offers tuning knobs for flow-control and
timing. An optional *wide CF fallback* widens receive filters and enables
``ATH1`` when LBC 0x21 pages miss consecutive frames.

## Usage

Example: scan all fields for a ZOE using a WiFi ELM327 dongle at the default
address::

    python tools/scan_car.py ZOE

Specify `--host` and `--port` if your dongle uses different settings. For
LBC/EVC snapshots run::

    python tools/battery_health.py ZOE

Use `--wide-cf-fallback` if your dongle occasionally drops ISO‑TP consecutive
frames from the LBC.

Contributions are welcome!

