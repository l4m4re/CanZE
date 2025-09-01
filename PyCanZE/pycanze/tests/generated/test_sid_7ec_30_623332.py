from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623332():
    client = ReplayUDSClient(sid_responses={"223332": ['0462333201AAAAAA']})
    assert client.read_field("7ec.30.623332") == pytest.approx(1.0)
