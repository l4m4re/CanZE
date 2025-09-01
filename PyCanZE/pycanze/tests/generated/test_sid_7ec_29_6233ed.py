from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233ed():
    client = ReplayUDSClient(sid_responses={"2233ED": ['046233ED00AAAAAA']})
    assert client.read_field("7ec.29.6233ed") == pytest.approx(0.0)
