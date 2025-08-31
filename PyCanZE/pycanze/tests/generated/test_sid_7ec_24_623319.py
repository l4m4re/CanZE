from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623319():
    client = ReplayUDSClient(sid_responses={"223319": ['0462331900AAAAAA']})
    assert client.read_field("7ec.24.623319") == pytest.approx(-1.0)
