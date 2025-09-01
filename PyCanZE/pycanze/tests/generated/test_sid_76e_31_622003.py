from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_31_622003():
    client = ReplayUDSClient(sid_responses={"222003": ['0462200300302020']})
    assert client.read_field("76e.31.622003") == pytest.approx(0.0)
