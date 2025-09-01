from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207c1():
    client = ReplayUDSClient(sid_responses={"2207C1": ['046207C100000000']})
    assert client.read_field("76d.24.6207c1") == pytest.approx(0.0)
