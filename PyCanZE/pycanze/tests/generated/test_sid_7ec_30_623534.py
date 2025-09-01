from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623534():
    client = ReplayUDSClient(sid_responses={"223534": ['0462353400AAAAAA']})
    assert client.read_field("7ec.30.623534") == pytest.approx(0.0)
