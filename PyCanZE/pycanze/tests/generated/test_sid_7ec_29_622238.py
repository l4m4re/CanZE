from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_622238():
    client = ReplayUDSClient(sid_responses={"222238": ['0462223801AAAAAA']})
    assert client.read_field("7ec.29.622238") == pytest.approx(1.0)
