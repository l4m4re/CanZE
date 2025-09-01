from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623424():
    client = ReplayUDSClient(sid_responses={"223424": ['0462342400AAAAAA']})
    assert client.read_field("7ec.31.623424") == pytest.approx(0.0)
