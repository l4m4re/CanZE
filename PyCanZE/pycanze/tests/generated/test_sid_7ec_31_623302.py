from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623302():
    client = ReplayUDSClient(sid_responses={"223302": ['0462330200AAAAAA']})
    assert client.read_field("7ec.31.623302") == pytest.approx(0.0)
