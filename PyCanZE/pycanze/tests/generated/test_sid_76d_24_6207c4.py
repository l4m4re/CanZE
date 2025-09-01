from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207c4():
    client = ReplayUDSClient(sid_responses={"2207C4": ['046207C401000000']})
    assert client.read_field("76d.24.6207c4") == pytest.approx(0.0)
