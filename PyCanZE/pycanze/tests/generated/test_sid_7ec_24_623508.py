from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623508():
    client = ReplayUDSClient(sid_responses={"223508": ['0462350800AAAAAA']})
    assert client.read_field("7ec.24.623508") == pytest.approx(0.0)
