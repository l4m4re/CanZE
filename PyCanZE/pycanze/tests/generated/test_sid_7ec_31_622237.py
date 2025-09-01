from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622237():
    client = ReplayUDSClient(sid_responses={"222237": ['0462223700AAAAAA']})
    assert client.read_field("7ec.31.622237") == pytest.approx(0.0)
