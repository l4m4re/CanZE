from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62338f():
    client = ReplayUDSClient(sid_responses={"22338F": ['0462338F00AAAAAA']})
    assert client.read_field("7ec.31.62338f") == pytest.approx(0.0)
