#!/usr/bin/env python3
"""Scan all diagnostic fields for a selected car model using PyCanZE.

The script lists available vehicles based on the CSV database copied from the
original CanZE Android project. For each ECU field definition it attempts to
query the connected vehicle via a WiFi ELM327 dongle using the :class:`UDSClient`
from :mod:`pycanze`. Retrieved values are printed to stdout.
"""

from __future__ import annotations

import argparse
import sys
import socket
from pathlib import Path

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pycanze import UDSClient  # type: ignore
from pycanze.parser import _read_csv  # type: ignore

# Directory containing copied asset CSV files
DATA_DIR = Path(__file__).resolve().parent.parent / "pycanze" / "data"


def list_cars() -> list[str]:
    """Return the list of available car directories."""

    return sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir()])


def parse_args() -> argparse.Namespace:
    cars = list_cars()
    parser = argparse.ArgumentParser(
        description="Scan ECU data points for a car",
    )
    parser.add_argument("car", nargs="?", choices=cars, help="Car model to scan")
    parser.add_argument("--host", default="192.168.2.21", help="ELM327 host")
    parser.add_argument("--port", type=int, default=35000, help="ELM327 TCP port")
    parser.add_argument(
        "--ecu",
        action="append",
        help="Limit scan to ECUs whose file name contains this token (can be repeated)",
    )
    parser.add_argument(
        "--only-values",
        action="store_true",
        help="Only print fields that returned a value",
    )
    return parser.parse_args()


def prompt_for_car() -> str:
    cars = list_cars()
    if not cars:
        raise SystemExit("No car definitions found under data directory")
    print("Available cars:")
    for idx, car in enumerate(cars, start=1):
        print(f"{idx}. {car}")
    while True:
        try:
            choice = int(input(f"Select car [1-{len(cars)}]: "))
            if 1 <= choice <= len(cars):
                return cars[choice - 1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


def _sid_for_row(row: list[str]) -> str | None:
    """Return the field SID matching parser logic or ``None`` to skip.

    Follows the same column layout used in ``pycanze.parser.load_fields``.
    If the CSV provides an explicit SID (col 0), it is returned. Otherwise a
    fallback SID of ``f"{frame_id}.{start_bit}.{response_id}"`` is generated.
    """

    # Normalize row length like the parser
    row = (row + [""] * 13)[:13]
    sid, frame_id_s, start_bit_s, _end_bit_s, _resolution_s, _offset_s, _decimals_s, _unit, _request_id, response_id, _options_s, _name, _raw_values = row
    sid = sid.strip()
    if sid and not sid.startswith("#"):
        return sid
    if not frame_id_s or not start_bit_s or not response_id:
        return None
    return f"{frame_id_s}.{start_bit_s}.{response_id}"


def scan_car(car: str, client: UDSClient) -> None:
    car_dir = DATA_DIR / car
    field_files = sorted(f for f in car_dir.iterdir() if f.name.endswith("_Fields.csv"))
    if not field_files:
        print(f"No field definitions found for {car}")
        return

    args = parse_args()  # reuse same args for filters when invoked as module
    filters = [t.lower() for t in (args.ecu or [])]

    for field_file in field_files:
        ecu = field_file.stem.replace("_Fields", "")
        if filters and not any(tok in ecu.lower() for tok in filters):
            continue
        print(f"\nECU: {ecu}")
        ok = 0
        total = 0
        for row in _read_csv(field_file):
            # Build SID compatible with the in-memory database
            sid = _sid_for_row(row)
            if not sid:
                continue
            # Only attempt UDS read queries: 0x22 (DID) and 0x21 (local id)
            req = (row + [""] * 13)[8]
            if not req or not (req.startswith("22") or req.startswith("21")):
                continue
            name = (row + [""] * 12)[11]
            # If the exact SID is unknown, try the generated fallback form
            if sid not in client.fields:
                # Attempt swapping when CSV uses frame.response.startbit
                try:
                    parts = sid.split(".")
                    if len(parts) == 3 and all(parts):
                        alt = f"{parts[0]}.{parts[2]}.{parts[1]}"
                        if alt in client.fields:
                            sid = alt
                except Exception:
                    pass
            try:
                value = client.read_field(sid)
            except BrokenPipeError:
                # Allow graceful exit when piped to head
                return
            except Exception:
                value = None
            # Detect sleeping bus / CAN error and exit cleanly
            if getattr(client, "last_status", None) == "CAN_ERROR":
                print("Vehicle CAN is asleep (CAN_ERROR). Exiting.")
                return
            total += 1
            if value is not None:
                ok += 1
                print(f" {sid:>16} {name} -> {value}")
            elif not args.only_values:
                print(f" {sid:>16} {name} -> {value}")
        print(f"-- {ecu}: {ok}/{total} values")


def main() -> None:
    args = parse_args()
    car = args.car or prompt_for_car()
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
        scan_car(car, client)
    finally:
        client.close()


if __name__ == "__main__":
    main()

