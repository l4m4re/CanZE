from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623421():
    client = ReplayUDSClient(sid_responses={"223421": ['0462342128AAAAAA']})
    assert client.read_field("7ec.24.623421") == pytest.approx(0.0)
