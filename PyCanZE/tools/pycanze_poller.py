#!/usr/bin/env python3
"""Poll selected EV fields, infer vehicle state and print metrics.

Connects to a WiFi ELM327 dongle, performs minimal initialization and repeatedly
queries diagnostic identifiers useful for charge planning (SoC/SOH/odometer,
HV voltage/current, plug status). The inferred vehicle state is printed along
with the raw values from the EVC and alternative SIDs where available.
"""

from __future__ import annotations

import argparse
import sys
import socket
import time
from pathlib import Path

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parents[1]))
from pycanze import UDSClient  # type: ignore

# Diagnostic field SIDs
SID_SOC = "7ec.24.622002"
SID_SOC_MEM = "7ec.168.623415"
SID_SOH = "7ec.24.623206"
SID_SOH_ALT = "7bb.40.6160"
SID_ODO = "7ec.24.622006"
SID_ODO_ALT = "7bc.28.624b9b"
SID_HV_V = "7ec.24.622004"
SID_HV_V_LBC = "7ec.24.623203"
SID_HV_I = "7ec.24.623204"
SID_HV_I_ALT = "7ec.24.623110"
SID_DCDC = "7ec.24.623028"
SID_PLUG = "7ec.29.6233ea"
SID_HEATPUMP_REQ = "7ec.25.623328"
SID_HVAC_RELAY = "7ec.31.6233cd"
SID_CHG_SET = "7ec.24.6234ad"
SID_CHG_MODE = "7ec.30.6234dd"
SID_KEY_STATE = "7ec.31.62200e"

POLL_SIDS = [
    SID_SOC,
    SID_SOC_MEM,
    SID_SOH,
    SID_SOH_ALT,
    SID_ODO,
    SID_ODO_ALT,
    SID_HV_V,
    SID_HV_V_LBC,
    SID_HV_I,
    SID_HV_I_ALT,
    SID_DCDC,
    SID_PLUG,
    SID_HEATPUMP_REQ,
    SID_HVAC_RELAY,
    SID_CHG_SET,
    SID_CHG_MODE,
    SID_KEY_STATE,
]


def _determine_state(vals: dict[str, float | None]) -> str:
    soc = vals.get(SID_SOC)
    soc_mem = vals.get(SID_SOC_MEM)
    if soc is None and soc_mem is None:
        return "offline"
    if vals.get(SID_KEY_STATE) == 1:
        return "ready"
    if vals.get(SID_CHG_MODE) == 2 or (
        (chg := vals.get(SID_CHG_SET)) is not None and chg > 0
    ):
        return "charging"
    if vals.get(SID_HVAC_RELAY) == 1 or (
        (hp := vals.get(SID_HEATPUMP_REQ)) is not None and hp < 1
    ):
        return "charger-connected-sleep"
    return "parked-sleep"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Poll EV fields via PyCanZE and infer vehicle state"
    )
    parser.add_argument("--host", default="192.168.2.21", help="ELM327 host")
    parser.add_argument("--port", type=int, default=35000, help="ELM327 TCP port")
    parser.add_argument("--interval", type=float, default=5.0, help="Polling interval in seconds")
    args = parser.parse_args()

    client = UDSClient(args.host, port=args.port)
    try:
        try:
            client.connect()
        except (OSError, ConnectionError, socket.timeout) as e:
            print(f"ELM327 not reachable at {args.host}:{args.port} -> {e}")
            sys.exit(2)
        try:
            client.initialize()
        except Exception as e:
            print(f"ELM327 initialization failed -> {e}")
            sys.exit(3)
        while True:
            vals = {sid: client.read_field(sid) for sid in POLL_SIDS}
            state = _determine_state(vals)

            soc = vals[SID_SOC]
            soc_mem = vals[SID_SOC_MEM]
            soh = vals[SID_SOH]
            soh_alt = vals[SID_SOH_ALT]
            odo = vals[SID_ODO]
            odo_alt = vals[SID_ODO_ALT]
            hv_v = vals[SID_HV_V]
            hv_v_lbc = vals[SID_HV_V_LBC]
            hv_i = vals[SID_HV_I]
            hv_i_alt = vals[SID_HV_I_ALT]
            dcdc = vals[SID_DCDC]
            plug = vals[SID_PLUG]
            chg_set = vals[SID_CHG_SET]
            chg_mode = vals[SID_CHG_MODE]
            hp_req = vals[SID_HEATPUMP_REQ]
            hvac = vals[SID_HVAC_RELAY]

            def _fmt(v: float | None, unit: str = "", prec: int = 2) -> str:
                return "None" if v is None else f"{v:.{prec}f}{unit}"

            odo_alt_km = None if odo_alt is None else odo_alt / 1000.0

            line = (
                f"State: {state} "
                f"SoC: {_fmt(soc, '%')} (mem {_fmt(soc_mem, '%')}) "
                f"SOH: {_fmt(soh, '%')} (alt {_fmt(soh_alt, '%')}) "
                f"Odo: {_fmt(odo, ' km', 0)} (alt {_fmt(odo_alt_km, ' km', 0)}) "
                f"HV: {_fmt(hv_v, ' V', 1)} (LBC {_fmt(hv_v_lbc, ' V', 1)}) "
                f"I: {_fmt(hv_i, ' A', 1)} (alt {_fmt(hv_i_alt, ' A', 1)}) "
                f"DCDC: {_fmt(dcdc, '%', 1)} Plug: {_fmt(plug, '', 0)} "
                f"SetI: {_fmt(chg_set, ' A', 1)} Mode: {_fmt(chg_mode, '', 0)} "
                f"HPReq: {_fmt(hp_req, '%', 1)} HVAC: {_fmt(hvac, '', 0)}"
            )
            print(line)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()


if __name__ == "__main__":
    main()

