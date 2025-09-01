from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207ff():
    client = ReplayUDSClient(sid_responses={"2207FF": ['046207FF00000000']})
    assert client.read_field("76d.24.6207ff") == pytest.approx(0.0)
