from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207c2():
    client = ReplayUDSClient(sid_responses={"2207C2": ['046207C200000000']})
    assert client.read_field("76d.24.6207c2") == pytest.approx(0.0)
