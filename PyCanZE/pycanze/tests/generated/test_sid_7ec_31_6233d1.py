from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233d1():
    client = ReplayUDSClient(sid_responses={"2233D1": ['046233D100AAAAAA']})
    assert client.read_field("7ec.31.6233d1") == pytest.approx(0.0)
