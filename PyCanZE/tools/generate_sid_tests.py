#!/usr/bin/env python3
"""Generate regression tests for known SIDs from captured logs.

The script scans ``Testing/logs/*.json`` for entries containing a ``sid``
field. For each unique SID that exists in the CSV database it writes a test
module under ``pycanze/tests/generated`` verifying the decoded value.

SIDs that appear in the logs but are missing from the database are written to
``skipped_sids.txt`` in the output directory.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys
from typing import Dict, List


sys.path.append(str(Path(__file__).resolve().parents[1]))
from pycanze.replay_client import ReplayClient as ReplayUDSClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_raw_mapping(path: Path) -> Dict[str, List[str]]:
    """Return mapping of request command to response lines from a raw log."""
    mapping: Dict[str, List[str]] = {}
    current: str | None = None
    responses: List[str] = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current and responses:
                    mapping[current] = responses
                cmd = "".join(line[1:].split()).upper()
                if cmd.startswith("AT"):
                    current = None
                    responses = []
                else:
                    current = cmd
                    responses = []
            elif line.startswith("<") and current:
                text = "".join(ch for ch in line[1:] if ch not in " ")
                up = text.upper()
                if any(token in up for token in [
                    "NODATA",
                    "NO DATA",
                    "ERROR",
                    "CANERROR",
                    "CAN ERROR",
                    "BUSINIT",
                    "BUS INIT",
                    "SEARCHING",
                ]):
                    current = None
                    responses = []
                else:
                    responses.append(up)
    if current and responses:
        mapping[current] = responses
    return mapping


def _clean_json(path: Path):
    text = path.read_text()
    clean = re.sub(r"[\x00-\x1F\x7F]", lambda m: "" if m.group(0) not in "\t\n\r" else m.group(0), text)
    return json.loads(clean)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "pycanze" / "tests" / "generated",
        help="directory to write test modules",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing tests if present",
    )
    args = parser.parse_args()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    logs_root = Path(__file__).resolve().parents[1] / "Testing" / "logs"
    fields = ReplayUDSClient().fields
    seen: set[str] = set()
    skipped: set[str] = set()

    for json_path in sorted(logs_root.glob("*.json")):
        raw_path = json_path.with_suffix(".raw")
        if not raw_path.exists():
            continue
        mapping = _parse_raw_mapping(raw_path)
        entries = _clean_json(json_path)
        for ent in entries:
            sid = ent.get("sid")
            value = ent.get("value")
            if not isinstance(sid, str) or not isinstance(value, (int, float)):
                continue
            if sid in seen:
                continue
            seen.add(sid)
            field = fields.get(sid)
            if field is None:
                skipped.add(sid)
                continue
            rid = field.request_id.upper()
            service = int(rid[:2], 16)
            id_hex = rid[2:]
            if len(id_hex) == 4:
                hi = int(id_hex[:2], 16)
                lo = int(id_hex[2:], 16)
                cmd = f"03{service:02X}{hi:02X}{lo:02X}"
                sid_key = f"{service:02X}{hi:02X}{lo:02X}"
            else:
                ident = int(id_hex, 16)
                cmd = f"02{service:02X}{ident:02X}"
                sid_key = f"{service:02X}{ident:02X}"
            responses = mapping.get(cmd)
            if not responses:
                skipped.add(sid)
                continue
            client = ReplayUDSClient(sid_responses={sid_key: responses})
            result = client.read_field(sid)
            if result is None or not (
                abs(result - float(value)) <= 1e-5
                or (abs(result) > 0 and abs(result - float(value)) <= abs(result) * 1e-5)
            ):
                continue
            test_name = f"test_sid_{sid.replace('.', '_')}.py"
            test_path = out_dir / test_name
            if test_path.exists() and not args.overwrite:
                continue
            content = (
                "from pycanze.replay_client import ReplayClient as ReplayUDSClient\n"
                "import pytest\n\n"
                f"def test_{sid.replace('.', '_')}():\n"
                f"    client = ReplayUDSClient(sid_responses={{\"{sid_key}\": {responses!r}}})\n"
                f"    assert client.read_field(\"{sid}\") == pytest.approx({float(value)})\n"
            )
            test_path.write_text(content)

    if skipped:
        skip_path = out_dir / "skipped_sids.txt"
        skip_path.write_text("\n".join(sorted(skipped)) + "\n")


if __name__ == "__main__":
    main()
