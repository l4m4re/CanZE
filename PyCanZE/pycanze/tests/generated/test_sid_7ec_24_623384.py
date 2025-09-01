from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623384():
    client = ReplayUDSClient(sid_responses={"223384": ['0462338400AAAAAA']})
    assert client.read_field("7ec.24.623384") == pytest.approx(0.0)
