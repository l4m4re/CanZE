from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f4():
    client = ReplayUDSClient(sid_responses={"2234F4": ['046234F478AAAAAA']})
    assert client.read_field("7ec.24.6234f4") == pytest.approx(80.0)
