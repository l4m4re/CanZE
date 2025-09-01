from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623390():
    client = ReplayUDSClient(sid_responses={"223390": ['0462339000AAAAAA']})
    assert client.read_field("7ec.31.623390") == pytest.approx(0.0)
