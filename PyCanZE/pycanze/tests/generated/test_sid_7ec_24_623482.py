from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623482():
    client = ReplayUDSClient(sid_responses={"223482": ['0462348200AAAAAA']})
    assert client.read_field("7ec.24.623482") == pytest.approx(0.0)
