from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622235():
    client = ReplayUDSClient(sid_responses={"222235": ['0462223500AAAAAA']})
    assert client.read_field("7ec.31.622235") == pytest.approx(0.0)
