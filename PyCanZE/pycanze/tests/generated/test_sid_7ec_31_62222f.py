from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62222f():
    client = ReplayUDSClient(sid_responses={"22222F": ['0462222F00AAAAAA']})
    assert client.read_field("7ec.31.62222f") == pytest.approx(0.0)
