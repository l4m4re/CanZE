from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623513():
    client = ReplayUDSClient(sid_responses={"223513": ['0462351300AAAAAA']})
    assert client.read_field("7ec.24.623513") == pytest.approx(0.0)
