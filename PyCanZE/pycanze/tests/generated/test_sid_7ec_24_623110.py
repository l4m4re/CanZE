from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623110():
    client = ReplayUDSClient(sid_responses={"223110": ['0462311000AAAAAA']})
    assert client.read_field("7ec.24.623110") == pytest.approx(0.0)
