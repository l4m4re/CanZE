from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622001():
    client = ReplayUDSClient(sid_responses={"222001": ['0462200128AAAAAA']})
    assert client.read_field("7ec.24.622001") == pytest.approx(0.0)
