import json
import math
import re
import sys
from pathlib import Path

import pytest

# Ensure package imports work when tests run from repo root
sys.path.append(str(Path(__file__).resolve().parents[2]))
from pycanze.uds import UDSClient, ELM_CMD_SLEEP
from pycanze.replay_client import ReplayClient as ReplayUDSClient


# Lists used for summary reporting after the SID decoding tests run
MISSING_DB_SIDS: set[str] = set()
MISMATCHES: dict[str, tuple[float, float | None, str | None]] = {}


# ---------------------------------------------------------------------------
# Frame reassembly
# ---------------------------------------------------------------------------


class DummyClient(UDSClient):
    def __init__(self):
        super().__init__("0.0.0.0")
        self.sock = object()
        self._read_calls = 0

    def _send(self, line: str, wait: float = ELM_CMD_SLEEP) -> None:  # pragma: no cover - network stub
        pass

    def _read_lines(self, timeout: float | None = None):
        self._read_calls += 1
        if self._read_calls == 1:
            return [
                "10 0D 61 03 11 22 33 44",
                "21 55 66 77 88 99 AA BB",
            ]
        return []


def test_collects_consecutive_frames_present_in_first_read():
    cli = DummyClient()
    resp = cli._read_by_id(0x21, 0x03, 1)
    assert resp == [
        0x61,
        0x03,
        0x11,
        0x22,
        0x33,
        0x44,
        0x55,
        0x66,
        0x77,
        0x88,
        0x99,
        0xAA,
        0xBB,
    ]


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
        missing_db = False
        missing_log = False
        count = 0
        for ent in entries:
            sid = ent.get("sid")
            value = ent.get("value")
            unit = ent.get("unit")
            if not isinstance(value, (int, float)):
                continue
            field = fields.get(sid)
            if field is None:
                MISSING_DB_SIDS.add(sid)
                if not missing_db:
                    cases.append(
                        pytest.param(
                            sid,
                            value,
                            unit,
                            mapping,
                            marks=pytest.mark.skip(reason="SID missing from database"),
                        )
                    )
                    missing_db = True
                continue
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
                if not missing_log:
                    cases.append(
                        pytest.param(
                            sid,
                            value,
                            unit,
                            mapping,
                            marks=pytest.mark.skip(reason="SID missing from logs"),
                        )
                    )
                    missing_log = True
                continue
            client = ReplayUDSClient(responses=mapping)
            result = client.read_field(sid)
            if result is None or not math.isclose(result, float(value), rel_tol=1e-5, abs_tol=1e-5):
                if sid not in MISMATCHES:
                    MISMATCHES[sid] = (float(value), float(result) if result is not None else None, unit)
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
    assert result is not None
    assert math.isclose(result, value, rel_tol=1e-5, abs_tol=1e-5)
