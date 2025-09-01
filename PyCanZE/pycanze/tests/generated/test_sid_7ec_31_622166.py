from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622166():
    client = ReplayUDSClient(sid_responses={"222166": ['0462216600AAAAAA']})
    assert client.read_field("7ec.31.622166") == pytest.approx(0.0)
