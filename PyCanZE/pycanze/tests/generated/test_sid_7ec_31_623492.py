from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623492():
    client = ReplayUDSClient(sid_responses={"223492": ['0462349200AAAAAA']})
    assert client.read_field("7ec.31.623492") == pytest.approx(0.0)
