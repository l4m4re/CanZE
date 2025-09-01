from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233c2():
    client = ReplayUDSClient(sid_responses={"2233C2": ['046233C203AAAAAA']})
    assert client.read_field("7ec.29.6233c2") == pytest.approx(3.0)
