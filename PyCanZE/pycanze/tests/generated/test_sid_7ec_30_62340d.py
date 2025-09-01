from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62340d():
    client = ReplayUDSClient(sid_responses={"22340D": ['0462340D01AAAAAA']})
    assert client.read_field("7ec.30.62340d") == pytest.approx(1.0)
