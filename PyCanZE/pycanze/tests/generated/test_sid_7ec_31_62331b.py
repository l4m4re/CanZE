from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62331b():
    client = ReplayUDSClient(sid_responses={"22331B": ['0462331B00AAAAAA']})
    assert client.read_field("7ec.31.62331b") == pytest.approx(0.0)
