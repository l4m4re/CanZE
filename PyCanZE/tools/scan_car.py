#!/usr/bin/env python3
"""Scan all diagnostic fields for a selected car model using PyCanZE.

The script lists available vehicles based on the CSV database copied from the
original CanZE Android project. For each ECU field definition it attempts to
query the connected vehicle via a WiFi ELM327 dongle using the :class:`UDSClient`
from :mod:`pycanze`. Retrieved values are printed to stdout.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# Allow running from repository root without installation
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pycanze import UDSClient  # type: ignore

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


def scan_car(car: str, client: UDSClient) -> None:
    car_dir = DATA_DIR / car
    field_files = sorted(f for f in car_dir.iterdir() if f.name.endswith("_Fields.csv"))
    if not field_files:
        print(f"No field definitions found for {car}")
        return

    for field_file in field_files:
        ecu = field_file.stem.replace("_Fields", "")
        print(f"\nECU: {ecu}")
        with field_file.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row:
                    continue
                sid = row[0].strip() if len(row) > 0 else ""
                name = row[11].strip() if len(row) > 11 else ""
                if not sid:
                    continue
                try:
                    value = client.read_field(sid)
                except Exception:
                    value = None
                print(f" {sid:>8} {name} -> {value}")


def main() -> None:
    args = parse_args()
    car = args.car or prompt_for_car()
    client = UDSClient(args.host, port=args.port)
    try:
        client.connect()
        client.initialize()
        scan_car(car, client)
    finally:
        client.close()


if __name__ == "__main__":
    main()

