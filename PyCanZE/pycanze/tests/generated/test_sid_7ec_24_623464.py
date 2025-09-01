from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623464():
    client = ReplayUDSClient(sid_responses={"223464": ['0462346400AAAAAA']})
    assert client.read_field("7ec.24.623464") == pytest.approx(0.0)
