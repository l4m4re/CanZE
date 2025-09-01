from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623519():
    client = ReplayUDSClient(sid_responses={"223519": ['0462351932AAAAAA']})
    assert client.read_field("7ec.24.623519") == pytest.approx(50.0)
