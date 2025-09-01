from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623312():
    client = ReplayUDSClient(sid_responses={"223312": ['0462331200AAAAAA']})
    assert client.read_field("7ec.31.623312") == pytest.approx(0.0)
