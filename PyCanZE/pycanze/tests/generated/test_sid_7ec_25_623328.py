from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_623328():
    client = ReplayUDSClient(sid_responses={"223328": ['046233280AAAAAAA']})
    assert client.read_field("7ec.25.623328") == pytest.approx(10.0)
