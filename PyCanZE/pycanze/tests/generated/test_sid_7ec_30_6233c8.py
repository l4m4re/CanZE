from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233c8():
    client = ReplayUDSClient(sid_responses={"2233C8": ['046233C800AAAAAA']})
    assert client.read_field("7ec.30.6233c8") == pytest.approx(0.0)
