from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233cb():
    client = ReplayUDSClient(sid_responses={"2233CB": ['046233CB00AAAAAA']})
    assert client.read_field("7ec.31.6233cb") == pytest.approx(0.0)
