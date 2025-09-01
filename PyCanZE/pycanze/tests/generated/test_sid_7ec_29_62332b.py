from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62332b():
    client = ReplayUDSClient(sid_responses={"22332B": ['0462332B00AAAAAA']})
    assert client.read_field("7ec.29.62332b") == pytest.approx(0.0)
