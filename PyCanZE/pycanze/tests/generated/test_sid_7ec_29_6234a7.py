from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6234a7():
    client = ReplayUDSClient(sid_responses={"2234A7": ['046234A701AAAAAA']})
    assert client.read_field("7ec.29.6234a7") == pytest.approx(1.0)
