from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234cb():
    client = ReplayUDSClient(sid_responses={"2234CB": ['046234CB32AAAAAA']})
    assert client.read_field("7ec.24.6234cb") == pytest.approx(100.0)
