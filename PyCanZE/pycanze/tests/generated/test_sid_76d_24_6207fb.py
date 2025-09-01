from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207fb():
    client = ReplayUDSClient(sid_responses={"2207FB": ['046207FB00000000']})
    assert client.read_field("76d.24.6207fb") == pytest.approx(0.0)
