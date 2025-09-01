from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f9():
    client = ReplayUDSClient(sid_responses={"2234F9": ['046234F900AAAAAA']})
    assert client.read_field("7ec.24.6234f9") == pytest.approx(0.0)
