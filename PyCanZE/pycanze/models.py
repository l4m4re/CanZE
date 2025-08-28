"""Dataclasses representing CanZE metadata."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Ecu:
    """Electronic Control Unit description."""

    name: str
    sid: int
    networks: List[str]
    request_id: int
    response_id: int
    mnemonic: str
    aliases: List[str]
    dtc_response_ids: List[int]
    start_diag: Optional[int]
    session_required: int


@dataclass(frozen=True)
class Frame:
    """CAN frame description."""

    frame_id: int
    interval_zoe: int
    interval_flukan: int
    ecu: str


@dataclass(frozen=True)
class Field:
    """Field description within a frame."""

    sid: str
    frame_id: int
    start_bit: int
    end_bit: int
    resolution: float
    offset: float
    decimals: int
    unit: str
    request_id: Optional[str]
    response_id: Optional[str]
    options: List[str] = field(default_factory=list)
    name: Optional[str] = None
    raw_values: Optional[str] = None
