from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207f4():
    client = ReplayUDSClient(sid_responses={"2207F4": ['056207F400000000']})
    assert client.read_field("76d.24.6207f4") == pytest.approx(0.0)
