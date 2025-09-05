#!/usr/bin/env python3
"""Poll SOC/SOH/HV voltage/odometer and publish to MQTT every 5 minutes."""

from __future__ import annotations

import argparse
import json
import os
import socket
import time
from pathlib import Path
from typing import Optional

import paho.mqtt.client as mqtt

from pycanze import UDSClient  # type: ignore
from pycanze.config import load_config  # type: ignore
from pycanze.parser import load_fields  # type: ignore
from pycanze.state import POLL_SIDS, build_payload, detect_state


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




def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Poll EVC fields and publish over MQTT")
    p.add_argument("--config", type=Path, help="YAML/JSON configuration file")
    p.add_argument("--host", default=os.environ.get("PYCANZE_HOST", "192.168.2.21"))
    p.add_argument("--port", type=int, default=int(os.environ.get("PYCANZE_PORT", "35000")))
    p.add_argument("--mqtt-host", default=os.environ.get("MQTT_HOST", "localhost"))
    p.add_argument("--mqtt-port", type=int, default=int(os.environ.get("MQTT_PORT", "1883")))
    p.add_argument("--mqtt-topic", default=os.environ.get("MQTT_TOPIC", "canze/metrics"))
    p.add_argument("--vehicle", default=os.environ.get("PYCANZE_VEHICLE"))
    p.add_argument("--interval", type=int, default=300, help="Polling interval in seconds")
    p.add_argument("--fields", nargs="+", help="Field identifiers to poll")
    p.add_argument("--log-csv", type=Path, help="Optional CSV log file")
    p.add_argument("--log-sqlite", type=Path, help="Optional SQLite log database")
    p.add_argument(
        "--log-rotate",
        type=int,
        help="Rotate logs when files exceed this size in kB",
    )
    args = p.parse_args()
    overrides = {
        k: v
        for k, v in vars(args).items()
        if k != "config" and v != p.get_default(k)
    }
    cfg = load_config(args.config, overrides)
    for k, v in cfg.items():
        setattr(args, k, v)
    return args


def main() -> None:
    args = parse_args()
    fields = load_fields(vehicle=args.vehicle)[0] if args.vehicle else load_fields()[0]
    client = UDSClient(args.host, port=args.port, fields=fields)
    poll_sids = args.fields or list(POLL_SIDS)
    mqtt_client = mqtt.Client()
    mqtt_client.connect(args.mqtt_host, args.mqtt_port)
    mqtt_client.loop_start()
    logger = None
    if args.log_csv or args.log_sqlite:
        from tools.logger import Logger  # type: ignore

        logger = Logger(args.log_csv, args.log_sqlite, args.log_rotate)

    try:
        while True:
            vals = {sid: _safe_read(client, sid) for sid in poll_sids}
            state = detect_state(vals)
            payload = build_payload(vals, state)
            payload["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            if logger:
                logger.log(payload)
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
            finally:
                if logger:
                    logger.close()


if __name__ == "__main__":
    main()
