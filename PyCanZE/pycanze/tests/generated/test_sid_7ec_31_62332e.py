from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62332e():
    client = ReplayUDSClient(sid_responses={"22332E": ['0462332E00AAAAAA']})
    assert client.read_field("7ec.31.62332e") == pytest.approx(0.0)
