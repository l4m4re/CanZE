from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_32_62200f():
    client = ReplayUDSClient(sid_responses={"22200F": ['0562200F6C000C0E']})
    assert client.read_field("76e.32.62200f") == pytest.approx(0.0)
