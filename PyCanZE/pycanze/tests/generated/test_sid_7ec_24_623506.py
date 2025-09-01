from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623506():
    client = ReplayUDSClient(sid_responses={"223506": ['0462350600AAAAAA']})
    assert client.read_field("7ec.24.623506") == pytest.approx(0.0)
