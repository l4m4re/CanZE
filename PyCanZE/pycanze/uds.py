"""UDS client for WiFi ELM327 dongles.

This module exposes :class:`UDSClient` which can communicate with a WiFi
ELM327 interface.  When the optional ``python-OBD-wifi`` package is available,
it is used to manage the underlying connection; otherwise a small set of socket
helpers derived from ``Testing/zoe_arrival_poller.py`` is employed.  The client
can query diagnostic data identifiers (DIDs) defined in the CanZE database and
decode the returned payload using the field's bit positions, resolution and
offset.
"""

from __future__ import annotations

import socket
import time
from typing import Dict, Optional, Sequence

try:  # optional dependency for proper ELM327 management
    from obd_wifi.elm327 import ELM327  # type: ignore
except Exception:  # pragma: no cover - dependency missing
    ELM327 = None

from .models import Field
from .parser import load_fields

# Default timings copied from ``Testing/zoe_arrival_poller.py``
ELM_CMD_SLEEP = 0.12
ELM_TIMEOUT_S = 12.0


class UDSClient:
    """Simple UDS client for querying diagnostic fields.

    Parameters mirror those used in the poller script.  By default the CanZE
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
        self.sock: Optional[socket.socket] = None
        self.elm = None
        self.use_obdwifi = use_obdwifi and ELM327 is not None
        self.fields = fields if fields is not None else load_fields()[0]

    # ------------------------------------------------------------------
    # Socket helpers (straight from ``zoe_arrival_poller.py``)
    def _send(self, line: str, wait: float = ELM_CMD_SLEEP) -> None:
        assert self.sock is not None
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
        for cmd in ("ATE0", "ATS0", "ATSP6", "ATAT1", "ATCAF0"):
            self._send(cmd)
            self._read_lines(3.0)
        self._send("ATSH7E4")
        self._read_lines(3.0)
        self._send("ATFCSH7E4")
        self._read_lines(3.0)
        self._send("ATCRA 7EC")
        self._read_lines(3.0)

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
        self._send(cmd)
        lines = self._read_lines()
        b = self._only_hex_bytes(lines)
        for i in range(0, max(0, len(b) - 2)):
            # Handle negative response (0x7F ...)
            if b[i] == 0x7F and (i + 2) < len(b):
                return None
            # Positive response marker
            if b[i] == 0x62 and b[i + 1] == did_hi and b[i + 2] == did_lo:
                return b[i:]
        return None

    @staticmethod
    def _extract_bits(data: bytes, start_bit: int, end_bit: int) -> int:
        """Return integer value contained between *start_bit* and *end_bit*.

        Bit 0 refers to the MSB of ``data[0]``.  The function assumes big-endian
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
        did = int(field.request_id[2:], 16)
        resp = self._read_did(did)
        if not resp:
            return None
        raw_value = self._extract_bits(bytes(resp), field.start_bit, field.end_bit)
        return field.offset + field.resolution * raw_value

