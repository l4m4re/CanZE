from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623322():
    client = ReplayUDSClient(sid_responses={"223322": ['0462332200AAAAAA']})
    assert client.read_field("7ec.31.623322") == pytest.approx(0.0)
