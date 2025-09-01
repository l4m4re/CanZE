from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623451():
    client = ReplayUDSClient(sid_responses={"223451": ['056234510078AAAA']})
    assert client.read_field("7ec.24.623451") == pytest.approx(120.0)
