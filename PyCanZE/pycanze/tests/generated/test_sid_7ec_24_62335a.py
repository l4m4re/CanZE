from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62335a():
    client = ReplayUDSClient(sid_responses={"22335A": ['0762335A00001939']})
    assert client.read_field("7ec.24.62335a") == pytest.approx(6457.0)
