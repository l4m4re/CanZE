from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623394():
    client = ReplayUDSClient(sid_responses={"223394": ['0462339400AAAAAA']})
    assert client.read_field("7ec.31.623394") == pytest.approx(0.0)
