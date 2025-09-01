from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_48_623375():
    client = ReplayUDSClient(sid_responses={"223375": ['1008623375010106', '210101AAAAAAAAAA']})
    assert client.read_field("7ec.48.623375") == pytest.approx(1.0)
