from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623308():
    client = ReplayUDSClient(sid_responses={"223308": ['0462330800AAAAAA']})
    assert client.read_field("7ec.30.623308") == pytest.approx(0.0)
