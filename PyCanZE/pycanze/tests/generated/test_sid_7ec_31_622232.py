from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622232():
    client = ReplayUDSClient(sid_responses={"222232": ['0462223200AAAAAA']})
    assert client.read_field("7ec.31.622232") == pytest.approx(0.0)
