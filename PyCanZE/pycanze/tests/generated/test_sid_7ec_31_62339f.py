from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62339f():
    client = ReplayUDSClient(sid_responses={"22339F": ['0462339F00AAAAAA']})
    assert client.read_field("7ec.31.62339f") == pytest.approx(0.0)
