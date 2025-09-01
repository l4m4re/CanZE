from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62339e():
    client = ReplayUDSClient(sid_responses={"22339E": ['0462339E00AAAAAA']})
    assert client.read_field("7ec.31.62339e") == pytest.approx(0.0)
