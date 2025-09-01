from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233c9():
    client = ReplayUDSClient(sid_responses={"2233C9": ['046233C900AAAAAA']})
    assert client.read_field("7ec.31.6233c9") == pytest.approx(0.0)
