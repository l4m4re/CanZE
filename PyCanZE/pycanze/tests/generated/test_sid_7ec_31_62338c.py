from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62338c():
    client = ReplayUDSClient(sid_responses={"22338C": ['0462338C00AAAAAA']})
    assert client.read_field("7ec.31.62338c") == pytest.approx(0.0)
