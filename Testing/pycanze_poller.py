#!/usr/bin/env python3
"""Simple SoC and odometer poller using PyCanZE.

Connects to a WiFi ELM327 dongle, performs minimal initialization and
repeatedly queries the state of charge (DID 0x2002) and total vehicle
distance (DID 0x2006).  Results are printed to stdout.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parents[1] / "PyCanZE"))
from pycanze import UDSClient  # type: ignore

# Diagnostic field SIDs
SID_SOC = "7ec.24.622002"
SID_ODO = "7ec.24.622006"


def elm327_init(client: UDSClient) -> None:
    """Minimal ELM327 initialization for UDS polling."""

    client._send("ATZ", wait=0.3); client._read_lines(3.0)
    for cmd in ("ATE0", "ATS0", "ATSP6", "ATAT1", "ATCAF0"):
        client._send(cmd)
        client._read_lines(3.0)
    client._send("ATSH7E4"); client._read_lines(3.0)
    client._send("ATFCSH7E4"); client._read_lines(3.0)
    client._send("ATCRA 7EC"); client._read_lines(3.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll SoC and odometer via PyCanZE")
    parser.add_argument("--host", default="192.168.2.21", help="ELM327 host")
    parser.add_argument("--port", type=int, default=35000, help="ELM327 TCP port")
    parser.add_argument("--interval", type=float, default=5.0, help="Polling interval in seconds")
    args = parser.parse_args()

    client = UDSClient(args.host, port=args.port)
    try:
        client.connect()
        elm327_init(client)
        while True:
            soc = client.read_field(SID_SOC)
            odo = client.read_field(SID_ODO)
            if soc is None or odo is None:
                print(f"SoC: {soc}  Odo: {odo}")
            else:
                print(f"SoC: {soc:.2f}%  Odo: {odo:.0f} km")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()


if __name__ == "__main__":
    main()
