from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623533():
    client = ReplayUDSClient(sid_responses={"223533": ['0462353300AAAAAA']})
    assert client.read_field("7ec.31.623533") == pytest.approx(0.0)
