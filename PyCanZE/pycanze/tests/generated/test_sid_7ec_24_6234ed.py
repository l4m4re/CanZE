from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234ed():
    client = ReplayUDSClient(sid_responses={"2234ED": ['046234ED00AAAAAA']})
    assert client.read_field("7ec.24.6234ed") == pytest.approx(0.0)
