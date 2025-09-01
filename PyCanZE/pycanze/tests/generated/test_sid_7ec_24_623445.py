from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623445():
    client = ReplayUDSClient(sid_responses={"223445": ['0562344501FEAAAA']})
    assert client.read_field("7ec.24.623445") == pytest.approx(51000.0)
