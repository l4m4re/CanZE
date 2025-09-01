from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623112():
    client = ReplayUDSClient(sid_responses={"223112": ['0462311200AAAAAA']})
    assert client.read_field("7ec.31.623112") == pytest.approx(0.0)
