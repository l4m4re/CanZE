from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234e5():
    client = ReplayUDSClient(sid_responses={"2234E5": ['046234E500AAAAAA']})
    assert client.read_field("7ec.24.6234e5") == pytest.approx(0.0)
