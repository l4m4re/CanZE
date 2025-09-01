from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_56_6161():
    client = ReplayUDSClient(sid_responses={"2161": ['10146161001170D8', '21C8C8C8B4B40000', '22B74D000024F8FF']})
    assert client.read_field("7bb.56.6161") == pytest.approx(100.0)
