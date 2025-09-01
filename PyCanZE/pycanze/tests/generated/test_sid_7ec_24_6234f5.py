from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f5():
    client = ReplayUDSClient(sid_responses={"2234F5": ['046234F578AAAAAA']})
    assert client.read_field("7ec.24.6234f5") == pytest.approx(80.0)
