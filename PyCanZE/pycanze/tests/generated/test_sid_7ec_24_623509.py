from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623509():
    client = ReplayUDSClient(sid_responses={"223509": ['0462350901AAAAAA']})
    assert client.read_field("7ec.24.623509") == pytest.approx(1.0)
