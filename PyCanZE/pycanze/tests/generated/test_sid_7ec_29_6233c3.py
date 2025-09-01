from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233c3():
    client = ReplayUDSClient(sid_responses={"2233C3": ['046233C300AAAAAA']})
    assert client.read_field("7ec.29.6233c3") == pytest.approx(0.0)
