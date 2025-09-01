from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623470():
    client = ReplayUDSClient(sid_responses={"223470": ['05623470000DAAAA']})
    assert client.read_field("7ec.24.623470") == pytest.approx(1.3)
