from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233ec():
    client = ReplayUDSClient(sid_responses={"2233EC": ['046233EC00AAAAAA']})
    assert client.read_field("7ec.29.6233ec") == pytest.approx(0.0)
