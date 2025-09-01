from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623439():
    client = ReplayUDSClient(sid_responses={"223439": ['0462343900AAAAAA']})
    assert client.read_field("7ec.30.623439") == pytest.approx(0.0)
