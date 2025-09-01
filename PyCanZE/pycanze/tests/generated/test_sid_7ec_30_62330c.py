from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62330c():
    client = ReplayUDSClient(sid_responses={"22330C": ['0462330C00AAAAAA']})
    assert client.read_field("7ec.30.62330c") == pytest.approx(0.0)
