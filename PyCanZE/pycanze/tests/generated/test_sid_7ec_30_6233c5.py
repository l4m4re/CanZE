from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233c5():
    client = ReplayUDSClient(sid_responses={"2233C5": ['046233C502AAAAAA']})
    assert client.read_field("7ec.30.6233c5") == pytest.approx(2.0)
