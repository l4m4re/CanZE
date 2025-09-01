from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623496():
    client = ReplayUDSClient(sid_responses={"223496": ['0462349600AAAAAA']})
    assert client.read_field("7ec.31.623496") == pytest.approx(0.0)
