from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62338d():
    client = ReplayUDSClient(sid_responses={"22338D": ['0462338D00AAAAAA']})
    assert client.read_field("7ec.31.62338d") == pytest.approx(0.0)
