from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62330d():
    client = ReplayUDSClient(sid_responses={"22330D": ['0462330D00AAAAAA']})
    assert client.read_field("7ec.31.62330d") == pytest.approx(0.0)
