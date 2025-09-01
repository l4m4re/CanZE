from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207f9():
    client = ReplayUDSClient(sid_responses={"2207F9": ['046207F900000000']})
    assert client.read_field("76d.24.6207f9") == pytest.approx(0.0)
