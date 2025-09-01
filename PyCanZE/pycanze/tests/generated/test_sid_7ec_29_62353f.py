from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62353f():
    client = ReplayUDSClient(sid_responses={"22353F": ['0462353F01AAAAAA']})
    assert client.read_field("7ec.29.62353f") == pytest.approx(1.0)
