from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233a6():
    client = ReplayUDSClient(sid_responses={"2233A6": ['046233A600AAAAAA']})
    assert client.read_field("7ec.29.6233a6") == pytest.approx(0.0)
