from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623452():
    client = ReplayUDSClient(sid_responses={"223452": ['0462345200AAAAAA']})
    assert client.read_field("7ec.31.623452") == pytest.approx(0.0)
