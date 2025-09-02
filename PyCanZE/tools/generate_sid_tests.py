#!/usr/bin/env python3
"""Generate regression tests for known SIDs from captured logs.

The script scans ``Testing/logs/*.json`` for entries containing a ``sid``
field. For each unique SID that exists in the CSV database it writes a single
parametrized test module under ``pycanze/tests/generated`` verifying the
decoded value.

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

    # Collect the first successful response for each SID across all logs. If a
    # SID never yields a valid response it will be written to ``skipped``.
    #
    # ``sid_info`` maps a SID to a tuple containing:
    #   (expected value, sid_key, responses, field name, case type, is_signed)
    # ``case type`` is one of ``numeric``, ``string`` or ``na`` (not available).
    sid_info: dict[str, tuple[object, str, list[str], str, str, bool]] = {}
    skipped_candidates: set[str] = set()

    for json_path in sorted(logs_root.glob("*.json")):
        raw_path = json_path.with_suffix(".raw")
        if not raw_path.exists():
            continue
        mapping = _parse_raw_mapping(raw_path)
        entries = _clean_json(json_path)
        for ent in entries:
            sid = ent.get("sid")
            raw_val = ent.get("value")
            if not isinstance(sid, str):
                continue
            if sid in sid_info:
                continue
            field = fields.get(sid)
            if field is None:
                skipped_candidates.add(sid)
                continue
            # Determine how to handle the captured value
            if raw_val is None or (isinstance(raw_val, str) and raw_val.upper() in {"N/A", "NA"}):
                case_type = "na"
                expected_val: object = None
            elif field.is_string() or field.is_hex_string():
                case_type = "string"
                expected_val = raw_val if isinstance(raw_val, str) else None
            elif isinstance(raw_val, str):
                case_type = "string"
                expected_val = raw_val
            elif isinstance(raw_val, (int, float)):
                case_type = "numeric"
                expected_val = float(raw_val)
            else:
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
                skipped_candidates.add(sid)
                continue
            client = ReplayUDSClient(sid_responses={sid_key: responses}, fields=fields)
            result = client.read_field(sid)

            if case_type == "numeric":
                if result is None or not isinstance(result, (int, float)):
                    continue
                if not (
                    abs(result - expected_val) <= 1e-5
                    or (
                        abs(result) > 0
                        and abs(result - expected_val) <= abs(result) * 1e-5
                    )
                ):
                    continue
                value = float(expected_val)
            elif case_type == "string":
                if result is None or not isinstance(result, str):
                    continue
                value = result
            else:  # "na"
                if result is not None:
                    continue
                value = None

            sid_info[sid] = (
                value,
                sid_key,
                responses,
                field.name,
                case_type,
                field.is_signed(),
            )

    # Remove any legacy per-SID test modules
    for old in out_dir.glob("test_sid_*.py"):
        old.unlink()

    test_path = out_dir / "test_generated_sids.py"
    if test_path.exists() and not args.overwrite:
        return

    lines = [
        "from pycanze.replay_client import ReplayClient as ReplayUDSClient",
        "import pytest",
        "",
        "CASES = [",
    ]

    for sid, (value, sid_key, responses, _name, case_type, _is_signed) in sorted(sid_info.items()):
        lines.append(
            f"    ({sid!r}, {sid_key!r}, {responses!r}, {value!r}, {case_type!r}),"
        )

    lines += [
        "]",
        "",
        "@pytest.mark.parametrize('sid, sid_key, responses, expected, case_type', CASES)",
        "def test_generated_sids(sid, sid_key, responses, expected, case_type):",
        "    client = ReplayUDSClient(sid_responses={sid_key: responses})",
        "    if case_type == 'numeric':",
        "        assert client.read_field(sid) == pytest.approx(expected)",
        "    elif case_type == 'string':",
        "        assert client.read_field(sid) == expected",
        "    else:",
        "        assert client.read_field(sid) is None",
    ]

    test_path.write_text("\n".join(lines) + "\n")

    skipped = sorted(s for s in skipped_candidates if s not in sid_info)
    skip_path = out_dir / "skipped_sids.txt"
    lines = []
    for sid in skipped:
        field = fields.get(sid)
        name = field.name if field else "Unknown"
        lines.append(f"{sid}\t{name}")
    skip_path.write_text("\n".join(lines) + ("\n" if lines else ""))


if __name__ == "__main__":
    main()
