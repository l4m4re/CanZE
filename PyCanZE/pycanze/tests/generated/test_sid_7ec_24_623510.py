from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623510():
    client = ReplayUDSClient(sid_responses={"223510": ['0462351000AAAAAA']})
    assert client.read_field("7ec.24.623510") == pytest.approx(0.0)
