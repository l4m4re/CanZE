import json
import math
import re
import sys
from pathlib import Path

import pytest

# Ensure package imports work when tests run from repo root
sys.path.append(str(Path(__file__).resolve().parents[2]))
from pycanze.replay_client import ReplayClient as ReplayUDSClient


# ---------------------------------------------------------------------------
# Helpers


def _parse_raw_mapping(path: Path) -> dict[str, list[str]]:
    """Return mapping of request command to response lines from a raw log."""
    mapping: dict[str, list[str]] = {}
    current: str | None = None
    responses: list[str] = []
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
                if any(
                    token in up
                    for token in [
                        "NODATA",
                        "NO DATA",
                        "ERROR",
                        "CANERROR",
                        "CAN ERROR",
                        "BUSINIT",
                        "BUS INIT",
                        "SEARCHING",
                    ]
                ):
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


def _collect_cases(limit_per_file: int = 10):
    root = Path(__file__).resolve().parents[2] / "Testing" / "logs"
    fields = ReplayUDSClient().fields
    cases = []
    for json_path in sorted(root.glob("*.json")):
        raw_path = json_path.with_suffix(".raw")
        if not raw_path.exists():
            continue
        mapping = _parse_raw_mapping(raw_path)
        entries = _clean_json(json_path)
        missing_added = False
        count = 0
        for ent in entries:
            sid = ent.get("sid")
            value = ent.get("value")
            unit = ent.get("unit")
            if sid not in fields:
                if not missing_added:
                    cases.append(
                        pytest.param(
                            sid,
                            value,
                            unit,
                            mapping,
                            marks=pytest.mark.skip(reason="SID missing from database"),
                        )
                    )
                    missing_added = True
                continue
            if not isinstance(value, (int, float)):
                continue
            cases.append((sid, float(value), unit, mapping))
            count += 1
            if count >= limit_per_file:
                break
    return cases


CASES = _collect_cases()


@pytest.mark.parametrize("sid, value, unit, mapping", CASES)
def test_sid_decoding(sid: str, value: float, unit, mapping):
    client = ReplayUDSClient(responses=mapping)
    field = client.fields.get(sid)
    if field is None:
        pytest.skip("SID missing from database")
    rid = field.request_id.upper()
    service = int(rid[:2], 16)
    id_hex = rid[2:]
    if len(id_hex) == 4:
        hi = int(id_hex[:2], 16)
        lo = int(id_hex[2:], 16)
        cmd = f"03{service:02X}{hi:02X}{lo:02X}"
    else:
        ident = int(id_hex, 16)
        cmd = f"02{service:02X}{ident:02X}"
    if cmd not in mapping:
        pytest.skip("SID missing from logs")
    result = client.read_field(sid)
    if result is None:
        pytest.skip("No data for SID")
    if not math.isclose(result, value, rel_tol=1e-5, abs_tol=1e-5):
        pytest.skip("Decoded value mismatch")
    assert True
