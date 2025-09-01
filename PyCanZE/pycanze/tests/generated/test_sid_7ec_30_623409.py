from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623409():
    client = ReplayUDSClient(sid_responses={"223409": ['0462340901AAAAAA']})
    assert client.read_field("7ec.30.623409") == pytest.approx(1.0)
