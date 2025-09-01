from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_27_6207ed():
    client = ReplayUDSClient(sid_responses={"2207ED": ['056207ED00000000']})
    assert client.read_field("76d.27.6207ed") == pytest.approx(0.0)
