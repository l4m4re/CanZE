from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207f6():
    client = ReplayUDSClient(sid_responses={"2207F6": ['046207F600000000']})
    assert client.read_field("76d.24.6207f6") == pytest.approx(0.0)
