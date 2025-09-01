from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62330b():
    client = ReplayUDSClient(sid_responses={"22330B": ['0462330B00AAAAAA']})
    assert client.read_field("7ec.31.62330b") == pytest.approx(0.0)
