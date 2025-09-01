from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623348():
    client = ReplayUDSClient(sid_responses={"223348": ['0462334800AAAAAA']})
    assert client.read_field("7ec.24.623348") == pytest.approx(0.0)
