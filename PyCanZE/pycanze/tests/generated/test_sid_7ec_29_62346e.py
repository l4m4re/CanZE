from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62346e():
    client = ReplayUDSClient(sid_responses={"22346E": ['0462346E00AAAAAA']})
    assert client.read_field("7ec.29.62346e") == pytest.approx(0.0)
