from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6234a4():
    client = ReplayUDSClient(sid_responses={"2234A4": ['046234A400AAAAAA']})
    assert client.read_field("7ec.29.6234a4") == pytest.approx(0.0)
