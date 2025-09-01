from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623349():
    client = ReplayUDSClient(sid_responses={"223349": ['0762334901865037']})
    assert client.read_field("7ec.24.623349") == pytest.approx(25579575.0)
