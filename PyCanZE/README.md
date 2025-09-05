# PyCanZE

PyCanZE is a Python spin-off of the [CanZE](../README.md) project, which
provides a graphical Android/iOS tool for Renault vehicles. This directory
houses a small Python package and companion scripts that use the CSV database
from CanZE to communicate with the car via an ELM327-compatible interface.

## Contents

* `pycanze/` – library with parsers, a minimal UDS client, and CLI tools
* `Testing/` – experimental logs and prototypes including sweep harnesses

## Goals

The immediate aim is to poll selected diagnostic registers and publish the
decoded values over systems like MQTT. In the longer term a GUI similar to the
original CanZE app may be created. The Python UDS client mirrors the Android
app's AT initialisation sequence and offers tuning knobs for flow-control and
timing. An optional *wide CF fallback* widens receive filters and enables
``ATH1`` when LBC 0x21 pages miss consecutive frames.

## Non-modifying policy

All PyCanZE libraries and tools operate in a read-only manner. UDS services or
other commands that could alter vehicle state are intentionally excluded. Any
future write capability would need explicit safety mechanisms and review before
being enabled.

### Read-only SID audit

The repository includes `tools/audit_readonly.py` which scans the
`pycanze/data` CSVs and Python sources for diagnostic services. CI runs this
audit and fails the build if a non read-only service is introduced. Run
`python tools/audit_readonly.py` from the repository root before submitting
changes.

## Build

From this directory install the package with `pip`::

    pip install .

Add WiFi dongle support (``python-OBD-wifi``) via the optional ``wifi`` extra::

    pip install .[wifi]

## Usage

Example: scan all fields for a ZOE using a WiFi ELM327 dongle at the default
address::

    python -m pycanze.scan_car ZOE

Specify `--host` and `--port` if your dongle uses different settings. For
LBC/EVC snapshots run::

    python -m pycanze.battery_health ZOE

Use `--wide-cf-fallback` if your dongle occasionally drops ISO‑TP consecutive
frames from the LBC.

For periodic MQTT publishing run::

    python -m pycanze.mqtt_poller --mqtt-host 192.168.1.10 --mqtt-topic canze/zoe

The poller reads SoC, SoH, HV voltage and the odometer every 5 minutes,
skipping sentinel values based on vehicle state heuristics.  To persist each
payload before publishing, supply a CSV or SQLite target::

    python -m pycanze.mqtt_poller --mqtt-host 192.168.1.10 \
        --log-csv metrics.csv --log-rotate 1024

Settings can also be supplied in a YAML or JSON file via ``--config``::

    # mqtt.yml
    interval: 60
    mqtt_host: broker.local
    mqtt_topic: canze/zoe
    fields:
      - 7ec.24.622002  # SOC
      - 7ec.24.623206  # SOH
      - 7ec.24.623203  # HV voltage
      - 7ec.24.623200  # odometer
    log_csv: metrics.csv

Then run::

    python -m pycanze.mqtt_poller --config mqtt.yml

Command-line options override values from the configuration file.

For standalone logging of arbitrary fields use the helper in `tools/`::

    python PyCanZE/tools/logger.py --fields 7ec.24.622002 7ec.24.623206 \
        --csv ev.csv --rotate 1024

Use `--sqlite` instead of `--csv` to write into a SQLite database.

### Lean EV poller with Shelly energy

The lean poller logs SoC/SoH/odo and robust charge/connection states at short intervals, and optionally fetches Shelly power metrics. It now also logs the Shelly cumulative wall energy as `shelly_aenergy_total_Wh` (Wh), which the analyzer prefers for accurate kWh.

Run it either as a module or directly:

    python -m pycanze.pycanze_poller --shelly-url http://192.168.2.14/rpc/Shelly.GetStatus

or from its folder:

    python PyCanZE/pycanze/pycanze_poller.py --shelly-url http://192.168.2.14/rpc/Shelly.GetStatus

CSV logs are written under `PyCanZE/Testing/logs/` by default. The `tools/analyze_charge_rates.py` script will auto‑use the cumulative energy column when present.

