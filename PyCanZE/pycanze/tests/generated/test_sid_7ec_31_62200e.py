from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62200e():
    client = ReplayUDSClient(sid_responses={"22200E": ['0462200E00AAAAAA']})
    assert client.read_field("7ec.31.62200e") == pytest.approx(0.0)
