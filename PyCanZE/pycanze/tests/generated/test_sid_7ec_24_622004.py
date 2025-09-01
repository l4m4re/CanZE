from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622004():
    client = ReplayUDSClient(sid_responses={"222004": ['0562200402C0AAAA']})
    assert client.read_field("7ec.24.622004") == pytest.approx(352.0)
