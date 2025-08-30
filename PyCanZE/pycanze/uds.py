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
        self._last_tp = 0.0
        # Android schedules TesterPresent every 1500 ms
        self._tp_interval = 1.5  # seconds between TesterPresent keep-alives
        # Short-lived cache for repeated 0x21 page reads: (req_id, service, ident) -> response bytes
        self._last_tuple = None  # type: Optional[tuple[int, int, int]]
        self._last_resp = None  # type: Optional[Sequence[int]]
        self._last_resp_ts = 0.0
        for ecu in _ecus.values():
            try:
                # Parser stores FromID in request_id (ECU->tester) and ToID in response_id (tester->ECU).
                # Swap to get (req=ToID, resp=FromID).
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
        # Tunables (can be overridden by tools)
        self.caf = None                 # 0 or 1 for ATCAF
        self.fc_stmin_ms = None         # STmin ms for ATFCSD 3000xx
        self.header_settle_ms = 0.0     # sleep after ATSH/ATCRA
        self.delay_before_21_ms = 0.0   # sleep before first 0x21 after switch
        self._just_switched = False
        self.use_mask_filter = False    # use ATCF/ATCM instead of ATCRA
        self.fc_retry_enabled = True    # allow FC reassert retry
        # Additional timing controls
        self.isotp_collect_timeout_s = 2.5  # total window to collect multi-frame payload
        self.cf_read_timeout_s = 1.2        # per read timeout while collecting CFs
        # Optional per-ECU first-0x21 delay (currently used for LBC 0x7BB)
        self.first_21_delay_by_req = {}

    def _pair_for_frame(self, fid: int):
        """Return (req_id, resp_id) for a given 11-bit CAN id.

        Tries direct lookup; if missing, searches by matching response id in
        the known pairs; finally falls back to standard +8 mapping.
        """
        fid &= 0x7FF
        pair = self._ecu_by_can.get(fid)
        if pair is not None:
            return pair
        # Search by response id match
        for (_k, pr) in self._ecu_by_can.items():
            try:
                if pr[1] == fid:
                    return pr
            except Exception:
                continue
        # Fallback to standard UDS addressing heuristic (req = resp - 0x8)
        return ((fid - 0x8) & 0x7FF, fid)

    # ------------------------------------------------------------------
    def _ensure_session(self, req_id: int, force: bool = False) -> None:
        """Start a diagnostic session for the ECU if required (best-effort).

        Uses UDS service 0x10 0xC0 (extended session) and expects a 0x50 0xC0 positive response.
        Non-fatal on failure.
        """
        try:
            if not force and not self._session_required_by_req.get(req_id):
                return
            if req_id in self._session_started:
                return
            # Try common sessions: Extended (0xC0), Renault (0xF2), LGChem (0xF3), then Default (0x81)
            for mode, expect in (("0210C0", "50C0"), ("0210F2", "50F2"), ("0210F3", "50F3"), ("021081", "5081")):
                self._send(mode)
                lines = self._read_lines()
                up = [ln.upper().replace(" ", "") for ln in lines]
                if any(expect in ln for ln in up):
                    self._session_started.add(req_id)
                    break
        except Exception:
            # Ignore, will continue without session
            return

    def _tester_present(self) -> None:
        try:
            now = time.time()
            if now - self._last_tp < self._tp_interval:
                return
            # 0x3E 0x00 (TesterPresent)
            self._send("023E00")
            _ = self._read_lines(1.0)
            self._last_tp = now
        except Exception:
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
        # Read optional environment overrides for tunables if not already set
        try:
            if self.caf is None and os.environ.get("PYCANZE_CAF"):
                self.caf = int(os.environ.get("PYCANZE_CAF", "0").strip())
        except Exception:
            self.caf = None
        try:
            if self.fc_stmin_ms is None and os.environ.get("PYCANZE_FC_STMIN_MS"):
                self.fc_stmin_ms = int(os.environ.get("PYCANZE_FC_STMIN_MS", "0").strip())
        except Exception:
            self.fc_stmin_ms = None
        try:
            if not self.header_settle_ms and os.environ.get("PYCANZE_HEADER_SETTLE_MS"):
                self.header_settle_ms = float(os.environ.get("PYCANZE_HEADER_SETTLE_MS", "0").strip())
        except Exception:
            self.header_settle_ms = 0.0
        try:
            if not self.delay_before_21_ms and os.environ.get("PYCANZE_DELAY_BEFORE_21_MS"):
                self.delay_before_21_ms = float(os.environ.get("PYCANZE_DELAY_BEFORE_21_MS", "0").strip())
        except Exception:
            self.delay_before_21_ms = 0.0
        try:
            if os.environ.get("PYCANZE_USE_MASK_FILTER"):
                self.use_mask_filter = os.environ.get("PYCANZE_USE_MASK_FILTER", "").strip() not in ("0", "false", "False", "")
        except Exception:
            self.use_mask_filter = False
        # Optional ELM timeouts and ISO-TP windows
        try:
            v = os.environ.get("PYCANZE_ISOTP_COLLECT_S")
            if v:
                self.isotp_collect_timeout_s = float(v)
        except Exception:
            pass
        try:
            v = os.environ.get("PYCANZE_CF_READ_TIMEOUT_S")
            if v:
                self.cf_read_timeout_s = float(v)
        except Exception:
            pass
        try:
            v = os.environ.get("PYCANZE_TP_INTERVAL_MS")
            if v:
                self._tp_interval = float(v) / 1000.0
        except Exception:
            pass
        try:
            v = os.environ.get("PYCANZE_FC_RETRY")
            if v is not None:
                self.fc_retry_enabled = v.strip() not in ("0", "false", "False", "")
        except Exception:
            pass
        # Per-ECU first-0x21 delay: allow targeting LBC specifically
        try:
            v = os.environ.get("PYCANZE_FIRST_21_DELAY_LBC_MS")
            if v:
                # LBC request id is 0x7BB
                self.first_21_delay_by_req[0x7BB] = float(v)
        except Exception:
            pass
        # Reset and basic config mirroring Android's sequence
        self._send("ATZ", wait=0.3)
        self._read_lines(3.0)
        caf_mode = 0 if self.caf is None else int(self.caf)
        stmin = 0 if self.fc_stmin_ms is None else max(0, min(255, int(self.fc_stmin_ms)))
        init_cmds = [
            "ATE0",
            "ATS0",
            "ATH0",
            "ATL0",
            "ATAL",
            f"ATCAF{caf_mode}",
            "ATFCSH77B",
            f"ATFCSD 3000{stmin:02X}",
            "ATFCSM1",
            "ATSP6",
        ]
        for cmd in init_cmds:
            self._send(cmd)
            self._read_lines(3.0)
        # Optional: adjust ELM response timeout via ATST
        # Accept either hex byte (PYCANZE_ATST) or milliseconds (PYCANZE_ATST_MS, rounded to 4ms units)
        atst_cmd = None
        try:
            raw_hex = os.environ.get("PYCANZE_ATST")
            if raw_hex:
                hh = raw_hex.strip().upper().replace("0X", "")[-2:]
                int(hh, 16)
                atst_cmd = f"ATST {hh}"
            else:
                ms = os.environ.get("PYCANZE_ATST_MS")
                if ms:
                    iv = max(0, int(float(ms)))
                    hh = max(0, min(0xFF, int(round(iv / 4.0))))
                    atst_cmd = f"ATST {hh:02X}"
        except Exception:
            atst_cmd = None
        if atst_cmd:
            try:
                self._send(atst_cmd)
                self._read_lines(3.0)
            except Exception:
                pass
        # Flow control retry is handled later if needed; no ATCFC1/ATST issued
        self.last_status = None
        # Default header (ZE/EVC): request 0x7E4, response 0x7EC
        self._send("ATSH7E4")
        self._read_lines(3.0)
        self._send("ATFCSH7E4")
        self._read_lines(3.0)
        self._send("ATCRA 7EC")
        self._read_lines(3.0)
        self._current_req_id = 0x7E4
        self._just_switched = False

    def close(self) -> None:
        """Close the TCP connection."""

        if self.sock is not None:
            self.sock.close()
            self.sock = None

    # ------------------------------------------------------------------
    def _read_by_id(self, service: int, ident: int, ident_len: int) -> Optional[Sequence[int]]:
        """Send a generic read-by-identifier request and return raw response bytes.

        - For service 0x22 (ReadDataByIdentifier), ``ident_len`` is 2 (16-bit DID).
        - For service 0x21 (ReadDataByLocalIdentifier), ``ident_len`` is 1 (8-bit LID).
        Returns bytes starting from the positive response SID (service+0x40) or ``None``.
        """

        resp_sid = (service + 0x40) & 0xFF
        if ident_len == 2:
            hi = (ident >> 8) & 0xFF
            lo = ident & 0xFF
            cmd = f"03{service:02X}{hi:02X}{lo:02X}"
        elif ident_len == 1:
            cmd = f"02{service:02X}{ident & 0xFF:02X}"
        else:
            raise ValueError("Unsupported identifier length")
        if self.debug:
            print(f"[PYCANZE DEBUG] UDS READ: {cmd}")
        # Optional delay just before the first 0x21 after switching headers
        if service == 0x21 and self._just_switched and self.delay_before_21_ms and self.delay_before_21_ms > 0:
            if self.debug:
                print(f"[PYCANZE DEBUG] delay_before_21_ms={self.delay_before_21_ms} ms before first 0x21")
            try:
                time.sleep(self.delay_before_21_ms / 1000.0)
            except Exception:
                pass
            finally:
                self._just_switched = False
        # Opportunistic reuse for 0x21 within 1s when repeating same request
        if (
            service == 0x21
            and self._current_req_id is not None
            and self._last_tuple == (self._current_req_id, service, ident)
            and (time.time() - self._last_resp_ts) < 1.0
            and self._last_resp is not None
        ):
            return list(self._last_resp)
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
    # Manual ISO-TP reassembly fallback (without sending our own Flow Control)
    # Detect First Frame (0x10 ..) and then continue reading Consecutive Frames
    # until the total length is satisfied. We rely on ATCFC1 so the ELM327 sends
    # Flow Control frames automatically; sending a manual FC as a normal request
    # (e.g. "03300000") is incorrect and can lead to "NO DATA" responses.
        if len(b) >= 3 and (b[0] >> 4) == 0x1:
            total_len = ((b[0] & 0x0F) << 8) | (b[1] & 0xFF)
            # Payload included in First Frame (starts at index 2)
            collected: list[int] = list(b[2:])
            deadline = time.time() + float(getattr(self, "isotp_collect_timeout_s", 2.5) or 2.5)
            expected_sn = 1
            while len(collected) < total_len and time.time() < deadline:
                try:
                    more = self._read_lines(float(getattr(self, "cf_read_timeout_s", 1.2) or 1.2))
                except Exception:
                    # No more data arrived within timeout
                    break
                bb = self._only_hex_bytes(more)
                if not bb:
                    continue
                j = 0
                while j < len(bb):
                    pci = bb[j]
                    if (pci >> 4) == 0x2:  # Consecutive Frame
                        sn = pci & 0x0F
                        if sn != (expected_sn & 0x0F):
                            return None  # sequence error
                        expected_sn = (expected_sn + 1) & 0x0F
                        take = min(7, len(bb) - (j + 1), total_len - len(collected))
                        if take > 0:
                            collected.extend(bb[j + 1 : j + 1 + take])
                        j += 1 + take
                    else:
                        j += 1
            # Build response bytes starting at positive response SID
            out = collected[: total_len]
            if out and out[0] == resp_sid and len(out) >= total_len:
                self.last_status = None
                if self._current_req_id is not None and service == 0x21:
                    self._last_tuple = (self._current_req_id, service, ident)
                    self._last_resp = list(out)
                    self._last_resp_ts = time.time()
                return out
            # If we only received a First Frame and no CFs, try reasserting ATCFC1/ATFCSD once
            if (
                len(collected) < total_len
                and self.fc_retry_enabled
                and not getattr(self, "_fc_retry_active", False)
            ):
                try:
                    setattr(self, "_fc_retry_active", True)
                    # Reassert flow control settings and allow long messages
                    for cmd in ("ATCFC1", "ATFCSD 300005", "ATAL"):
                        try:
                            self._send(cmd)
                            self._read_lines(1.0)
                        except Exception:
                            pass
                    if self.debug:
                        print("[PYCANZE DEBUG] ISO-TP FF without CFs; reasserted FC, retrying once")
                    time.sleep(0.05)
                    # Retry the same request once
                    return self._read_by_id(service, ident, ident_len)
                finally:
                    setattr(self, "_fc_retry_active", False)
            # Do not fall back to segment concatenation for First Frame cases
            # to avoid returning partial payloads.
            return None
        # Some ECUs (e.g., LBC) may page multi-frame responses where lines can
        # be delivered in chunks. Try to collect segments that start with the
        # expected positive response and concatenate until we either see a
        # different SID or run out of data. The ELM with ATCFC1 should already
        # assemble frames, but some clones leak multiple lines.
        segments: list[Sequence[int]] = []
        i = 0
        while i <= max(0, len(b) - 2):
            if b[i] == 0x7F and (i + 2) < len(b):
                return None
            if b[i] == resp_sid:
                if ident_len == 2 and (i + 2) < len(b):
                    did_hi = (ident >> 8) & 0xFF
                    did_lo = ident & 0xFF
                    if b[i + 1] != did_hi or b[i + 2] != did_lo:
                        i += 1
                        continue
                # Capture this segment until the next header marker or end
                j = i + 1
                while j < len(b) and b[j] not in (0x7F, resp_sid):
                    j += 1
                segments.append(b[i:j])
                i = j
            else:
                i += 1
        if segments:
            # Flatten segments
            out: list[int] = []
            for seg in segments:
                out.extend(seg)
            self.last_status = None
            if self._current_req_id is not None and service == 0x21:
                self._last_tuple = (self._current_req_id, service, ident)
                self._last_resp = list(out)
                self._last_resp_ts = time.time()
            return out
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
        if self.use_mask_filter:
            # Use filter/mask pair instead of ATCRA (some clones handle CFs better)
            self._send(f"ATCF {resp}")
            self._read_lines(3.0)
            self._send("ATCM 7FF")
            self._read_lines(3.0)
        else:
            self._send(f"ATCRA {resp}")
            self._read_lines(3.0)
        self._current_req_id = req_id
        # Give the ELM/adapter a short settle time after header switch if configured
        if self.header_settle_ms and self.header_settle_ms > 0:
            if self.debug:
                print(f"[PYCANZE DEBUG] header_settle_ms={self.header_settle_ms} ms after ATSH/ATCRA")
            try:
                time.sleep(self.header_settle_ms / 1000.0)
            except Exception:
                pass
        # Mark that we've just switched to allow an optional delay before next 0x21
        self._just_switched = True
        # If a per-ECU first-0x21 delay is configured for this req id, override the generic one
        try:
            if req_id in self.first_21_delay_by_req:
                self.delay_before_21_ms = self.first_21_delay_by_req[req_id]
        except Exception:
            pass

    # Public helper to attempt a diagnostic session for a given field frame id (11-bit CAN)
    def ensure_session(self, frame_id: int, force: bool = False) -> None:
        """Best-effort session start for the ECU associated with frame_id.

        If ``force`` is True, sessions are attempted even if the ECU isn't
        marked as requiring one in the database. Useful for ECUs like LBC
        when accessing certain local identifiers (0x21).
        """
        fid = frame_id & 0x7FF
        req_id, resp_id = self._pair_for_frame(fid)
        self._select_frame(req_id, resp_id)
        self._ensure_session(req_id, force=force)

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
        rid = field.request_id.upper()
        if not (rid.startswith("22") or rid.startswith("21")):
            raise ValueError(f"Unsupported service in request id: {field.request_id}")
        # Switch to the ECU for this field if needed.
        # Select ECU headers for this field
        try:
            fid = field.frame_id & 0x7FF
            req_id, resp_id = self._pair_for_frame(fid)
            self._select_frame(req_id, resp_id)
            self._ensure_session(req_id)
        except Exception:
            # Fallback: keep current header; some fields may still respond
            pass
        service = int(rid[:2], 16)
        id_hex = rid[2:]
        ident = int(id_hex, 16)
        ident_len = 2 if len(id_hex) == 4 else 1
        resp = self._read_by_id(service, ident, ident_len)
        # Best-effort keep-alive while scanning
        self._tester_present()
        if not resp:
            return None
        # Ensure we have enough bytes to extract the requested bit range
        total_bits = len(resp) * 8
        if total_bits <= field.end_bit:
            return None
        raw_value = self._extract_bits(bytes(resp), field.start_bit, field.end_bit)
        return field.offset + field.resolution * raw_value

