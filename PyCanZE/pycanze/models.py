"""Dataclasses representing CanZE metadata."""

from dataclasses import dataclass
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
    options: int = 0
    name: Optional[str] = None
    raw_values: Optional[str] = None

    FIELD_TYPE_MASK = 0x700
    FIELD_TYPE_SIGNED = 0x100
    FIELD_TYPE_STRING = 0x200
    FIELD_TYPE_HEXSTRING = 0x400
    FIELD_SELFPROPELLED = 0x800

    def is_signed(self) -> bool:
        return (self.options & self.FIELD_TYPE_MASK) == self.FIELD_TYPE_SIGNED

    def is_string(self) -> bool:
        return (self.options & self.FIELD_TYPE_MASK) == self.FIELD_TYPE_STRING

    def is_hex_string(self) -> bool:
        return (self.options & self.FIELD_TYPE_MASK) == self.FIELD_TYPE_HEXSTRING

    def is_self_propelled(self) -> bool:
        return (self.options & self.FIELD_SELFPROPELLED) == self.FIELD_SELFPROPELLED
