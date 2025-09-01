from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62338b():
    client = ReplayUDSClient(sid_responses={"22338B": ['0462338B00AAAAAA']})
    assert client.read_field("7ec.31.62338b") == pytest.approx(0.0)
