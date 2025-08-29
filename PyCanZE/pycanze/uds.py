"""UDS client for WiFi ELM327 dongles.

This module exposes :class:`UDSClient` which can communicate with a WiFi
ELM327 interface. When the optional ``python-OBD-wifi`` package is available,
it is used to manage the underlying connection; otherwise a small set of
socket helpers derived from ``Testing/zoe_arrival_poller.py`` is employed.
The client can query diagnostic data identifiers (DIDs) defined in the CanZE
database and decode the returned payload using the field's bit positions,
resolution and offset.
"""

from __future__ import annotations

import socket
import os
import time
from typing import Dict, Optional, Sequence

try:  # optional dependency for proper ELM327 management
    from obd_wifi.elm327 import ELM327  # type: ignore
except Exception:  # pragma: no cover - dependency missing
    ELM327 = None

from .models import Field
from .parser import load_fields, load_ecus

# Default timings copied from ``Testing/zoe_arrival_poller.py``
ELM_CMD_SLEEP = 0.12
ELM_TIMEOUT_S = 12.0


class UDSClient:
    """Simple UDS client for querying diagnostic fields.

    Parameters mirror those used in the poller script. By default the CanZE
    database is loaded so fields can be looked up by SID.
    """

    def __init__(
        self,
        host: str,
        port: int = 35000,
        timeout: float = ELM_TIMEOUT_S,
        fields: Optional[Dict[str, Field]] = None,
        use_obdwifi: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None  # type: Optional[socket.socket]
        self.elm = None
        self.use_obdwifi = use_obdwifi and ELM327 is not None
        self.fields = fields if fields is not None else load_fields()[0]
        self.debug = bool(os.environ.get("PYCANZE_DEBUG"))
        # Map CAN IDs (both request and response) to (request_id, response_id)
        try:
            _ecus = load_ecus()
        except Exception:
            _ecus = {}
        self._ecu_by_can = {}
        self._net_by_req = {}  # req_id -> list of networks
        self._session_required_by_req = {}  # req_id -> bool
        self._session_started = set()  # req_ids with active session
        for ecu in _ecus.values():
            try:
                # _Ecus.csv has columns 'From ID' (ECU->tester) and 'To ID' (tester->ECU).
                # Our parser currently stores them as request_id=row[3] and response_id=row[4],
                # which means request_id actually holds the ECU response CAN id.
                # Fix the mapping here by swapping to ensure (req -> ECU, resp <- ECU).
                req = ecu.response_id & 0x7FF
                resp = ecu.request_id & 0x7FF
                self._ecu_by_can[req] = (req, resp)
                self._ecu_by_can[resp] = (req, resp)
                self._net_by_req[req] = ecu.networks
                self._session_required_by_req[req] = bool(getattr(ecu, "session_required", 0))
            except Exception:
                continue
        # Last ELM/CAN status hint (e.g. 'CAN_ERROR', 'NO_DATA')
        self.last_status = None
        # Track currently selected CAN request id (11-bit)
        self._current_req_id = None

    # ------------------------------------------------------------------
    def _ensure_session(self, req_id: int) -> None:
        """Start a diagnostic session for the ECU if required (best-effort).

        Uses UDS service 0x10 0xC0 (extended session) and expects a 0x50 0xC0 positive response.
        Non-fatal on failure.
        """
        try:
            if not self._session_required_by_req.get(req_id):
                return
            if req_id in self._session_started:
                return
            # Send 0210C0
            self._send("0210C0")
            lines = self._read_lines()
            up = [ln.upper() for ln in lines]
            if any("50C0" in ln.replace(" ", "") for ln in up):
                self._session_started.add(req_id)
        except Exception:
            # Ignore, will continue without session
            return

    # ------------------------------------------------------------------
    # Socket helpers (straight from ``zoe_arrival_poller.py``)
    def _send(self, line: str, wait: float = ELM_CMD_SLEEP) -> None:
        assert self.sock is not None
        if self.debug:
            print(f"[PYCANZE DEBUG] SEND: {line}")
        self.sock.sendall((line + "\r").encode("ascii", errors="ignore"))
        time.sleep(wait)

    def _read_lines(self, timeout: float = ELM_TIMEOUT_S) -> Sequence[str]:
        assert self.sock is not None
        self.sock.settimeout(timeout)
        buf = b""
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b">" in buf:
                break
        text = buf.decode(errors="ignore").replace("\r", "\n")
        lines = [ln.strip() for ln in text.split("\n") if ln.strip() and ln.strip() != ">"]
        if self.debug:
            print(f"[PYCANZE DEBUG] RECV: {lines}")
        return lines

    @staticmethod
    def _only_hex_bytes(lines: Sequence[str]) -> Sequence[int]:
        out = []
        for ln in lines:
            up = ln.upper()
            if any(k in up for k in ["NO DATA", "ERROR", "SEARCHING", "BUS INIT", "CAN ERROR"]):
                continue
            only_hex = "".join(ch for ch in ln if ch.upper() in "0123456789ABCDEF")
            out.extend(int(only_hex[i : i + 2], 16) for i in range(0, len(only_hex), 2))
        return out

    # ------------------------------------------------------------------
    def connect(self) -> None:
        """Open the connection to the ELM327 dongle."""

        if self.sock is not None:
            return
        if self.use_obdwifi and ELM327 is not None:
            self.elm = ELM327(self.host, port=self.port, timeout=self.timeout)  # type: ignore[call-arg]
            self.elm.connect()  # type: ignore[attr-defined]
            self.sock = getattr(self.elm, "sock", None)  # type: ignore[attr-defined]
        if self.sock is None:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)

    def initialize(self) -> None:
        """Send a standard AT init sequence to the dongle."""

        if self.sock is None:
            raise RuntimeError("connect() must be called before initialize()")
        self._send("ATZ", wait=0.3)
        self._read_lines(3.0)
        for cmd in ("ATE0", "ATH0", "ATS0", "ATSP6", "ATAT1", "ATCAF0", "ATAL"):
            self._send(cmd)
            self._read_lines(3.0)
        self.last_status = None
        # Default header (ZE/EVC): request 0x7E4, response 0x7EC
        self._send("ATSH7E4")
        self._read_lines(3.0)
        self._send("ATFCSH7E4")
        self._read_lines(3.0)
        self._send("ATCRA 7EC")
        self._read_lines(3.0)
        self._current_req_id = 0x7E4

    def close(self) -> None:
        """Close the TCP connection."""

        if self.sock is not None:
            self.sock.close()
            self.sock = None

    # ------------------------------------------------------------------
    def _read_did(self, did: int) -> Optional[Sequence[int]]:
        """Send a ReadDataByIdentifier request and return raw response bytes.

        ``did`` should be the 16-bit diagnostic identifier.
        The returned value includes the positive response header ``62 DID`` if
        present, or ``None`` for negative responses or parse errors.
        """

        did_hi = (did >> 8) & 0xFF
        did_lo = did & 0xFF
        cmd = f"0322{did_hi:02X}{did_lo:02X}"
        if self.debug:
            print(f"[PYCANZE DEBUG] UDS RDBI: {cmd}")
        self._send(cmd)
        lines = self._read_lines()
        # Detect common ELM/CAN error statuses early
        up = [ln.upper() for ln in lines]
        if any(("CAN" in ln and "ERROR" in ln) or "CAN ERROR" in ln for ln in up):
            self.last_status = "CAN_ERROR"
        elif any("NO DATA" in ln for ln in up):
            self.last_status = "NO_DATA"
        elif any("ERROR" in ln for ln in up):
            self.last_status = "ELM_ERROR"
        b = self._only_hex_bytes(lines)
        if self.debug:
            print(f"[PYCANZE DEBUG] PARSED HEX: {b}")
        for i in range(0, max(0, len(b) - 2)):
            # Handle negative response (0x7F ...)
            if b[i] == 0x7F and (i + 2) < len(b):
                return None
            # Positive response marker
            if b[i] == 0x62 and b[i + 1] == did_hi and b[i + 2] == did_lo:
                self.last_status = None
                return b[i:]
        return None

    # ------------------------------------------------------------------
    def _select_frame(self, req_id: int, resp_id: Optional[int] = None) -> None:
        """Ensure ELM headers/filters are set for the given 11-bit CAN request id.

        Sets request header (ATSH/ATFCSH) to ``req_id`` and response filter
        (ATCRA) to ``resp_id`` if provided, otherwise ``req_id + 8`` which
        matches standard UDS addressing.
        """

        # Only handle 11-bit IDs here. Extended (29-bit) support is out of scope for now.
        if req_id <= 0 or req_id > 0x7FF:
            return
        if self.sock is None:
            raise RuntimeError("connect() must be called before reading fields")
        if self._current_req_id == req_id:
            return
        rid = f"{req_id & 0x7FF:03X}"
        rpid = (resp_id if resp_id is not None else (req_id + 0x8)) & 0x7FF
        resp = f"{rpid:03X}"
        self._send(f"ATSH{rid}")
        self._read_lines(3.0)
        self._send(f"ATFCSH{rid}")
        self._read_lines(3.0)
        self._send(f"ATCRA {resp}")
        self._read_lines(3.0)
        self._current_req_id = req_id

    @staticmethod
    def _extract_bits(data: bytes, start_bit: int, end_bit: int) -> int:
        """Return integer value contained between *start_bit* and *end_bit*.

        Bit 0 refers to the MSB of ``data[0]``. The function assumes big-endian
        bit numbering as used by the existing CanZE database.
        """

        total_bits = len(data) * 8
        value = int.from_bytes(data, "big")
        shift = total_bits - end_bit - 1
        value >>= shift
        mask = (1 << (end_bit - start_bit + 1)) - 1
        return value & mask

    # ------------------------------------------------------------------
    def read_field(self, sid: str) -> Optional[float]:
        """Read and decode a diagnostic field by its SID.

        Returns the scaled value or ``None`` if the ECU returned a negative
        response.
        """

        field = self.fields.get(sid)
        if field is None or not field.request_id:
            raise KeyError(f"Unknown diagnostic field SID: {sid}")
        if len(field.request_id) != 6:
            raise ValueError(f"Unexpected request id format: {field.request_id}")
        # Switch to the ECU for this field if needed.
        # Select ECU headers for this field
        try:
            fid = field.frame_id & 0x7FF
            pair = self._ecu_by_can.get(fid)
            if pair is not None:
                self._select_frame(pair[0], pair[1])
                self._ensure_session(pair[0])
            else:
                # Fallback heuristic: fields often list the response id
                self._select_frame((fid - 0x8) & 0x7FF, fid)
        except Exception:
            # Fallback: keep current header; some fields may still respond
            pass
        did = int(field.request_id[2:], 16)
        resp = self._read_did(did)
        if not resp:
            return None
        raw_value = self._extract_bits(bytes(resp), field.start_bit, field.end_bit)
        return field.offset + field.resolution * raw_value

