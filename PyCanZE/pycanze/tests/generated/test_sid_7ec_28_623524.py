from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_623524():
    client = ReplayUDSClient(sid_responses={"223524": ['0462352400AAAAAA']})
    assert client.read_field("7ec.28.623524") == pytest.approx(0.0)
