#!/usr/bin/env python3
"""Battery health snapshot using LBC/EVC dedicated reads.

Outputs a compact set of metrics helpful for monitoring battery health:
- SOH (EVC $3206)
- SOC (EVC $2002)
- HV voltage (EVC $2004 or $3008)
- Min/Max cell voltage (LBC 21_03)
- OCV (LBC 21_03)
- Battery average/min/max temperatures (LBC 21_04)
- Balancing flags summary (LBC 21_07)

Requires the same WiFi ELM327 setup used by other tools.

The tool mirrors the app's AT sequence and exposes tunables for timing and
filter behaviour. For LBC clones that occasionally lose consecutive frames a
``--wide-cf-fallback`` option widens filters and enables ``ATH1`` temporarily.
"""
from __future__ import annotations

import argparse
import socket
import time
import sys
from pathlib import Path

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pycanze import UDSClient  # type: ignore
from pycanze.parser import load_fields  # type: ignore


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Battery health snapshot (LBC/EVC)")
    p.add_argument("car", nargs="?", default="ZOE")
    p.add_argument("--host", default="192.168.2.21")
    p.add_argument("--port", type=int, default=35000)
    p.add_argument("--debug", action="store_true", help="Verbose UDS/ELM logging")
    p.add_argument(
        "--try-session",
        action="store_true",
        help="Attempt a diagnostic session on LBC before 0x21 reads",
    )
    p.add_argument("--caf", type=int, choices=[0, 1], help="ATCAF mode (0/1)")
    p.add_argument(
        "--stmin-ms", type=int, help="Flow Control STmin in ms (ATFCSD 3000xx)"
    )
    p.add_argument(
        "--header-settle-ms",
        type=float,
        help="Delay after ATSH/ATCRA before first request",
    )
    p.add_argument(
        "--first-21-delay-ms",
        type=float,
        help="Delay before first 0x21 after header switch",
    )
    p.add_argument(
        "--use-mask-filter", action="store_true", help="Use ATCF/ATCM instead of ATCRA"
    )
    p.add_argument(
        "--wide-cf-fallback",
        action="store_true",
        help="Temporarily widen filters and enable ATH1 if CFs are missing",
    )
    p.add_argument(
        "--atst-ms", type=float, help="ELM ATST timeout in ms (rounded to 4ms units)"
    )
    p.add_argument(
        "--atst-hex", type=str, help="ELM ATST raw hex byte (overrides --atst-ms)"
    )
    p.add_argument(
        "--isotp-collect-s", type=float, help="ISO-TP total collect window in seconds"
    )
    p.add_argument(
        "--cf-read-timeout-s",
        type=float,
        help="Per-read timeout when collecting Consecutive Frames",
    )
    p.add_argument(
        "--lbc-first-21-delay-ms",
        type=float,
        help="Override first-0x21 delay for LBC only",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    client = UDSClient(args.host, port=args.port)
    try:
        # Connect and init
        try:
            client.connect()
        except (OSError, ConnectionError, socket.timeout) as e:
            print(f"ELM327 not reachable at {args.host}:{args.port} -> {e}")
            sys.exit(2)
        try:
            # Apply tunables via environment so uds.py can read them lazily
            import os

            if args.caf is not None:
                os.environ["PYCANZE_CAF"] = str(args.caf)
            if args.stmin_ms is not None:
                os.environ["PYCANZE_FC_STMIN_MS"] = str(args.stmin_ms)
            if args.header_settle_ms is not None:
                os.environ["PYCANZE_HEADER_SETTLE_MS"] = str(args.header_settle_ms)
            if args.first_21_delay_ms is not None:
                os.environ["PYCANZE_DELAY_BEFORE_21_MS"] = str(args.first_21_delay_ms)
            if args.use_mask_filter:
                os.environ["PYCANZE_USE_MASK_FILTER"] = "1"
            if args.wide_cf_fallback:
                os.environ["PYCANZE_WIDE_CF_FALLBACK"] = "1"
            if args.atst_hex:
                os.environ["PYCANZE_ATST"] = str(args.atst_hex)
            elif args.atst_ms is not None:
                os.environ["PYCANZE_ATST_MS"] = str(args.atst_ms)
            if args.isotp_collect_s is not None:
                os.environ["PYCANZE_ISOTP_COLLECT_S"] = str(args.isotp_collect_s)
            if args.cf_read_timeout_s is not None:
                os.environ["PYCANZE_CF_READ_TIMEOUT_S"] = str(args.cf_read_timeout_s)
            if args.lbc_first_21_delay_ms is not None:
                os.environ["PYCANZE_FIRST_21_DELAY_LBC_MS"] = str(
                    args.lbc_first_21_delay_ms
                )
            client.initialize()
        except Exception as e:
            print(f"ELM327 initialization failed -> {e}")
            sys.exit(3)

        fields_by_sid, fields_by_name = load_fields()

        # Enable debug printing both in tool and client
        if args.debug:
            os.environ["PYCANZE_DEBUG"] = "1"
            setattr(client, "debug", True)

        # Best-effort session start on LBC (0x79B/0x7BB) when requested
        if args.try_session:
            try:
                client.ensure_session(0x7BB, force=True)
            except Exception as e:
                if args.debug:
                    print(f"[battery_health] LBC session attempt failed: {e}")

        def _normalize(s: str) -> str:
            return "".join(ch.lower() for ch in s if ch.isalnum() or ch in "_#")

        def _resolve_field(name: str):
            # Try exact
            f = fields_by_name.get(name)
            if f:
                return f
            # Try suffix match ignoring leading "($XXXX) " in CSV names
            needle = name.strip().lower()
            needle_norm = _normalize(name)
            for fld in list(fields_by_sid.values()):
                nm = (getattr(fld, "name", None) or "").strip()
                if not nm:
                    continue
                nm_low = nm.lower()
                # If name in CSV starts with a DID prefix, drop it for compare
                if nm_low.startswith("($") and ") " in nm_low:
                    nm_low_cmp = nm_low.split(") ", 1)[1]
                else:
                    nm_low_cmp = nm_low
                if (
                    nm_low_cmp == needle
                    or nm_low.endswith(needle)
                    or needle in nm_low_cmp
                ):
                    return fld
                # Normalize out spaces and punctuation to catch variants
                if _normalize(nm_low_cmp) == needle_norm:
                    return fld
            return None

        def val(name: str) -> float | None:
            f = _resolve_field(name)
            if not f:
                if args.debug:
                    print(f"[battery_health] field not found by name: {name}")
                return None
            try:
                if args.debug:
                    print(f"[battery_health] reading: {name} ({f.sid})")
                # Light retry for flaky 0x21 pages
                v = client.read_field(f.sid)
                if v is None and f.request_id.upper().startswith("21"):
                    time.sleep(0.15)
                    v = client.read_field(f.sid)
                if args.debug:
                    print(
                        f"[battery_health] -> {v} (status={getattr(client, 'last_status', None)})"
                    )
                return v
            except Exception:
                return None

        # EVC basics
        soc = val("State Of Charge (SOC) HV battery")
        soh = val("State Of Health (SOH) HV battery")
        hv_v = (
            val("consolidated HV voltage")
            or val("($2004) consolidated HV voltage")
            or val("HV PEB voltage measure")
            or val("($3008) HV PEB voltage measure")
        )

        # LBC 21_03 block
        ocv = val("21_03#03 OCV (Open Circuit Voltage)") or val(
            "21_03#03OCV(OpenCircuitVoltage)"
        )
        v_max = (
            val("21_03_#13_Maximum_Cell_voltage")
            or val("21_03#13 Maximum Cell voltage")
            # Fallback to 0x22 DIDs used by some DB variants
            or val("($1417) 1417_Maximum Cell Voltage")
            or val("1417_Maximum Cell Voltage")
        )
        v_min = (
            val("21_03_#15_Minimum_Cell_voltage")
            or val("21_03#15 Minimum Cell voltage")
            or val("($1419) 1419_Minimum Cell Voltage")
            or val("1419_Minimum Cell Voltage")
        )

        # LBC 21_04 temps
        t_avg = val("21_04_#76_Average_Battery_Temperature") or val(
            "21_04#76 Average Battery Temperature"
        )
        t_min = val("21_04_#75_Minimum_Battery_Temperature") or val(
            "21_04#75 Minimum Battery Temperature"
        )
        t_max = val("21_04_#77 Maximum Battery Temperature") or val(
            "21_04#77 Maximum Battery Temperature"
        )

        # LBC 21_07 balancing: summarize first few banks
        bal1 = val("21_07_#03_Balancing Switch 1 Status") or val(
            "21_07#03 Balancing Switch 1 Status"
        )
        bal2 = val("21_07_#04_Balancing Switch 2 Status") or val(
            "21_07#04 Balancing Switch 2 Status"
        )
        bal3 = val("21_07_#05_Balancing Switch 3 Status") or val(
            "21_07#05 Balancing Switch 3 Status"
        )

        # Print summary
        print("Battery Health Snapshot")
        print("------------------------")
        print(f"SOC: {soc if soc is not None else 'NA'} %")
        print(f"SOH: {soh if soh is not None else 'NA'} %")
        print(f"HV voltage: {hv_v if hv_v is not None else 'NA'} V")
        print(f"OCV: {ocv if ocv is not None else 'NA'} V")
        print(
            f"Cell V min/max: {v_min if v_min is not None else 'NA'} / {v_max if v_max is not None else 'NA'} V"
        )
        print(
            f"Temps min/avg/max: {t_min if t_min is not None else 'NA'} / {t_avg if t_avg is not None else 'NA'} / {t_max if t_max is not None else 'NA'} °C"
        )
        print(f"Balancing (banks 1-3): {bal1},{bal2},{bal3}")
        if getattr(client, "last_status", None):
            print(f"Status: {getattr(client, 'last_status', None)}")
        if getattr(client, "last_status", None) == "CAN_ERROR":
            print("Vehicle CAN is asleep (CAN_ERROR). Exiting.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
