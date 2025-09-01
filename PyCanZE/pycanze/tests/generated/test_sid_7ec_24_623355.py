from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623355():
    client = ReplayUDSClient(sid_responses={"223355": ['07623355000051A2']})
    assert client.read_field("7ec.24.623355") == pytest.approx(20898.0)
