from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233aa():
    client = ReplayUDSClient(sid_responses={"2233AA": ['046233AA00AAAAAA']})
    assert client.read_field("7ec.31.6233aa") == pytest.approx(0.0)
