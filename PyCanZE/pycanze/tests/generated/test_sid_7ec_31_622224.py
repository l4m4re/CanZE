from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622224():
    client = ReplayUDSClient(sid_responses={"222224": ['0462222400AAAAAA']})
    assert client.read_field("7ec.31.622224") == pytest.approx(0.0)
