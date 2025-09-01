from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233fd():
    client = ReplayUDSClient(sid_responses={"2233FD": ['046233FD00AAAAAA']})
    assert client.read_field("7ec.31.6233fd") == pytest.approx(0.0)
