from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234a5():
    client = ReplayUDSClient(sid_responses={"2234A5": ['046234A502AAAAAA']})
    assert client.read_field("7ec.30.6234a5") == pytest.approx(2.0)
