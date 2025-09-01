from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207d4():
    client = ReplayUDSClient(sid_responses={"2207D4": ['046207D400000000']})
    assert client.read_field("76d.24.6207d4") == pytest.approx(0.0)
