from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_6234a6():
    client = ReplayUDSClient(sid_responses={"2234A6": ['046234A600AAAAAA']})
    assert client.read_field("7ec.25.6234a6") == pytest.approx(0.0)
