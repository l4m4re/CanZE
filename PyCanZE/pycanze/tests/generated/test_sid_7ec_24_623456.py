from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623456():
    client = ReplayUDSClient(sid_responses={"223456": ['056234560098AAAA']})
    assert client.read_field("7ec.24.623456") == pytest.approx(152.0)
