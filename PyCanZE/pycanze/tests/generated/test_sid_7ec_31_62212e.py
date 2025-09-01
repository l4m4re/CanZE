from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62212e():
    client = ReplayUDSClient(sid_responses={"22212E": ['0462212E00AAAAAA']})
    assert client.read_field("7ec.31.62212e") == pytest.approx(0.0)
