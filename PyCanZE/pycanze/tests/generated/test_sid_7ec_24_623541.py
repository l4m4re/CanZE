from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623541():
    client = ReplayUDSClient(sid_responses={"223541": ['0462354100AAAAAA']})
    assert client.read_field("7ec.24.623541") == pytest.approx(0.0)
