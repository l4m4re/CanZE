from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_40_6160():
    client = ReplayUDSClient(sid_responses={"2160": ['100961603BC34C5A', '215EFFFF00000000']})
    assert client.read_field("7bb.40.6160") == pytest.approx(90.0)
