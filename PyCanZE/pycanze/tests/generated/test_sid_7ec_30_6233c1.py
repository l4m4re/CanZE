from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233c1():
    client = ReplayUDSClient(sid_responses={"2233C1": ['046233C102AAAAAA']})
    assert client.read_field("7ec.30.6233c1") == pytest.approx(2.0)
