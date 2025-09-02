#!/usr/bin/env python3
"""Poll lean EV fields, infer charging and cable connection, and log to CSV.

Connects to a WiFi ELM327 dongle, performs minimal initialization and
periodically queries a small set of diagnostic identifiers that are most
informative for charger connection detection (plus SoC and odometer for
context). Each sample is appended to a CSV file, and the terminal prints a
compact summary: timestamp, inferred state, odometer, and SoC.
"""

from __future__ import annotations

import argparse
import sys
import socket
import time
from pathlib import Path
import csv
from typing import Optional

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parents[1]))
from pycanze import UDSClient  # type: ignore

# Core context SIDs
SID_SOC = "7ec.24.622002"            # SoC (may be None asleep)
SID_SOC_MEM = "7ec.168.623415"       # SoC from memory (often available)
SID_ODO = "7ec.24.622006"            # Odometer (km)

# Charger connection SIDs (lean set)
SID_PLUG = "7ec.29.6233ea"           # Plug connection status (0/2/4/6/7)
SID_PLUG_VALID = "7ec.30.6233bd"     # Validity of plug status
SID_PLUG_DETECTED = "7ec.31.62339d"  # Charger detects plug present (0/1)
SID_EARTH = "7ec.31.623108"          # Earth plug connection (0/1)
SID_CHARGER_BLOC = "7ec.29.623101"   # Charger Bloc state
SID_CHG_SET = "7ec.24.6234ad"        # Charge current setpoint (A)
SID_CHG_MODE = "7ec.30.6234dd"       # Request for PEB Charge mode V2
SID_CHG_MODE_STATUS = "7ec.30.6234dc"# PEB charge mode status V2
SID_WAIT_ISO = "7ec.31.6234af"       # Waiting isolation confirmation before start
SID_JB_FAULT = "7ec.29.62346f"       # Synthesis of JB charger fault type

# Minimal key state to detect "ready"
SID_KEY_STATE = "7ec.31.62200e"

POLL_SIDS = [
    SID_SOC,
    SID_SOC_MEM,
    SID_ODO,
    SID_PLUG,
    SID_PLUG_VALID,
    SID_PLUG_DETECTED,
    SID_EARTH,
    SID_CHARGER_BLOC,
    SID_CHG_SET,
    SID_CHG_MODE,
    SID_CHG_MODE_STATUS,
    SID_WAIT_ISO,
    SID_JB_FAULT,
    SID_KEY_STATE,
]
  

def _is_charging(vals: dict[str, float | None]) -> bool:
    """Charging when charge mode request/status indicate active or set current > 0."""
    if vals.get(SID_CHG_MODE) == 2:
        return True
    if vals.get(SID_CHG_MODE_STATUS) == 2:
        return True
    chg = vals.get(SID_CHG_SET)
    return bool(chg is not None and chg > 0)


def _is_connected(vals: dict[str, float | None]) -> bool:
    """Cable connected (powered or not) using robust indicators.

    - plug in {2,4,6} with plug_valid OK (or unknown) is strong
    - plug_detected==1 counts only if plug_valid==1
    - earth alone is ignored to avoid false positives
    """
    plug = vals.get(SID_PLUG)
    plug_valid = vals.get(SID_PLUG_VALID)
    plug_detected = vals.get(SID_PLUG_DETECTED)

    if plug in (2, 4, 6) and (plug_valid is None or plug_valid == 1):
        return True
    if plug_detected == 1 and plug_valid == 1:
        return True
    return False


