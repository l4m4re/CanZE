from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623458():
    client = ReplayUDSClient(sid_responses={"223458": ['056234580041AAAA']})
    assert client.read_field("7ec.24.623458") == pytest.approx(65.0)
