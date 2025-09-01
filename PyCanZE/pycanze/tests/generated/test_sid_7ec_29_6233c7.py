from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233c7():
    client = ReplayUDSClient(sid_responses={"2233C7": ['046233C700AAAAAA']})
    assert client.read_field("7ec.29.6233c7") == pytest.approx(0.0)
