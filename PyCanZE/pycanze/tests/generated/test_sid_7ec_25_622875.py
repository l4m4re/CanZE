from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_622875():
    client = ReplayUDSClient(sid_responses={"222875": ['056228750000AAAA']})
    assert client.read_field("7ec.25.622875") == pytest.approx(0.0)
