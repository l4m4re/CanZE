import sys
from pathlib import Path
import pytest

# ensure package path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pycanze.replay_client import ReplayClient
from pycanze.uds import UDSClient


def test_evc_soc_scaling() -> None:
    client = ReplayClient(responses={"03222002": ["62 20 02 08 D8"]})
    value = client.read_field("7EC.24.622002")
    assert value == pytest.approx(45.28)


def test_evc_battery_rack_temperature() -> None:
    client = ReplayClient(responses={"03222001": ["62 20 01 50"]})
    value = client.read_field("7EC.24.622001")
    assert value == pytest.approx(20.0)


def test_free_frame_hv_battery_temp() -> None:
    client = ReplayClient()
    field = client.fields["42e.44."]
    frame = bytes.fromhex("0000000000078000")
    raw = UDSClient._extract_bits(frame, field.start_bit, field.end_bit)
    value = (raw - field.offset) * field.resolution
    assert value == pytest.approx(10.0)
