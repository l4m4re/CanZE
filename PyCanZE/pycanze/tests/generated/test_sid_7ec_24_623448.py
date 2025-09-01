from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623448():
    client = ReplayUDSClient(sid_responses={"223448": ['056234489A40AAAA']})
    assert client.read_field("7ec.24.623448") == pytest.approx(210.0)
