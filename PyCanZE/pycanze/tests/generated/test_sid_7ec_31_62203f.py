from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62203f():
    client = ReplayUDSClient(sid_responses={"22203F": ['0462203F00AAAAAA']})
    assert client.read_field("7ec.31.62203f") == pytest.approx(0.0)
