from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62332c():
    client = ReplayUDSClient(sid_responses={"22332C": ['0462332C00AAAAAA']})
    assert client.read_field("7ec.29.62332c") == pytest.approx(0.0)
