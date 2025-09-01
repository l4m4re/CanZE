from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623351():
    client = ReplayUDSClient(sid_responses={"223351": ['0762335100000001']})
    assert client.read_field("7ec.24.623351") == pytest.approx(1.0)
