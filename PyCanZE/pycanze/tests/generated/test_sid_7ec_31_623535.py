from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623535():
    client = ReplayUDSClient(sid_responses={"223535": ['0462353500AAAAAA']})
    assert client.read_field("7ec.31.623535") == pytest.approx(0.0)