def _is_awake(vals: dict[str, float | None]) -> bool:
    """Awake when the main SoC is readable and > 0, or charging.

    SoC==0.0 has been observed as a sleep signature; this heuristic may be
    refined later if needed.
    """
    if _is_charging(vals):
        return True
    soc = vals.get(SID_SOC)
    return bool(soc is not None and soc > 0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Poll EV fields via PyCanZE, infer charging/connection, and log CSV"
    )
    parser.add_argument("--host", default="192.168.2.21", help="ELM327 host")
    parser.add_argument("--port", type=int, default=35000, help="ELM327 TCP port")
    parser.add_argument("--interval", type=float, default=5.0, help="Polling interval in seconds")
    parser.add_argument(
        "--csv-file",
        default=None,
        help=(
            "Path to CSV log. Defaults to PyCanZE/Testing/logs/pycanze_poller_YYYYMMDD-HHMMSS.csv"
        ),
    )
    args = parser.parse_args()

    # Prepare CSV logging
    start_ts = time.strftime('%Y%m%d-%H%M%S')
    if args.csv_file:
        csv_path = Path(args.csv_file)
        try:
            csv_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
    else:
        # Default to PyCanZE/Testing/logs relative to this file
        log_dir = Path(__file__).resolve().parents[1] / "Testing" / "logs"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        csv_path = log_dir / f"pycanze_poller_{start_ts}.csv"
    csv_file = open(str(csv_path), "a", newline="")
    csv_writer = csv.writer(csv_file)
    # Write header if file is empty
    try:
        if csv_file.tell() == 0:
            csv_writer.writerow([
                "timestamp",
                "state",
                "charging",
                "connected_inst",
                "connected_lat",
                "soc",
                "soc_mem",
                "odo_km",
                "plug",
                "plug_valid",
                "plug_detected",
                "earth",
                "charger_bloc",
                "chg_set_A",
                "chg_mode_req",
                "chg_mode_status",
                "wait_isolation",
                "jb_fault_type",
            ])
            csv_file.flush()
    except Exception:
        pass

    client = UDSClient(args.host, port=args.port)
    try:
        # Initial connect; if it fails, we'll fall into the reconnect loop below.
        elm_connected = False
        # Latched cable connection: persists across sleep, reset on offline
        latched_connected = False
        try:
            client.connect()
            client.initialize()
            elm_connected = True
        except Exception as e:
            ts = time.strftime('%Y-%m-%dT%H:%M:%S')
            print(f"{ts} State: offline ELM327 init failed: {e}")

        while True:
            # Reconnect ELM327 link if needed
            if not elm_connected:
                try:
                    client.close()
                except Exception:
                    pass
                try:
                    client.connect()
                    client.initialize()
                    elm_connected = True
                except Exception as e:
                    ts = time.strftime('%Y-%m-%dT%H:%M:%S')
                    print(f"{ts} State: offline (reconnect) -> {e}")
                    time.sleep(args.interval)
                    continue

            try:
                vals: dict[str, float | None] = {}
                for sid in POLL_SIDS:
                    try:
                        vals[sid] = client.read_field(sid)
                    except (TimeoutError, socket.timeout):
                        vals[sid] = None
                    except (OSError, ConnectionError):
                        raise
                    except Exception:
                        vals[sid] = None
                # No legacy state classification; we derive simple states below
            except (TimeoutError, socket.timeout, OSError, ConnectionError) as e:
                # Connection dropped or unreachable: mark offline and retry.
                elm_connected = False
                ts = time.strftime('%Y-%m-%dT%H:%M:%S')
                print(f"{ts} State: offline -> {e}")
                # Log offline sample
                csv_writer.writerow([
                    ts, "offline", False, False, False, None, None, None, None, None, None,
                    None, None, None, None, None, None,
                ])
                csv_file.flush()
                # Reset latched connection on offline
                latched_connected = False
                time.sleep(args.interval)
                continue
            # Extract values
            soc = vals.get(SID_SOC)
            soc_mem = vals.get(SID_SOC_MEM)
            odo = vals.get(SID_ODO)
            plug = vals.get(SID_PLUG)
            plug_valid = vals.get(SID_PLUG_VALID)
            plug_det = vals.get(SID_PLUG_DETECTED)
            earth = vals.get(SID_EARTH)
            charger_bloc = vals.get(SID_CHARGER_BLOC)
            chg_set = vals.get(SID_CHG_SET)
            chg_mode_req = vals.get(SID_CHG_MODE)
            chg_mode_status = vals.get(SID_CHG_MODE_STATUS)
            wait_iso = vals.get(SID_WAIT_ISO)
            jb_fault = vals.get(SID_JB_FAULT)

            ts = time.strftime('%Y-%m-%dT%H:%M:%S')

            # Derived flags (instantaneous)
            charging = _is_charging(vals)
            connected_inst = _is_connected(vals)
            awake = _is_awake(vals)

            # Update latched connection only while awake; keep through sleep
            if awake:
                latched_connected = connected_inst

            # CSV row
            csv_writer.writerow([
                ts,
                # Simplified taxonomy in CSV
                ("charging" if charging else ("awake" if awake else "sleeping")),
                charging,
                connected_inst,
                latched_connected,
                None if soc is None else round(float(soc), 3),
                None if soc_mem is None else round(float(soc_mem), 3),
                None if odo is None else int(odo),
                None if plug is None else int(plug),
                None if plug_valid is None else int(plug_valid),
                None if plug_det is None else int(plug_det),
                None if earth is None else int(earth),
                None if charger_bloc is None else int(charger_bloc),
                None if chg_set is None else round(float(chg_set), 3),
                None if chg_mode_req is None else int(chg_mode_req),
                None if chg_mode_status is None else int(chg_mode_status),
                None if wait_iso is None else int(wait_iso),
                None if jb_fault is None else int(jb_fault),
            ])
            csv_file.flush()

            # Console summary with simplified taxonomy
            soc_print: Optional[float] = soc if soc is not None else soc_mem
            odo_print: Optional[int] = None if odo is None else int(odo)
            soc_str = "None" if soc_print is None else f"{soc_print:.2f}%"
            odo_str = "None" if odo_print is None else f"{odo_print} km"
            simple_state = "charging" if charging else ("awake" if awake else "sleeping")
            tail = "" if charging else f" Conn: {'yes' if latched_connected else 'no'}"
            print(f"{ts} State: {simple_state:<22} Odo: {odo_str:<10} SoC: {soc_str}{tail}")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            client.close()
        finally:
            try:
                csv_file.flush()
                csv_file.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()

