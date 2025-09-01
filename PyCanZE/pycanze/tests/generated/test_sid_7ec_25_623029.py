from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_623029():
    client = ReplayUDSClient(sid_responses={"223029": ['0462302964AAAAAA']})
    assert client.read_field("7ec.25.623029") == pytest.approx(100.0)
