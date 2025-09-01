from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623426():
    client = ReplayUDSClient(sid_responses={"223426": ['0462342600AAAAAA']})
    assert client.read_field("7ec.31.623426") == pytest.approx(0.0)