### Web log dashboard

`tools/log_dashboard.py` exposes recent samples and simple charts over HTTP.
It reads the rotating CSV/SQLite logs produced by `logger.py` and does not send
any commands to the vehicle.

Install dependencies and start the logger and dashboard::

    pip install flask
    python PyCanZE/tools/logger.py --fields 7ec.24.622002 7ec.24.623203 \
        --csv ev.csv --rotate 1024
    python PyCanZE/tools/log_dashboard.py --csv ev.csv --host 0.0.0.0 --port 8000

Open ``http://localhost:8000/`` for charts of SOC and HV voltage. The server is
read‑only and should run on a trusted network.

Contributions are welcome!

## PyCanZE (Python tools) roadmap

This repository also contains a Python toolkit under `PyCanZE/` used for command‑line polling and experiments (MQTT, HA integration, etc.). See `AGENTS.md` for a living roadmap, Codex analysis plan, and next goals including a 5‑minute MQTT poller (SoC/SOH/HV/odometer) and optional battery diagnostics snapshots.

### Known limitations (PyCanZE tools)

These apply to the Python command‑line tools under `PyCanZE/` and do not affect the Android app:

- Raw frame sniffing via `tools/sniff_frames.py` uses `ATMA` to monitor bus traffic. It does not perform ISO‑TP reassembly and is read‑only (no frame injection).
- 11‑bit CAN only: extended (29‑bit) ISO‑TP addressing (`ATSP7` + `ATCP`) isn’t implemented yet. Legacy ZOE and Twingo 3 Ph2 battery ECUs use 11‑bit and are supported. ZOE Ph2 battery ECUs (e.g., LBC/LBC2 with 29‑bit IDs) are not yet reachable from the Python tools.

These gaps are intentional for now. Primary goal is HA integration and basic diagnostics; there’s no intent to build a live driving dashboard. If needed later, both features can be added behind flags with per‑ECU selection from the CSV database.


## ECU responsiveness by state (observed)

Based on four fullscans in `Testing/logs/` (ready, charging, charger‑connected sleep, sleep; 2025‑08‑31/2025‑09‑01), ECU sections are present in all states; practical differences come from which DIDs return sane values. The matrix below summarizes what reliably responds per state and highlights a useful “awake probe”.

| ECU | Ready | Charging | Connected sleep | Sleep | Notes |
|---|---|---|---|---|---|
| EVC (0x7EC) | responds | responds | responds | responds | Key signals differ by state: SOC 622002 > 0 when awake; 0 in sleep. SOH 623206 sane (≤100) when awake; 126% in sleep. Charge setpoint 6234AD > 0 only while charging. Mode status 6234DC: 1=ready, 2=charging, 0=sleep. |
| LBC + LBC2 (0x7BB/0x7B6) | 6180 OK | 6180 OK | header only (no 6180) | header only (no 6180) | Identification DID 0x6180 returns in ready/charging but not in either sleep state. This makes LBC2 6180 a good “ECU‑awake probe.” |
| BCB‑OBC, DCM, EPS, HVAC, PEB, Parking‑Sonar, TDB, UBP, UCH, USM, VFC | responds | responds | responds | responds | Sections present across states; some modules return fewer/zero meaningful DIDs in sleep (typical). |

Practical takeaways
- Treat “sleep” and “charger‑connected sleep” as the same for polling: EVC DIDs are reachable but many contents read as “sleep signatures” (e.g., SOC=0, SOH>100). LBC/LBC2 identification 6180 does not respond in sleep.
- For state detection, prefer DIDs over ECU section presence. The poller brackets each cycle with LBC2 0x6180 identification reads: 7bb.56.6180 at the start and 7bb.200.6180 at the end. If both respond, the car is considered awake; if either is absent, it is sleeping. If the two probes disagree (state changed during the poll), the sample is discarded.
  Charging is detected via 6234AD/6234DC/6234DD and evaluated only when awake. EVSE presence is inferred from plug 6233EA with validity 6233BD and detected 62339D (earth‑only 623108 ignored). A latched connection flag persists across sleep and resets on offline.

