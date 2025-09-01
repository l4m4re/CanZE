from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_26_6207c9():
    client = ReplayUDSClient(sid_responses={"2207C9": ['056207C926FD0000']})
    assert client.read_field("76d.26.6207c9") == pytest.approx(99.81)
