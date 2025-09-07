"""UDS client for WiFi ELM327 dongles.

This module exposes :class:`UDSClient` which can communicate with a WiFi
ELM327 interface. When the optional ``python-OBD-wifi`` package is available,
it is used to manage the underlying connection; otherwise a small set of
socket helpers derived from ``Testing/zoe_arrival_poller.py`` is employed.
The client can query diagnostic data identifiers (DIDs) defined in the CanZE
database and decode the returned payload using the field's bit positions,
resolution and offset.  It is intentionally limited to read-only diagnostics;
write or actuation services (e.g. UDS 0x2E/0x31) are deliberately not
implemented.  Any future write support must be gated behind explicit
whitelists and safety checks.

The default initialisation mirrors the Android driver's AT sequence::

    ATZ; ATE0; ATS0; ATH0; ATL0; ATAL; ATCAF{0|1};
    ATFCSH77B; ATFCSD3000xx; ATFCSM1; ATSP6

Optional behaviour such as a *wide CF fallback* for LBC CF loss can be
enabled via environment variables or corresponding tool flags.
"""

from __future__ import annotations

import socket
import os
import time
import threading
from typing import Callable, Dict, Iterator, Optional, Sequence, Tuple, Union
import os
import socket
import time
import tempfile
import fcntl

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
    database is loaded so fields can be looked up by SID. The client only
    issues read-oriented UDS services (0x21/0x22 along with session control and
    tester-present keep-alives)."""

    # Future write support, if ever implemented, should live in dedicated
    # helpers (e.g. ``write_by_id``) that validate identifiers against a
    # whitelist and require explicit user confirmation or safeguards before
    # sending any UDS commands that could alter ECU state.

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
        # Global process lock to prevent concurrent sessions on one ELM
        self._lock_fh = None  # type: Optional[object]
        self._lock_path = os.environ.get(
            "PYCANZE_LOCK_PATH",
            os.path.join(tempfile.gettempdir(), "pycanze_elm.lock"),
        )
        if fields is not None:
            self.fields = fields
        else:
            # Default to classic ZOE dataset to avoid mixing 11/29-bit ECUs by default.
            # Can be overridden via PYCANZE_VEHICLE.
            try:
                veh = os.environ.get("PYCANZE_VEHICLE", "ZOE")
                self.fields = load_fields(vehicle=veh)[0]
            except Exception:
                # Fallback to all fields if specific dataset load fails
                self.fields = load_fields()[0]
        self.debug = bool(os.environ.get("PYCANZE_DEBUG"))
        # Map CAN IDs (both request and response) to (request_id, response_id)
        try:
            veh = os.environ.get("PYCANZE_VEHICLE", "ZOE")
            _ecus = load_ecus(vehicle=veh)
        except Exception:
            _ecus = {}
        self._ecu_by_can = {}
        self._net_by_req = {}  # req_id -> list of networks
        self._session_required_by_req = {}  # req_id -> bool
        self._session_started = set()  # req_ids with active session
        self._last_tp = 0.0
        # Last UDS negative response code (e.g. 0x22 ConditionsNotCorrect)
        self.last_nrc_code = None
        # Keep the EVC (0x7E4/0x7EC) session alive as a gateway keep-alive when
        # talking to other ECUs. Some ZOE variants appear to require periodic
        # TesterPresent to the EVC to allow bridging to V/E networks.
        self._evc_req_id = 0x7E4
        self._evc_resp_id = 0x7EC
        self._last_evc_tp = 0.0
        self._evc_tp_interval = 1.2  # seconds between EVC TesterPresent
        # Use a slightly shorter TesterPresent cadence to keep ECUs lively
        self._tp_interval = 1.2  # seconds between TesterPresent keep-alives
        # Base read timeout for a single UDS request-prompt cycle (socket level)
        # This is distinct from the TCP connect timeout; it is intentionally
        # short and will be scaled adaptively similar to the Android app.
        self.read_timeout_s = 0.8
        # Adaptive timeout controls (Android-like intervalMultiplicator)
        self.adaptive_timeouts = True
        self._interval_multiplier = 1.6
        self._interval_min = 1.3
        self._interval_max = 2.5
        self._interval_step_up = 0.10   # on failure
        self._interval_step_down = 0.01 # on success
        # Short-lived cache for repeated 0x21 page reads: (req_id, service, ident) -> response bytes
        self._last_tuple = None
        self._last_resp = None
        self._last_resp_ts = 0.0
        # Default to 11-bit; 29-bit only if explicitly forced via env at init.
        # Per-ECU switching is handled in _select_frame.
        self._use_29bit = False
        # Build ECU maps for header selection and session requirements
        for ecu in _ecus.values():
            try:
                # Skip entries with invalid CAN ids (0/0 placeholders)
                if (getattr(ecu, "request_id", 0) == 0) or (
                    getattr(ecu, "response_id", 0) == 0
                ):
                    continue
                # Parser stores FromID in request_id (ECU->tester) and ToID in response_id (tester->ECU).
                # Swap to get (req=ToID, resp=FromID) and keep full 29-bit identifiers.
                req = ecu.response_id & 0x1FFFFFFF
                resp = ecu.request_id & 0x1FFFFFFF
                self._ecu_by_can[req] = (req, resp)
                self._ecu_by_can[resp] = (req, resp)
                self._net_by_req[req] = ecu.networks
                self._session_required_by_req[req] = bool(
                    getattr(ecu, "session_required", 0)
                )
            except Exception:
                continue
        # Respect explicit 29-bit override at init; otherwise start in 11-bit and
        # let _select_frame switch per ECU as needed.
        try:
            v29 = os.environ.get("PYCANZE_FORCE_29BIT")
            if v29 and v29.strip().lower() not in ("0", "false", "no", ""):
                self._use_29bit = True
        except Exception:
            pass
        # Last ELM/CAN status hint (e.g. 'CAN_ERROR', 'NO_DATA')
        self.last_status = None
        # Whether the last read had any positive UDS response bytes
        # (useful for scanners to count transport successes even if decoding
        # yields a sentinel/invalid value and returns None)
        self.last_positive = False
        # Length of the last raw positive response (bytes)
        self.last_raw_len = 0
        # Buffer of the last positive response (full positive buffer: SID+echoed ID+data)
        self.last_resp_buf = None
        # Track currently selected CAN request id (11- or 29-bit)
        self._current_req_id = None
        # Tunables (can be overridden by tools)
        self.caf = None  # 0 or 1 for ATCAF
        self.fc_stmin_ms = None  # STmin ms for ATFCSD 3000xx
        self.header_settle_ms = 0.0  # sleep after ATSH/ATCRA
        self.delay_before_21_ms = 0.0  # sleep before first 0x21 after switch
        self._just_switched = False
        self.use_mask_filter = False  # use ATCF/ATCM instead of ATCRA
        self.fc_retry_enabled = True  # allow FC reassert retry
        self.wide_cf_fallback = False  # allow temporary ATH1/filter widening
        # Additional timing controls
        self.isotp_collect_timeout_s = (
            2.5  # total window to collect multi-frame payload
        )
        self.cf_read_timeout_s = 1.2  # per read timeout while collecting CFs
        # Optional per-ECU first-0x21 delay (currently used for LBC 0x7BB)
        self.first_21_delay_by_req = {}
        # Sniffing state
        self._sniffing = False
        self._sniff_thread = None
        # Decoding controls
        self.disable_all_ones_sentinel = False
        # Decode reference: by default bit offsets are relative to the full
        # positive response (SID+echoed ID+data). Set via env to payload-only
        # to test datasets that define offsets excluding the UDS header bytes.
        self.decode_against_full_response = True

    # ------------------------------------------------------------------
    @staticmethod
    def _nrc_text(code: int) -> str:
        mapping = {
            0x10: "GeneralReject",
            0x11: "ServiceNotSupported",
            0x12: "SubFunctionNotSupportedInvalidFormat",
            0x13: "IncorrectMessageLengthOrInvalidFormat",
            0x22: "ConditionsNotCorrect",
            0x31: "RequestOutOfRange",
            0x33: "SecurityAccessDenied",
            0x35: "InvalidKey",
            0x36: "ExceededNumberOfAttempts",
            0x37: "RequiredTimeDelayNotExpired",
            0x78: "ResponsePending",
            0x7E: "SubFunctionNotSupportedInActiveSession",
            0x7F: "ServiceNotSupportedInActiveSession",
        }
        return mapping.get(code & 0xFF, f"NRC_0x{code:02X}")

    # sleep hook -------------------------------------------------------------
    def _sleep(self, duration: float) -> None:
        """Sleep for the given duration (seconds).

        Subclasses may override this to skip delays during testing.
        """
        time.sleep(duration)

    def _pair_for_frame(self, fid: int):
        """Return ``(req_id, resp_id)`` for a given CAN id.

        Tries direct lookup; if missing, searches by matching response id in
        the known pairs; finally falls back to standard +8 mapping. Supports
        both 11‑bit and 29‑bit identifiers.
        """
        fid &= 0x1FFFFFFF
        pair = self._ecu_by_can.get(fid)
        if pair is not None:
            return pair
        # Search by response id match
        for _k, pr in self._ecu_by_can.items():
            try:
                if pr[1] == fid:
                    return pr
            except Exception:
                continue
        # Fallback to standard UDS addressing heuristic (req = resp - 0x8)
        mask = 0x1FFFFFFF if fid > 0x7FF else 0x7FF
        return ((fid - 0x8) & mask, fid)

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
            # Try common sessions: Extended (0xC0), EPS-specific (0xFA), Renault (0xF2), LGChem (0xF3),
            # followed by default sessions (0x81 and 0x00). Some ECUs like DCM only accept 0x1000.
            for mode, expect in (
                ("0210C0", "50C0"),
                ("0210FA", "50FA"),
                ("0210F2", "50F2"),
                ("0210F3", "50F3"),
                ("021081", "5081"),
                ("021000", "5000"),
            ):
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
                # Even if we skip current ECU TP due to interval throttling,
                # still consider keeping the EVC session alive.
                self._evc_keepalive(now)
                return
            # 0x3E 0x01 (TesterPresent, with response)
            self._send("023E01")
            _ = self._read_lines(1.0)
            self._last_tp = now
            # Also keep the EVC gateway session alive
            self._evc_keepalive(now)
        except Exception:
            return

    # ------------------------------------------------------------------
    def _evc_keepalive(self, now_ts: Optional[float] = None) -> None:
        """Periodically send TesterPresent to the EVC (0x7E4/0x7EC).

        Some vehicles require the EVC to stay in a diagnostic session for
        other ECUs to reliably respond. We briefly switch headers to EVC,
        send a TesterPresent, then restore the previous headers.
        """
        try:
            now = time.time() if now_ts is None else now_ts
            if now - self._last_evc_tp < self._evc_tp_interval:
                return
            # Save current header
            prev_req = self._current_req_id
            prev_resp = None
            if prev_req is not None:
                try:
                    prev_req, prev_resp = self._pair_for_frame(prev_req)
                except Exception:
                    prev_resp = None
            # Switch to EVC header
            self._select_frame(self._evc_req_id, self._evc_resp_id)
            # TesterPresent to EVC
            self._send("023E01")
            _ = self._read_lines(1.0)
            self._last_evc_tp = now
            # Restore previous header if any
            if prev_req is not None:
                try:
                    self._select_frame(prev_req, prev_resp)
                except Exception:
                    pass
        except Exception:
            return

    # ------------------------------------------------------------------
    def gateway_poke(self) -> None:
        """Best-effort EVC poke to encourage gateway bridging.

        Starts/refreshes a session on EVC (0x7E4) and queries configuration
        DIDs that are safe and read-only. Then restores the previous header.
        Non-fatal on failure.
        """
        try:
            # Save current selection
            prev_req = self._current_req_id
            prev_resp = None
            if prev_req is not None:
                try:
                    prev_req, prev_resp = self._pair_for_frame(prev_req)
                except Exception:
                    prev_resp = None
            # Switch to EVC
            self._select_frame(self._evc_req_id, self._evc_resp_id)
            # Default session (ignore failure)
            try:
                self._send("021081")
                self._read_lines(1.5)
            except Exception:
                pass
            # Read two benign DIDs that list networks/ECUs
            for cmd in ("0221B7", "0221B8"):
                try:
                    self._send(cmd)
                    self._read_lines(1.0)
                except Exception:
                    pass
            # TesterPresent (no response) to leave EVC quiet but alive
            try:
                self._send("023E00")
                self._read_lines(0.5)
            except Exception:
                pass
        finally:
            if prev_req is not None:
                try:
                    self._select_frame(prev_req, prev_resp)
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Socket helpers (straight from ``zoe_arrival_poller.py``)
    def _send(self, line: str, wait: float = ELM_CMD_SLEEP) -> None:
        assert self.sock is not None
        if self.debug:
            print(f"[PYCANZE DEBUG] SEND: {line}")
        self.sock.sendall((line + "\r").encode("ascii", errors="ignore"))
        self._sleep(wait)

    def _read_lines(self, timeout: float | None = None) -> Sequence[str]:
        assert self.sock is not None
        # Prefer adaptive per-read timeout over the global connect timeout
        t = self.read_timeout_s if timeout is None else float(timeout)
        if getattr(self, "adaptive_timeouts", True):
            try:
                mult = float(getattr(self, "_interval_multiplier", 1.6) or 1.6)
            except Exception:
                mult = 1.6
            t = max(0.05, t * mult)
        self.sock.settimeout(t)
        buf = b""
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b">" in buf:
                break
        text = buf.decode(errors="ignore").replace("\r", "\n")
        lines = [
            ln.strip() for ln in text.split("\n") if ln.strip() and ln.strip() != ">"
        ]
        if self.debug:
            print(f"[PYCANZE DEBUG] RECV: {lines}")
        return lines

    @staticmethod
    def _only_hex_bytes(lines: Sequence[str]) -> Sequence[int]:
        out = []
        for ln in lines:
            up = ln.upper()
            if any(
                k in up
                for k in ["NO DATA", "ERROR", "SEARCHING", "BUS INIT", "CAN ERROR"]
            ):
                continue
            only_hex = "".join(ch for ch in ln if ch.upper() in "0123456789ABCDEF")
            out.extend(int(only_hex[i : i + 2], 16) for i in range(0, len(only_hex), 2))
        return out

    # Simple adaptive timeout adjustment inspired by Android driver
    def _adapt_on_success(self) -> None:
        try:
            if not getattr(self, "adaptive_timeouts", True):
                return
            cur = float(self._interval_multiplier)
            lo = float(self._interval_min)
            step = float(self._interval_step_down)
            self._interval_multiplier = max(lo, cur - step)
        except Exception:
            pass

    def _adapt_on_failure(self) -> None:
        try:
            if not getattr(self, "adaptive_timeouts", True):
                return
            cur = float(self._interval_multiplier)
            hi = float(self._interval_max)
            step = float(self._interval_step_up)
            self._interval_multiplier = min(hi, cur + step)
        except Exception:
            pass

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
            self.sock = socket.create_connection(
                (self.host, self.port), timeout=self.timeout
            )
        # Try to acquire non-blocking exclusive lock with stale-PID check
        def _pid_alive(pid: int) -> bool:
            try:
                if pid <= 0:
                    return False
                os.kill(pid, 0)
                return True
            except ProcessLookupError:
                return False
            except PermissionError:
                return True
            except Exception:
                return True

        try:
            # Do not truncate before taking the lock
            self._lock_fh = open(self._lock_path, "a+")
            fcntl.flock(self._lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            # We own the lock: write our PID atomically
            try:
                self._lock_fh.seek(0)
                self._lock_fh.truncate(0)
                self._lock_fh.write(f"pid={os.getpid()}\n")
                self._lock_fh.flush()
            except Exception:
                pass
        except BlockingIOError:
            # Someone holds the lock: inspect the recorded PID
            stale_pid = None
            try:
                with open(self._lock_path, "r") as _fh:
                    first = _fh.readline().strip()
                    if first.lower().startswith("pid="):
                        stale_pid = int(first.split("=", 1)[1] or "0")
            except Exception:
                stale_pid = None
            # If the recorded PID is not alive, retry to take over the lock briefly
            if stale_pid is not None and not _pid_alive(stale_pid):
                for _ in range(20):  # ~2s total
                    try:
                        # Reopen fresh handle each attempt
                        fh = open(self._lock_path, "a+")
                        try:
                            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            self._lock_fh = fh
                            # Write our PID
                            try:
                                self._lock_fh.seek(0)
                                self._lock_fh.truncate(0)
                                self._lock_fh.write(f"pid={os.getpid()}\n")
                                self._lock_fh.flush()
                            except Exception:
                                pass
                            break
                        except BlockingIOError:
                            fh.close()
                            time.sleep(0.1)
                    except Exception:
                        time.sleep(0.1)
                if self._lock_fh is None:
                    raise RuntimeError(
                        f"Stale PyCanZE lock detected (pid={stale_pid}) but still locked (lock: {self._lock_path})."
                        " Please wait a moment or remove the stale process."
                    )
            else:
                # Active holder present
                holder = f" pid={stale_pid}" if stale_pid else ""
                raise RuntimeError(
                    f"Another PyCanZE session is active{holder} (lock: {self._lock_path}). "
                    "Please stop it before starting a new scan."
                )
        except Exception:
            # Best-effort: continue even if lock cannot be taken due to filesystem issues
            self._lock_fh = None

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
                self.fc_stmin_ms = int(
                    os.environ.get("PYCANZE_FC_STMIN_MS", "0").strip()
                )
        except Exception:
            self.fc_stmin_ms = None
        try:
            if not self.header_settle_ms and os.environ.get("PYCANZE_HEADER_SETTLE_MS"):
                self.header_settle_ms = float(
                    os.environ.get("PYCANZE_HEADER_SETTLE_MS", "0").strip()
                )
        except Exception:
            self.header_settle_ms = 0.0
        try:
            if not self.delay_before_21_ms and os.environ.get(
                "PYCANZE_DELAY_BEFORE_21_MS"
            ):
                self.delay_before_21_ms = float(
                    os.environ.get("PYCANZE_DELAY_BEFORE_21_MS", "0").strip()
                )
        except Exception:
            self.delay_before_21_ms = 0.0
        try:
            if os.environ.get("PYCANZE_USE_MASK_FILTER"):
                self.use_mask_filter = os.environ.get(
                    "PYCANZE_USE_MASK_FILTER", ""
                ).strip() not in ("0", "false", "False", "")
        except Exception:
            self.use_mask_filter = False
        try:
            if os.environ.get("PYCANZE_WIDE_CF_FALLBACK"):
                self.wide_cf_fallback = os.environ.get(
                    "PYCANZE_WIDE_CF_FALLBACK", ""
                ).strip() not in (
                    "0",
                    "false",
                    "False",
                    "",
                )
        except Exception:
            self.wide_cf_fallback = False
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
            v = os.environ.get("PYCANZE_EVC_TP_INTERVAL_MS")
            if v:
                self._evc_tp_interval = float(v) / 1000.0
        except Exception:
            pass
        # Adaptive timeout environment overrides
        try:
            v = os.environ.get("PYCANZE_READ_TIMEOUT_S")
            if v:
                self.read_timeout_s = float(v)
        except Exception:
            pass
        try:
            v = os.environ.get("PYCANZE_ADAPTIVE_TIMEOUTS")
            if v is not None:
                self.adaptive_timeouts = v.strip() not in ("0", "false", "False", "")
        except Exception:
            pass
        for key, attr in (
            ("PYCANZE_INTERVAL_MULT", "_interval_multiplier"),
            ("PYCANZE_INTERVAL_MIN", "_interval_min"),
            ("PYCANZE_INTERVAL_MAX", "_interval_max"),
            ("PYCANZE_INTERVAL_STEP_UP", "_interval_step_up"),
            ("PYCANZE_INTERVAL_STEP_DOWN", "_interval_step_down"),
        ):
            try:
                v = os.environ.get(key)
                if v:
                    setattr(self, attr, float(v))
            except Exception:
                pass
        try:
            v = os.environ.get("PYCANZE_FC_RETRY")
            if v is not None:
                self.fc_retry_enabled = v.strip() not in ("0", "false", "False", "")
        except Exception:
            pass
        try:
            v = os.environ.get("PYCANZE_DISABLE_ALL_ONES_SENTINEL")
            if v is not None:
                self.disable_all_ones_sentinel = v.strip() not in ("0", "false", "False", "")
        except Exception:
            pass
        try:
            v = os.environ.get("PYCANZE_DECODE_PAYLOAD_ONLY")
            if v is not None:
                # If set truthy, decode against payload only (exclude SID+ID)
                self.decode_against_full_response = v.strip() in ("0", "false", "False", "")
        except Exception:
            pass
        # Per-ECU first-0x21 delay: allow targeting LBC specifically
        try:
            v = os.environ.get("PYCANZE_FIRST_21_DELAY_LBC_MS")
            if v:
                # LBC request id (tester->ECU) is 0x79B; response is 0x7BB
                self.first_21_delay_by_req[0x79B] = float(v)
        except Exception:
            pass
        # Reset and basic config mirroring Android's sequence
        self._send("ATZ", wait=0.3)
        self._read_lines(3.0)
        caf_mode = 0 if self.caf is None else int(self.caf)
        stmin = (
            0 if self.fc_stmin_ms is None else max(0, min(255, int(self.fc_stmin_ms)))
        )
        proto_cmd = "ATSP7" if self._use_29bit else "ATSP6"
        init_cmds = [
            "ATE0",
            "ATS0",
            "ATH0",
            "ATL0",
            "ATAL",
            "ATAT1",  # auto timing like Android app
            f"ATCAF{caf_mode}",
            "ATFCSH77B",
            f"ATFCSD 3000{stmin:02X}",
            "ATFCSM1",
            proto_cmd,
        ]
        if self._use_29bit:
            init_cmds.append("ATCP 00")
        for cmd in init_cmds:
            self._send(cmd)
            self._read_lines(3.0)
        # Some ELM 1.5 clones require explicit CFC enable
        try:
            self._send("ATCFC1")
            self._read_lines(3.0)
        except Exception:
            pass
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
        if self._use_29bit:
            self._send("ATSH000007E4")
            self._read_lines(3.0)
            self._send("ATFCSH000007E4")
            self._read_lines(3.0)
            self._send("ATCRA 000007EC")
            self._read_lines(3.0)
        else:
            self._send("ATSH7E4")
            self._read_lines(3.0)
            self._send("ATFCSH7E4")
            self._read_lines(3.0)
            self._send("ATCRA 7EC")
            self._read_lines(3.0)
        self._current_req_id = 0x7E4
        self._just_switched = False
        # Start a basic session on EVC and seed a TesterPresent to keep the
        # gateway alive. Ignore failures as not all adapters/variants need it.
        try:
            self._send("021081")  # Default session
            self._read_lines(1.5)
        except Exception:
            pass
        try:
            self._send("023E00")  # TesterPresent
            self._read_lines(1.0)
            self._last_evc_tp = time.time()
        except Exception:
            pass

    def close(self) -> None:
        """Close the TCP connection."""

        if self.sock is not None:
            self.sock.close()
            self.sock = None
        # Release lock last
        if self._lock_fh is not None:
            try:
                fcntl.flock(self._lock_fh.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                self._lock_fh.close()
            except Exception:
                pass
            self._lock_fh = None

    # ------------------------------------------------------------------
    def _sniff_loop(self) -> Iterator[Tuple[int, bytes]]:
        """Internal generator yielding ``(frame_id, payload)`` tuples."""

        assert self.sock is not None
        self._sniffing = True
        self._send("ATMA", wait=0.0)
        self.sock.settimeout(0.2)
        buf = b""
        while self._sniffing:
            try:
                chunk = self.sock.recv(4096)
            except Exception:
                continue
            if not chunk:
                continue
            buf += chunk
            while b"\r" in buf or b"\n" in buf:
                for sep in (b"\r", b"\n"):
                    if sep in buf:
                        line, buf = buf.split(sep, 1)
                        break
                text = line.decode(errors="ignore").strip()
                if not text or text == ">" or "STOPPED" in text:
                    continue
                parts = text.split()
                try:
                    fid = int(parts[0], 16)
                    payload = bytes(int(p, 16) for p in parts[1:])
                except Exception:
                    continue
                yield fid, payload
        try:
            self.sock.settimeout(self.timeout)
        except Exception:
            pass

    def start_sniffing(
        self, callback: Optional[Callable[[int, bytes], None]] = None
    ) -> Iterator[Tuple[int, bytes]] | None:
        """Start ``ATMA`` sniffing.

        If ``callback`` is provided, frames are delivered via the function in a
        background thread and the method returns ``None``. Otherwise an iterator
        yielding ``(frame_id, payload)`` tuples is returned and should be
        consumed by the caller. Call :meth:`stop_sniffing` to stop.
        """

        if self.sock is None:
            raise RuntimeError("connect() must be called before sniffing")
        if callback is None:
            return self._sniff_loop()

        def _run() -> None:
            for fid, payload in self._sniff_loop():
                callback(fid, payload)

        self._sniff_thread = threading.Thread(target=_run, daemon=True)
        self._sniff_thread.start()
        return None

    def stop_sniffing(self) -> None:
        """Stop active ``ATMA`` sniffing."""

        if not self._sniffing:
            return
        self._sniffing = False
        if self.sock is not None:
            try:
                self.sock.sendall(b"\x03")  # Ctrl+C abort
                # Flush any remaining lines including the prompt
                self.sock.settimeout(0.2)
                try:
                    self.sock.recv(4096)
                except Exception:
                    pass
            except Exception:
                pass
        if self._sniff_thread is not None:
            self._sniff_thread.join(timeout=1.0)
            self._sniff_thread = None

    # ------------------------------------------------------------------
    def _read_by_id(
        self, service: int, ident: int, ident_len: int
    ) -> Optional[Sequence[int]]:
        """Send a generic read-by-identifier request and return raw response bytes.

    - For service 0x22 (ReadDataByIdentifier), ``ident_len`` is 2 (16-bit DID).
    Returns bytes starting from the positive response SID (service+0x40) or ``None``.
        """
        resp_sid = (service + 0x40) & 0xFF
        # Reset positive flags for this request
        self.last_positive = False
        self.last_raw_len = 0
        self.last_resp_buf = None
        if ident_len == 2:
            hi = (ident >> 8) & 0xFF
            lo = ident & 0xFF
            cmd = f"03{service:02X}{hi:02X}{lo:02X}"
        elif ident_len == 1:
            cmd = f"02{service:02X}{ident & 0xFF:02X}"
        else:
            raise ValueError("Unsupported identifier length")
        if self.debug:
            hdr = self._current_req_id
            proto = "29bit" if (self._use_29bit or (hdr is not None and hdr > 0x7FF)) else "11bit"
            hdr_str = f"0x{hdr:x}" if isinstance(hdr, int) else "None"
            print(f"[PYCANZE DEBUG] UDS READ: {cmd} (hdr={hdr_str} proto={proto})")
        # Optional delay just before the first 0x21 after switching headers
        if (
            service == 0x21
            and self._just_switched
            and self.delay_before_21_ms
            and self.delay_before_21_ms > 0
        ):
            if self.debug:
                print(
                    f"[PYCANZE DEBUG] delay_before_21_ms={self.delay_before_21_ms} ms before first 0x21"
                )
            try:
                self._sleep(self.delay_before_21_ms / 1000.0)
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
            self._adapt_on_success()
            return list(self._last_resp)
        # Clear last NRC before issuing request
        self.last_nrc_code = None
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
        # If adapter reported an error and we did not receive any hex bytes, adapt as failure
        if getattr(self, "last_status", None) in {"CAN_ERROR", "NO_DATA", "ELM_ERROR"} and not b:
            self._adapt_on_failure()
            self.last_positive = False
            self.last_raw_len = 0
            return None
        expected_len = b[0] if b and b[0] < 0x10 else 0
        if self.debug:
            print(f"[PYCANZE DEBUG] PARSED HEX: {b}")
        # Manual ISO-TP reassembly fallback (without sending our own Flow Control)
        if len(b) >= 3 and (b[0] >> 4) == 0x1:
            total_len = ((b[0] & 0x0F) << 8) | (b[1] & 0xFF)
            collected: list[int] = []
            take = min(6, len(b) - 2)
            if take > 0:
                collected.extend(b[2 : 2 + take])
            j = 2 + take
            expected_sn = 1
            while len(collected) < total_len and j < len(b):
                pci = b[j]
                if (pci >> 4) != 0x2:
                    break
                sn = pci & 0x0F
                if sn != (expected_sn & 0x0F):
                    self._adapt_on_failure()
                    return None
                expected_sn = (expected_sn + 1) & 0x0F
                take = min(7, len(b) - (j + 1), total_len - len(collected))
                if take > 0:
                    collected.extend(b[j + 1 : j + 1 + take])
                j += 1 + take
            deadline = time.time() + float(
                getattr(self, "isotp_collect_timeout_s", 2.5) or 2.5
            )
            while len(collected) < total_len and time.time() < deadline:
                try:
                    more = self._read_lines(
                        float(getattr(self, "cf_read_timeout_s", 1.2) or 1.2)
                    )
                except Exception:
                    break
                bb = self._only_hex_bytes(more)
                if not bb:
                    continue
                j = 0
                while j < len(bb):
                    pci = bb[j]
                    if (pci >> 4) == 0x2:
                        sn = pci & 0x0F
                        if sn != (expected_sn & 0x0F):
                            return None
                        expected_sn = (expected_sn + 1) & 0x0F
                        take = min(7, len(bb) - (j + 1), total_len - len(collected))
                        if take > 0:
                            collected.extend(bb[j + 1 : j + 1 + take])
                        j += 1 + take
                    else:
                        j += 1
            out = collected[:total_len]
            if out and out[0] == resp_sid and len(out) >= total_len:
                self.last_status = None
                self.last_positive = True
                self.last_raw_len = len(out)
                self.last_resp_buf = list(out)
                if self._current_req_id is not None and service == 0x21:
                    self._last_tuple = (self._current_req_id, service, ident)
                    self._last_resp = list(out)
                    self._last_resp_ts = time.time()
                return out
            if (
                len(collected) < total_len
                and self.fc_retry_enabled
                and not getattr(self, "_fc_retry_active", False)
            ):
                try:
                    setattr(self, "_fc_retry_active", True)
                    stmin = 0 if self.fc_stmin_ms is None else max(0, min(255, int(self.fc_stmin_ms)))
                    for cmd_fc in ("ATFCSM1", f"ATFCSD 3000{stmin:02X}", "ATCFC1", "ATAL"):
                        try:
                            self._send(cmd_fc)
                            self._read_lines(1.0)
                        except Exception:
                            pass
                    if self.debug:
                        print("[PYCANZE DEBUG] ISO-TP FF without CFs; reasserted FC, retrying once")
                    self._sleep(0.05)
                    return self._read_by_id(service, ident, ident_len)
                finally:
                    setattr(self, "_fc_retry_active", False)
            if len(collected) < total_len and getattr(self, "wide_cf_fallback", False):
                if self.debug:
                    print("[PYCANZE DEBUG] WIDE-CF fallback: ATH1 + ATCM/ATCF=000, resending request")
                resp_id = 0
                if self._current_req_id is not None:
                    resp_id = self._pair_for_frame(self._current_req_id)[1]
                resp_hex = f"{resp_id & 0x7FF:03X}"
                try:
                    self._send("ATH1")
                    self._read_lines(1.0)
                    self._send("ATCM 000")
                    self._read_lines(1.0)
                    self._send("ATCF 000")
                    self._read_lines(1.0)
                    self._sleep(0.02)
                    self._send(cmd)
                    self._read_lines(self.timeout)
                    while len(collected) < total_len and time.time() < deadline:
                        try:
                            more = self._read_lines(
                                float(getattr(self, "cf_read_timeout_s", 1.2) or 1.2)
                            )
                        except Exception:
                            break
                        for ln in more:
                            up = ln.upper().replace(" ", "")
                            if not up.startswith(resp_hex):
                                continue
                            hex_part = "".join(ch for ch in up[len(resp_hex) :] if ch in "0123456789ABCDEF")
                            bb = [int(hex_part[i : i + 2], 16) for i in range(0, len(hex_part), 2)]
                            j = 0
                            while j < len(bb):
                                pci = bb[j]
                                if (pci >> 4) == 0x2:
                                    sn = pci & 0x0F
                                    if sn != (expected_sn & 0x0F):
                                        break
                                    expected_sn = (expected_sn + 1) & 0x0F
                                    take = min(7, len(bb) - (j + 1), total_len - len(collected))
                                    if take > 0:
                                        collected.extend(bb[j + 1 : j + 1 + take])
                                    j += 1 + take
                                else:
                                    j += 1
                finally:
                    try:
                        self._send("ATCM 7FF")
                        self._read_lines(1.0)
                        self._send(f"ATCF {resp_hex}")
                        self._read_lines(1.0)
                    except Exception:
                        pass
                    try:
                        self._send("ATH0")
                        self._read_lines(1.0)
                    except Exception:
                        pass
                if len(collected) >= total_len:
                    out = collected[:total_len]
                    if out and out[0] == resp_sid and len(out) >= total_len:
                        self.last_status = None
                        if self._current_req_id is not None and service == 0x21:
                            self._last_tuple = (self._current_req_id, service, ident)
                            self._last_resp = list(out)
                            self._last_resp_ts = time.time()
                        self.last_positive = True
                        self.last_raw_len = len(out)
                        self.last_resp_buf = list(out)
                        self._adapt_on_success()
                        return out
            self._adapt_on_failure()
            self.last_positive = False
            self.last_raw_len = 0
            return None
        # Segment concatenation path
        segments: list[Sequence[int]] = []
        i = 0
        while i < len(b):
            if b[i] == 0x7F:
                if (i + 2) < len(b):
                    try:
                        self.last_nrc_code = b[i + 2] & 0xFF
                        self.last_status = "NEG"
                    except Exception:
                        self.last_status = "NEG"
                    self._adapt_on_failure()
                    self.last_positive = False
                    self.last_raw_len = 0
                    return None
                break
            if b[i] == resp_sid:
                if ident_len == 2 and (i + 2) < len(b):
                    did_hi = (ident >> 8) & 0xFF
                    did_lo = ident & 0xFF
                    if b[i + 1] != did_hi or b[i + 2] != did_lo:
                        i += 1
                        continue
                if ident_len == 1 and (i + 1) < len(b):
                    if b[i + 1] != (ident & 0xFF):
                        i += 1
                        continue
                j = i + 1
                while j < len(b) and b[j] not in (0x7F, resp_sid):
                    j += 1
                segments.append(b[i:j])
                i = j
            else:
                i += 1
        if segments:
            out: list[int] = []
            for idx, seg in enumerate(segments):
                if idx == 0:
                    out.extend(seg)
                else:
                    drop = 1 + (2 if ident_len == 2 else 1)
                    payload = seg[drop:] if len(seg) > drop else []
                    out.extend(payload)
            # Do not trim trailing bytes. Some ECUs legitimately end pages
            # with 0x00/0xFF padding or zero-valued data, and trimming here
            # can shorten the buffer below CSV-defined bit ranges causing
            # decoders to return None. Keep the full concatenated response.
            min_len = 1 + (2 if ident_len == 2 else 1) + 1
            if expected_len:
                min_len = max(min_len, expected_len)
            if not out or out[0] != resp_sid or len(out) < min_len:
                self._adapt_on_failure()
                return None
            self.last_status = None
            self.last_positive = True
            self.last_raw_len = len(out)
            self.last_resp_buf = list(out)
            if self._current_req_id is not None and service == 0x21:
                self._last_tuple = (self._current_req_id, service, ident)
                self._last_resp = list(out)
                self._last_resp_ts = time.time()
            self._adapt_on_success()
            return out
        self._adapt_on_failure()
        self.last_positive = False
        self.last_raw_len = 0
        self.last_resp_buf = None
        return None

    # ------------------------------------------------------------------
    def _select_frame(self, req_id: int, resp_id: Optional[int] = None) -> None:
        """Ensure ELM headers/filters are set for the given CAN request id."""

        if req_id <= 0 or req_id > 0x1FFFFFFF:
            return
        if self.sock is None:
            raise RuntimeError("connect() must be called before reading fields")
        if self._current_req_id == req_id:
            return
        # Decide header format per ECU: prefer env overrides, otherwise by id size
        needed_ext = False
        try:
            v29 = os.environ.get("PYCANZE_FORCE_29BIT")
            if v29 and v29.strip().lower() not in ("0", "false", "no", ""):
                needed_ext = True
        except Exception:
            pass
        # If not explicitly forced, infer from id magnitude
        if not needed_ext:
            needed_ext = (req_id > 0x7FF) or (resp_id is not None and resp_id > 0x7FF)
        # Never downforce 11-bit for truly extended IDs: ignore FORCE_11BIT here
        if needed_ext != self._use_29bit:
            # Switch CAN protocol on the adapter
            self._send("ATSP7" if needed_ext else "ATSP6")
            self._read_lines(3.0)
            if needed_ext:
                # Required for extended addressing on some ELMs
                self._send("ATCP 00")
                self._read_lines(3.0)
            self._use_29bit = needed_ext
            # Invalidate previously selected header
            self._current_req_id = None
        ext = needed_ext
        if ext:
            rid = f"{req_id & 0x1FFFFFFF:08X}"
            rpid = (
                resp_id if resp_id is not None else (req_id + 0x8)
            ) & 0x1FFFFFFF
            resp = f"{rpid:08X}"
        else:
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
            self._send("ATCM 7FF" if not ext else "ATCM 1FFFFFFF")
            self._read_lines(3.0)
        else:
            self._send(f"ATCRA {resp}")
            self._read_lines(3.0)
        self._current_req_id = req_id
        # Give the ELM/adapter a short settle time after header switch if configured
        if self.header_settle_ms and self.header_settle_ms > 0:
            if self.debug:
                print(
                    f"[PYCANZE DEBUG] header_settle_ms={self.header_settle_ms} ms after ATSH/ATCRA"
                )
            try:
                self._sleep(self.header_settle_ms / 1000.0)
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
        # DCM/LBC priming: some ECUs respond better when first pinged
        try:
            if req_id in (0x7CA, 0x18DAF110):  # DCM (tester->ECU: 11-bit and a common 29-bit)
                # Increase settle and first-0x21 delays slightly for DCM
                self.header_settle_ms = max(getattr(self, "header_settle_ms", 0.0) or 0.0, 40.0)
                self.delay_before_21_ms = max(getattr(self, "delay_before_21_ms", 0.0) or 0.0, 100.0)
                # Send a TesterPresent (no response) to wake DCM, ignore errors
                try:
                    self._send("023E00")
                    self._read_lines(0.8)
                except Exception:
                    pass
                # Follow up with a TesterPresent expecting a response
                try:
                    self._send("023E01")
                    self._read_lines(1.0)
                except Exception:
                    pass
                # Additionally try a functional broadcast prime (7DF -> expect 7DA)
                try:
                    # Remember current header strings to restore exactly
                    ext_now = ext
                    rid_now = f"{(req_id & 0x1FFFFFFF):08X}" if ext_now else f"{(req_id & 0x7FF):03X}"
                    resp_now = (
                        (resp_id if resp_id is not None else (req_id + 0x8)) & (0x1FFFFFFF if ext_now else 0x7FF)
                    )
                    resp_now_s = f"{resp_now:08X}" if ext_now else f"{resp_now:03X}"
                    # Switch to functional broadcast (11-bit only), filter DCM response, send TP
                    self._send("ATSH7DF")
                    self._read_lines(0.6)
                    self._send("ATCRA 7DA")
                    self._read_lines(0.6)
                    self._send("023E01")
                    self._read_lines(1.0)
                except Exception:
                    pass
                finally:
                    # Restore previous header/filter unconditionally
                    try:
                        self._send(f"ATSH{rid_now}")
                        self._read_lines(0.6)
                        if self.use_mask_filter:
                            self._send(f"ATCF {resp_now_s}")
                            self._read_lines(0.6)
                            self._send("ATCM 7FF" if not ext_now else "ATCM 1FFFFFFF")
                            self._read_lines(0.6)
                        else:
                            self._send(f"ATCRA {resp_now_s}")
                            self._read_lines(0.6)
                    except Exception:
                        pass
            if req_id in (0x79B, 0x796):  # LBC (0x79B) and LBC2 (0x796)
                # LBC/LBC2 often benefit from a short pre-delay and ping when switching
                self.header_settle_ms = max(getattr(self, "header_settle_ms", 0.0) or 0.0, 35.0)
                self.delay_before_21_ms = max(getattr(self, "delay_before_21_ms", 0.0) or 0.0, 80.0)
                try:
                    self._send("023E00")
                    self._read_lines(0.6)
                except Exception:
                    pass
        except Exception:
            pass

    # Public helper to attempt a diagnostic session for a given field frame id
    def ensure_session(self, frame_id: int, force: bool = False) -> None:
        """Best-effort session start for the ECU associated with frame_id.

        If ``force`` is True, sessions are attempted even if the ECU isn't
        marked as requiring one in the database. Useful for ECUs like LBC
        when accessing certain local identifiers (0x21).
        """
        fid = frame_id & 0x1FFFFFFF
        req_id, resp_id = self._pair_for_frame(fid)
        self._select_frame(req_id, resp_id)
        # If the ECU is marked as requiring a session in the dataset, force attempts
        try:
            force_needed = bool(self._session_required_by_req.get(req_id))
        except Exception:
            force_needed = False
        self._ensure_session(req_id, force=(force or force_needed))

    # Public helper to prime/wake an ECU (TesterPresent without response)
    def prime_ecu(self, frame_id: int) -> None:
        try:
            fid = frame_id & 0x1FFFFFFF
            req_id, resp_id = self._pair_for_frame(fid)
            self._select_frame(req_id, resp_id)
            # TesterPresent with no response, then a short wait
            self._send("023E00")
            self._read_lines(0.8)
        except Exception:
            return

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
    def read_field(self, sid: str) -> Optional[Union[float, str]]:
        """Read and decode a diagnostic field by its SID.

        Returns the scaled value, decoded string/hex string or ``None`` if the
        ECU returned a negative response.
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
            fid = field.frame_id & 0x1FFFFFFF
            req_id, resp_id = self._pair_for_frame(fid)
            self._select_frame(req_id, resp_id)
            self._ensure_session(req_id)
        except Exception:
            # Fallback: keep current header; some fields may still respond
            pass
        service = int(rid[:2], 16)
        id_hex = rid[2:]
        ident = int(id_hex, 16)
        # Identifier length differs per service:
        # - 0x21 (ReadDataByLocalIdentifier) -> 1 byte local ID
        # - 0x22 (ReadDataByIdentifier) -> typically 2 bytes (DID)
        if service == 0x21:
            ident_len = 1
        else:
            ident_len = 2 if len(id_hex) >= 4 else 1
        # Reset positive marker for this field read
        self.last_positive = False
        self.last_raw_len = 0
        resp = self._read_by_id(service, ident, ident_len)
        # If we received a buffer (including from cache), mark transport-positive
        if resp:
            try:
                self.last_positive = True
                self.last_raw_len = len(resp)
                # Keep a copy so callers can attempt fallback decoding
                self.last_resp_buf = list(resp)
            except Exception:
                pass
        # Best-effort keep-alive while scanning
        self._tester_present()
        if not resp:
            return None
        return self.decode_value_from_response(field, resp)

    # ------------------------------------------------------------------
    def decode_value_from_response(self, field: Field, resp: Sequence[int]) -> Optional[Union[float, str]]:
        """Decode a field value from a full positive response buffer.

        The buffer must start with the positive response SID (0x61/0x62)
        followed by the echoed identifier bytes and data. Bit offsets in the
        CanZE CSV are defined over this entire buffer.
        """
        data = bytes(resp)
        # Optionally decode relative to payload only (exclude SID + echoed ID)
        try:
            if not getattr(self, "decode_against_full_response", True):
                rid = (field.request_id or "").upper()
                if rid and (rid.startswith("21") or rid.startswith("22")):
                    service = int(rid[:2], 16)
                    ident_len = 1 if service == 0x21 else (2 if len(rid[2:]) >= 4 else 1)
                    header_bytes = 1 + ident_len
                    if len(data) > header_bytes:
                        data = data[header_bytes:]
        except Exception:
            pass
        total_bits = len(data) * 8
        if total_bits <= field.end_bit:
            return None
        width = max(1, int(field.end_bit) - int(field.start_bit) + 1)
        start_byte = int(field.start_bit) // 8
        end_byte = int(field.end_bit) // 8
        raw = data[start_byte : end_byte + 1]
        raw_value = self._extract_bits(data, field.start_bit, field.end_bit)
        # Treat all-ones for wider fields as invalid (common sentinel)
        if (not getattr(self, "disable_all_ones_sentinel", False)) and width >= 5 and raw_value == (1 << width) - 1:
            return None
        # String / hex-string
        if field.is_string() or field.is_hex_string():
            if field.is_string():
                return raw.rstrip(b"\x00").decode("latin-1", errors="ignore")
            return raw.hex()
        # Two's complement for signed
        if field.is_signed():
            sign_bit = 1 << (width - 1)
            if raw_value & sign_bit:
                raw_value -= 1 << width
        # Scale and offset (Android semantics)
        try:
            value = (raw_value - float(field.offset)) * float(field.resolution)
        except Exception:
            value = (raw_value - (field.offset or 0.0)) * (field.resolution or 1.0)
        # Round like Android UI
        try:
            decimals = int(field.decimals)
        except Exception:
            decimals = 0
        return round(value, decimals) if decimals > 0 else value

    # ------------------------------------------------------------------
    def explain_decode_none(self, field: Field, resp: Sequence[int]) -> str:
        """Explain common reasons a decode yielded None for a field.

        Returns one of:
        - 'OUT_OF_RANGE' if the CSV bit range exceeds the available data
        - 'ALL_ONES' if the selected bit range is all 1s (sentinel) and the
          sentinel invalidation is enabled
        - 'UNKNOWN' otherwise
        """
        try:
            data = bytes(resp)
            # Align with the same reference used by the decoder
            if not getattr(self, "decode_against_full_response", True):
                rid = (field.request_id or "").upper()
                if rid and (rid.startswith("21") or rid.startswith("22")):
                    service = int(rid[:2], 16)
                    ident_len = 1 if service == 0x21 else (2 if len(rid[2:]) >= 4 else 1)
                    header_bytes = 1 + ident_len
                    if len(data) > header_bytes:
                        data = data[header_bytes:]
            total_bits = len(data) * 8
            if total_bits <= field.end_bit:
                return "OUT_OF_RANGE"
            width = max(1, int(field.end_bit) - int(field.start_bit) + 1)
            raw_value = self._extract_bits(data, field.start_bit, field.end_bit)
            if (not getattr(self, "disable_all_ones_sentinel", False)) and width >= 5 and raw_value == (1 << width) - 1:
                return "ALL_ONES"
        except Exception:
            return "UNKNOWN"
        return "UNKNOWN"
