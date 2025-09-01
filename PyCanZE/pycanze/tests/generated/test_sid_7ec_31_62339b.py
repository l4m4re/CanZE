from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62339b():
    client = ReplayUDSClient(sid_responses={"22339B": ['0462339B00AAAAAA']})
    assert client.read_field("7ec.31.62339b") == pytest.approx(0.0)
