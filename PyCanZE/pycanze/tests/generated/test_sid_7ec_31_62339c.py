from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62339c():
    client = ReplayUDSClient(sid_responses={"22339C": ['0462339C00AAAAAA']})
    assert client.read_field("7ec.31.62339c") == pytest.approx(0.0)
