from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623392():
    client = ReplayUDSClient(sid_responses={"223392": ['0462339200AAAAAA']})
    assert client.read_field("7ec.31.623392") == pytest.approx(0.0)
