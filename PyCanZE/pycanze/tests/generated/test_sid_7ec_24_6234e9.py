from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234e9():
    client = ReplayUDSClient(sid_responses={"2234E9": ['046234E964AAAAAA']})
    assert client.read_field("7ec.24.6234e9") == pytest.approx(100.0)
