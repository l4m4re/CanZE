from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62351c():
    client = ReplayUDSClient(sid_responses={"22351C": ['0462351C00AAAAAA']})
    assert client.read_field("7ec.24.62351c") == pytest.approx(0.0)
