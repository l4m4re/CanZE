from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_62200f():
    client = ReplayUDSClient(sid_responses={"22200F": ['0562200F6C000C0E']})
    assert client.read_field("76e.24.62200f") == pytest.approx(108.0)
