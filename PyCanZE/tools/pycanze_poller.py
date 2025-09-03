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
SID_SOH = "7ec.24.623206"            # HV battery SOH (can exceed 100%)

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
    SID_SOH,
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
 
# Lightweight ECU-awake probes (identification DIDs) to bracket each poll.
# Based on logs: LBC2 0x6180 returns during charging/awake, not in sleep.
PROBE_LBC2_BEGIN = "7bb.56.6180"   # DiagnosticIdentificationCode -> 35 when awake
PROBE_LBC2_END   = "7bb.200.6180"  # ManufacturerIdentificationCode -> 136.0 when awake
  

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


def _safe_read(client: UDSClient, sid: str) -> Optional[float]:
    """Read a single field with per-call resilience; return None on benign errors."""
    try:
        return client.read_field(sid)
    except (TimeoutError, socket.timeout):
        return None
    except (OSError, ConnectionError):
        # Bubble up for offline handling
        raise
    except Exception:
        return None


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
    # No flag for probes: we always bracket each poll with LBC2 0x6180 probes to detect
    # awakeness and reject samples if a transition occurs during the poll.
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
                "soh",
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
                "probe_lbc2_awake",
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
        # For concise output/logging when sleeping/offline
        last_simple_state: Optional[str] = None  # 'offline'|'sleeping'|'awake'|'charging'
        dot_mode = False
        try:
            client.connect()
            client.initialize()
            elm_connected = True
        except Exception as e:
            ts = time.strftime('%Y-%m-%dT%H:%M:%S')
            if last_simple_state != "offline":
                if dot_mode:
                    print()
                    dot_mode = False
                print(f"{ts} State: offline -> ELM327 init failed: {e}")
                csv_writer.writerow([
                    ts, "offline", False, False, False,
                    None, None, None, None, None, None, None, None, None,
                    None, None, None, None, None, None,
                ])
                csv_file.flush()
                last_simple_state = "offline"
            else:
                print('.', end='', flush=True)
                dot_mode = True

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
                    if last_simple_state != "offline":
                        if dot_mode:
                            print()
                            dot_mode = False
                        print(f"{ts} State: offline -> {e}")
                        csv_writer.writerow([
                            ts, "offline", False, False, False,
                            None, None, None, None, None, None, None, None, None,
                            None, None, None, None, None, None,
                        ])
                        csv_file.flush()
                        last_simple_state = "offline"
                    else:
                        print('.', end='', flush=True)
                        dot_mode = True
                    time.sleep(args.interval)
                    continue

            try:
                # Bracket the poll with LBC2 0x6180 probes to detect awakeness and transitions.
                pre_probe_val = _safe_read(client, PROBE_LBC2_BEGIN)
                pre_awake = pre_probe_val is not None

                if not pre_awake:
                    # Immediately check post probe to detect a rapid wake-up; if changed, retry.
                    post_probe_val_quick = _safe_read(client, PROBE_LBC2_END)
                    post_awake_quick = post_probe_val_quick is not None
                    if post_awake_quick != pre_awake:
                        # Transition occurred during our minimal bracket; discard and retry.
                        time.sleep(0.2)
                        continue
                    # Stable sleeping: no need to query heavy SIDs this cycle.
                    vals = {}
                    awake_stable = False
                    post_awake = post_awake_quick
                else:
                    # Awake at start: read the main SIDs, then post-probe to confirm stability.
                    vals: dict[str, float | None] = {}
                    for sid in POLL_SIDS:
                        vals[sid] = _safe_read(client, sid)
                    post_probe_val = _safe_read(client, PROBE_LBC2_END)
                    post_awake = post_probe_val is not None
                    if post_awake != pre_awake:
                        # Transition occurred during the poll; discard this sample and retry.
                        print(f"Transition detected: {pre_awake} -> {post_awake}")
                        time.sleep(0.2)
                        continue
                    awake_stable = True
            except (TimeoutError, socket.timeout, OSError, ConnectionError) as e:
                # Connection dropped or unreachable: mark offline and retry.
                elm_connected = False
                ts = time.strftime('%Y-%m-%dT%H:%M:%S')
                if last_simple_state != "offline":
                    # End any dot line
                    if dot_mode:
                        print()
                        dot_mode = False
                    print(f"{ts} State: offline -> {e}")
                    # Log offline sample once on transition
                    csv_writer.writerow([
                        ts, "offline", False, False, False,
                        None, None, None, None, None, None, None, None, None,
                        None, None, None, None, None, None,
                    ])
                    csv_file.flush()
                    last_simple_state = "offline"
                else:
                    # Just a dot to show we're alive
                    print('.', end='', flush=True)
                    dot_mode = True
                # Reset latched connection on offline
                latched_connected = False
                time.sleep(args.interval)
                continue
            # Extract values (may be empty when sleeping)
            soc = vals.get(SID_SOC) if vals else None
            soc_mem = vals.get(SID_SOC_MEM) if vals else None
            soh = vals.get(SID_SOH) if vals else None
            odo = vals.get(SID_ODO) if vals else None
            plug = vals.get(SID_PLUG) if vals else None
            plug_valid = vals.get(SID_PLUG_VALID) if vals else None
            plug_det = vals.get(SID_PLUG_DETECTED) if vals else None
            earth = vals.get(SID_EARTH) if vals else None
            charger_bloc = vals.get(SID_CHARGER_BLOC) if vals else None
            chg_set = vals.get(SID_CHG_SET) if vals else None
            chg_mode_req = vals.get(SID_CHG_MODE) if vals else None
            chg_mode_status = vals.get(SID_CHG_MODE_STATUS) if vals else None
            wait_iso = vals.get(SID_WAIT_ISO) if vals else None
            jb_fault = vals.get(SID_JB_FAULT) if vals else None

            ts = time.strftime('%Y-%m-%dT%H:%M:%S')

            # Derived flags (instantaneous)
            probe_lbc2_awake: Optional[bool] = True if awake_stable else (False if vals == {} else None)
            charging = _is_charging(vals) if awake_stable else False
            # EVSE presence (powered or not) using validity-gated indicators; only trust when awake
            connected_inst = _is_connected(vals) if awake_stable else None
            awake = bool(awake_stable)

            # Update latched connection only while awake AND EVSE present; keep through sleep
            if awake and connected_inst is True:
                latched_connected = True

            # Console/CSV with simplified taxonomy; minimize chatter while sleeping
            soc_print: Optional[float] = soc if soc is not None else soc_mem
            odo_print: Optional[int] = None if odo is None else int(odo)
            soc_str = "None" if soc_print is None else f"{soc_print:.2f}%"
            odo_str = "None" if odo_print is None else f"{odo_print} km"
            simple_state = "charging" if charging else ("awake" if awake else "sleeping")
            # Decide whether to log/print fully
            if simple_state == "sleeping" and last_simple_state == "sleeping":
                # Keep quiet, just a dot
                print('.', end='', flush=True)
                dot_mode = True
            else:
                # End any dot line
                if dot_mode:
                    print()
                    dot_mode = False
                # CSV row
                csv_writer.writerow([
                    ts,
                    simple_state,
                    charging,
                    connected_inst if connected_inst is not None else None,
                    latched_connected,
                    None if soc is None else round(float(soc), 3),
                    None if soc_mem is None else round(float(soc_mem), 3),
                    None if soh is None else round(float(soh), 3),
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
                    None if probe_lbc2_awake is None else bool(probe_lbc2_awake),
                ])
                csv_file.flush()

                tail = "" if charging else f" Conn: {'yes' if latched_connected else 'no'}"
                # Append probe state for visibility when known
                if probe_lbc2_awake is not None:
                    tail += f" Probe[LBC2]: {'1' if probe_lbc2_awake else '0'}"
                print(f"{ts} State: {simple_state:<22} Odo: {odo_str:<10} SoC: {soc_str}{tail}")
                last_simple_state = simple_state
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

