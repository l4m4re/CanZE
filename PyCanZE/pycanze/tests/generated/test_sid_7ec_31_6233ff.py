from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233ff():
    client = ReplayUDSClient(sid_responses={"2233FF": ['046233FF00AAAAAA']})
    assert client.read_field("7ec.31.6233ff") == pytest.approx(0.0)
