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

## PyCanZE (Python tools) roadmap

This repository also contains a Python toolkit under `PyCanZE/` used for command‑line polling and experiments (MQTT, HA integration, etc.). See `AGENTS.md` for a living roadmap, Codex analysis plan, and next goals including a 5‑minute MQTT poller (SoC/SOH/HV/odometer) and optional battery diagnostics snapshots.

### Known limitations (PyCanZE tools)

These apply to the Python command‑line tools under `PyCanZE/` and do not affect the Android app:

- No free‑frame capture yet: the tools do not use `ATMA` to sniff broadcast frames. They focus on on‑demand UDS reads (0x21/0x22). This mainly impacts “live dashboard” use cases that rely on high‑rate broadcast messages. It does not affect the planned Home Assistant integration or periodic snapshots (EVC‑based SoC/SOH/HV/odometer are supported).
- 11‑bit CAN only: extended (29‑bit) ISO‑TP addressing (`ATSP7` + `ATCP`) isn’t implemented yet. Legacy ZOE and Twingo 3 Ph2 battery ECUs use 11‑bit and are supported. ZOE Ph2 battery ECUs (e.g., LBC/LBC2 with 29‑bit IDs) are not yet reachable from the Python tools.

These gaps are intentional for now. Primary goal is HA integration and basic diagnostics; there’s no intent to build a live driving dashboard. If needed later, both features can be added behind flags with per‑ECU selection from the CSV database.

