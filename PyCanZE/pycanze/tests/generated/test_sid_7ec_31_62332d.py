from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62332d():
    client = ReplayUDSClient(sid_responses={"22332D": ['0462332D00AAAAAA']})
    assert client.read_field("7ec.31.62332d") == pytest.approx(0.0)
