from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623427():
    client = ReplayUDSClient(sid_responses={"223427": ['0462342700AAAAAA']})
    assert client.read_field("7ec.31.623427") == pytest.approx(0.0)
