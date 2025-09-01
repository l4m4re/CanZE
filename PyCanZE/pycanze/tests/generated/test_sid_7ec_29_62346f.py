from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62346f():
    client = ReplayUDSClient(sid_responses={"22346F": ['0462346F00AAAAAA']})
    assert client.read_field("7ec.29.62346f") == pytest.approx(0.0)
