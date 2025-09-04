#!/usr/bin/env python3
"""Poll SOC/SOH/HV voltage/odometer and publish to MQTT every 5 minutes."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import paho.mqtt.client as mqtt

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parents[1]))
from pycanze import UDSClient  # type: ignore
from pycanze.parser import load_fields  # type: ignore

# Core SIDs
SID_SOC = "7ec.24.622002"
SID_SOC_MEM = "7ec.168.623415"
SID_SOH = "7ec.24.623206"
SID_HV_V = "7ec.24.623203"
SID_ODO = "7ec.24.623200"  # some datasets use 7ec.24.622006
SID_CHG_MODE = "7ec.30.6234dd"
SID_CHG_SET = "7ec.24.6234ad"
SID_HVAC_REQ = "7ec.31.6233cd"
SID_HEAT_REQ = "7ec.25.623328"
SID_KEY_STATE = "7ec.31.62200e"

POLL_SIDS = [
    SID_SOC,
    SID_SOC_MEM,
    SID_SOH,
    SID_HV_V,
    SID_ODO,
    SID_CHG_MODE,
    SID_CHG_SET,
    SID_HVAC_REQ,
    SID_HEAT_REQ,
    SID_KEY_STATE,
]


def _safe_read(client: UDSClient, sid: str) -> Optional[float]:
    """Read a SID; return None on benign errors."""

    try:
        val = client.read_field(sid)
        if isinstance(val, str):
            return None
        return val  # type: ignore[return-value]
    except (TimeoutError, socket.timeout):
        return None
    except (OSError, ConnectionError):
        raise
    except Exception:
        return None


def detect_state(vals: Dict[str, Optional[float]]) -> str:
    """Return vehicle state based on heuristic signals."""

    key = vals.get(SID_KEY_STATE)
    chg_mode = vals.get(SID_CHG_MODE)
    chg_set = vals.get(SID_CHG_SET)
    soc = vals.get(SID_SOC)
    hvac = vals.get(SID_HVAC_REQ)
    heat = vals.get(SID_HEAT_REQ)

    if key == 1:
        return "ready"
    if chg_mode == 2 or (chg_set is not None and chg_set > 0):
        return "charging"
    if soc == 0:
        if hvac == 1 or heat == 0:
            return "charger_connected_sleep"
        return "parked_sleep"
    return "parked"


def build_payload(vals: Dict[str, Optional[float]], state: str) -> Dict[str, object]:
    """Filter sentinel values and construct payload."""

    soc = vals.get(SID_SOC)
    soc_mem = vals.get(SID_SOC_MEM)
    if soc in (None, 0) and soc_mem not in (None, 0):
        soc = soc_mem

    soh = vals.get(SID_SOH)
    hv = vals.get(SID_HV_V)
    odo = vals.get(SID_ODO)

    data: Dict[str, object] = {"state": state}
    if soc not in (None, 0):
        data["soc"] = round(float(soc), 3)
    if soh is not None and soh <= 100:
        data["soh"] = round(float(soh), 3)
    if hv is not None and hv < 500:
        data["hv_voltage"] = round(float(hv), 3)
    if odo is not None:
        try:
            data["odometer"] = int(odo)
        except Exception:
            pass
    return data


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Poll EVC fields and publish over MQTT")
    p.add_argument("--host", default=os.environ.get("PYCANZE_HOST", "192.168.2.21"))
    p.add_argument("--port", type=int, default=int(os.environ.get("PYCANZE_PORT", "35000")))
    p.add_argument("--mqtt-host", default=os.environ.get("MQTT_HOST", "localhost"))
    p.add_argument("--mqtt-port", type=int, default=int(os.environ.get("MQTT_PORT", "1883")))
    p.add_argument("--mqtt-topic", default=os.environ.get("MQTT_TOPIC", "canze/metrics"))
    p.add_argument("--vehicle", default=os.environ.get("PYCANZE_VEHICLE"))
    p.add_argument("--interval", type=int, default=300, help="Polling interval in seconds")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    fields = load_fields(vehicle=args.vehicle)[0] if args.vehicle else load_fields()[0]
    client = UDSClient(args.host, port=args.port, fields=fields)
    mqtt_client = mqtt.Client()
    mqtt_client.connect(args.mqtt_host, args.mqtt_port)
    mqtt_client.loop_start()

    try:
        while True:
            vals = {sid: _safe_read(client, sid) for sid in POLL_SIDS}
            state = detect_state(vals)
            payload = build_payload(vals, state)
            payload["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            mqtt_client.publish(args.mqtt_topic, json.dumps(payload))
            time.sleep(args.interval)
    finally:
        try:
            client.close()
        finally:
            try:
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    main()
