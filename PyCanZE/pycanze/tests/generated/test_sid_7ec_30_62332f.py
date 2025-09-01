from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62332f():
    client = ReplayUDSClient(sid_responses={"22332F": ['0462332F00AAAAAA']})
    assert client.read_field("7ec.30.62332f") == pytest.approx(0.0)
