from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62331e():
    client = ReplayUDSClient(sid_responses={"22331E": ['0462331E00AAAAAA']})
    assert client.read_field("7ec.31.62331e") == pytest.approx(0.0)
