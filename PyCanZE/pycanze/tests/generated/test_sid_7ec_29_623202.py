from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623202():
    client = ReplayUDSClient(sid_responses={"223202": ['0462320201AAAAAA']})
    assert client.read_field("7ec.29.623202") == pytest.approx(1.0)
