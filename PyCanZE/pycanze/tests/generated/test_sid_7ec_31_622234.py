from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622234():
    client = ReplayUDSClient(sid_responses={"222234": ['0462223400AAAAAA']})
    assert client.read_field("7ec.31.622234") == pytest.approx(0.0)
