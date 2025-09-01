from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62339d():
    client = ReplayUDSClient(sid_responses={"22339D": ['0462339D00AAAAAA']})
    assert client.read_field("7ec.31.62339d") == pytest.approx(0.0)
