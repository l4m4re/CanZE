from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207ec():
    client = ReplayUDSClient(sid_responses={"2207EC": ['046207EC00000000']})
    assert client.read_field("76d.24.6207ec") == pytest.approx(0.0)
