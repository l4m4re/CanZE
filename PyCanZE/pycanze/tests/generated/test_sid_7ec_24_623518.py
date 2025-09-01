from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623518():
    client = ReplayUDSClient(sid_responses={"223518": ['056235180021AAAA']})
    assert client.read_field("7ec.24.623518") == pytest.approx(33.0)
