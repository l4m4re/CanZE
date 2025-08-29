#!/usr/bin/env python3
"""Scan all data points for a selected car model.

The script lists available cars based on the asset directories in the
Android project. After choosing a car, each ECU's field definition is
walked and a placeholder read operation is executed.  The goal is to
verify that all data points can be parsed from the database.

Actual communication with a vehicle is not implemented; the current
implementation prints the field names as they are encountered.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "app" / "src" / "main" / "assets"


def list_cars() -> list[str]:
    """Return the list of available car directories."""
    if not ASSETS_DIR.exists():
        return []
    return sorted([d.name for d in ASSETS_DIR.iterdir() if d.is_dir()])


def parse_args() -> argparse.Namespace:
    cars = list_cars()
    parser = argparse.ArgumentParser(description="Scan ECU data points for a car")
    parser.add_argument("car", nargs="?", choices=cars, help="Car model to scan")
    return parser.parse_args()


def prompt_for_car() -> str:
    cars = list_cars()
    if not cars:
        raise SystemExit("No car definitions found under assets directory")
    print("Available cars:")
    for idx, car in enumerate(cars, start=1):
        print(f"{idx}. {car}")
    while True:
        try:
            choice = int(input("Select car [1-%d]: " % len(cars)))
            if 1 <= choice <= len(cars):
                return cars[choice - 1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


def read_from_ecu(field: list[str]):
    """Placeholder for ECU read operation.

    The actual implementation should communicate with the vehicle's ECU
    using the appropriate CAN/UDS protocol and return the value for the
    provided field definition.
    """
    # TODO: implement ECU communication
    return "N/A"


def scan_car(car: str) -> None:
    car_dir = ASSETS_DIR / car
    if not car_dir.exists():
        raise SystemExit(f"Unknown car '{car}'")

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
                value = read_from_ecu(row)
                print(f" {sid:>8} {name} -> {value}")


def main() -> None:
    args = parse_args()
    car = args.car or prompt_for_car()
    scan_car(car)


if __name__ == "__main__":
    main()
