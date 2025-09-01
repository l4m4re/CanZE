from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623364():
    client = ReplayUDSClient(sid_responses={"223364": ['0762336400000006']})
    assert client.read_field("7ec.24.623364") == pytest.approx(6.0)
