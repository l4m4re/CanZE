from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_31_6207b1():
    client = ReplayUDSClient(sid_responses={"2207B1": ['056207B100540000']})
    assert client.read_field("76d.31.6207b1") == pytest.approx(84.0)
