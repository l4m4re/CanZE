from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623357():
    client = ReplayUDSClient(sid_responses={"223357": ['0762335700421456']})
    assert client.read_field("7ec.24.623357") == pytest.approx(4330582.0)
