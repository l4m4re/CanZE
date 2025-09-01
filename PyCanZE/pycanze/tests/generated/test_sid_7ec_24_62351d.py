from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62351d():
    client = ReplayUDSClient(sid_responses={"22351D": ['0462351D00AAAAAA']})
    assert client.read_field("7ec.24.62351d") == pytest.approx(0.0)
