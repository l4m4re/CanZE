from __future__ import annotations

"""In-memory UDS client that replays canned responses.

The :class:`ReplayClient` behaves like :class:`~pycanze.uds.UDSClient` but
reads responses from a provided mapping instead of a real socket.  It is
intended for unit tests and examples that need deterministic interaction
without accessing a physical ELM327 dongle.

Parameters
----------
responses:
    Mapping of command hex strings to the list of response lines that
    :meth:`_read_lines` should return.  Each key is the exact string passed to
    :meth:`_send`.
sid_responses:
    Optional mapping of *service identifier* strings to response lines.  The
    length byte normally prepended by :class:`UDSClient` is inserted
    automatically.  For example::

        client = ReplayClient(sid_responses={"10C0": ["50C0"]})
        client._send("0210C0")
        client._read_lines()  # -> ["50C0"]

Unknown commands yield an empty list of lines.
"""

from typing import Dict, Mapping, Sequence, Optional, Union

from .models import Field
from .uds import UDSClient, ELM_CMD_SLEEP


class ReplayClient(UDSClient):
    """UDS client returning canned responses from a mapping."""

    def __init__(
        self,
        responses: Optional[Mapping[str, Sequence[str]]] = None,
        sid_responses: Optional[Mapping[str, Union[Sequence[str], str]]] = None,
        fields: Optional[Dict[str, Field]] = None,
    ) -> None:
        super().__init__("0.0.0.0", fields=fields)
        # a dummy sock object satisfies UDSClient checks without networking
        self.sock = object()
        self._last_cmd = ""
        self._responses: Dict[str, Sequence[str]] = {}
        if responses:
            for cmd, lines in responses.items():
                self._responses[cmd.upper()] = list(lines)
        if sid_responses:
            for sid, lines in sid_responses.items():
                # normalise service identifier and prepend length byte
                norm = sid.strip().upper().replace(" ", "")
                length = len(norm) // 2
                cmd = f"{length:02X}{norm}"
                if isinstance(lines, str):
                    self._responses[cmd] = [lines]
                else:
                    self._responses[cmd] = list(lines)

    # override socket helpers -------------------------------------------------
    def _send(self, line: str, wait: float = ELM_CMD_SLEEP) -> None:  # type: ignore[override]
        self._last_cmd = line.strip().upper().replace(" ", "")

    def _read_lines(self, timeout: float | None = None):  # type: ignore[override]
        return self._responses.get(self._last_cmd, [])
