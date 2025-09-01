from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_623387():
    client = ReplayUDSClient(sid_responses={"223387": ['0462338701AAAAAA']})
    assert client.read_field("7ec.28.623387") == pytest.approx(1.0)
