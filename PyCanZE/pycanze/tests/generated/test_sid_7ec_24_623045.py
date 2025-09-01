from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623045():
    client = ReplayUDSClient(sid_responses={"223045": ['056230457830AAAA']})
    assert client.read_field("7ec.24.623045") == pytest.approx(-20000.0)
