from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623485():
    client = ReplayUDSClient(sid_responses={"223485": ['056234853E80AAAA']})
    assert client.read_field("7ec.24.623485") == pytest.approx(16.0)
