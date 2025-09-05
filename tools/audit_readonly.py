#!/usr/bin/env python3
"""Audit SIDs for read-only UDS services.

The script scans ``pycanze/data`` CSV files and Python sources for diagnostic
service identifiers (SIDs). Any SID whose service byte is not in the allow
list is reported and the script exits with a non-zero status.

It helps enforce the repository's read-only policy.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Iterable

# UDS services that are considered benign / read-only.
ALLOWED_SERVICES = {
    "10",  # diagnostic session control
    "14",  # clear diagnostic information (legacy; see dataset)
    "19",  # read DTC information
    "21",  # read data by local identifier
    "22",  # read data by identifier
    "3e",  # tester present
}

CSV_ROOT = Path(__file__).resolve().parents[1] / "PyCanZE" / "pycanze" / "data"
PY_ROOT = Path(__file__).resolve().parents[1] / "PyCanZE"


def _iter_csv_services() -> Iterable[tuple[Path, int, str]]:
    """Yield (path, line number, request id) for disallowed CSV entries."""
    for csv_path in CSV_ROOT.rglob("*.csv"):
        name = csv_path.name
        if "Fields" not in name and "Dtcs" not in name:
            continue
        with csv_path.open(newline="") as fh:
            reader = csv.reader(fh)
            for line_no, row in enumerate(reader, 1):
                if row and row[0].lstrip().startswith("#"):
                    continue
                if len(row) < 9:
                    continue
                request = row[8].strip()
                if not request or request.upper() == "999999":
                    continue
                if not re.fullmatch(r"[0-9A-Fa-f]{2,}", request):
                    continue
                service = request[:2].lower()
                if service not in ALLOWED_SERVICES:
                    yield csv_path, line_no, request


def _iter_py_services() -> Iterable[tuple[Path, int, str]]:
    """Yield (path, line number, SID string) for disallowed Python constants."""
    sid_re = re.compile(r"([0-9a-fA-F]+\.[0-9a-fA-F]+\.[0-9a-fA-F]+)")
    for py_path in PY_ROOT.rglob("*.py"):
        text = py_path.read_text(encoding="utf-8")
        for match in sid_re.finditer(text):
            sid = match.group(1)
            parts = sid.split(".")
            tail = parts[-1]
            if len(tail) < 2 or not re.fullmatch(r"[0-9a-fA-F]+", tail):
                continue
            try:
                service_byte = int(tail[:2], 16)
            except ValueError:
                continue
            if service_byte >= 0x40:
                service_byte -= 0x40  # positive response -> request service
            service = f"{service_byte:02x}"
            if service not in ALLOWED_SERVICES:
                line_no = text.count("\n", 0, match.start()) + 1
                yield py_path, line_no, sid


def main() -> int:
    offenders: list[str] = []
    for path, line, token in _iter_csv_services():
        offenders.append(f"{path}:{line}: request {token}")
    for path, line, sid in _iter_py_services():
        offenders.append(f"{path}:{line}: SID {sid}")

    if offenders:
        print("Found potentially unsafe diagnostic services:")
        for line in offenders:
            print("  ", line)
        return 1
    print("All SIDs appear to be read-only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
