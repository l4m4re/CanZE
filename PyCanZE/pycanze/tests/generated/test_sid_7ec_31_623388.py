from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623388():
    client = ReplayUDSClient(sid_responses={"223388": ['0462338800AAAAAA']})
    assert client.read_field("7ec.31.623388") == pytest.approx(0.0)
