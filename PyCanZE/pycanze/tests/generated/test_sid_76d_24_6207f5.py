from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207f5():
    client = ReplayUDSClient(sid_responses={"2207F5": ['046207F500000000']})
    assert client.read_field("76d.24.6207f5") == pytest.approx(0.0)
