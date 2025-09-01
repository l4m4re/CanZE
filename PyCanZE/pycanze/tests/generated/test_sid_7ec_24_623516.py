from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623516():
    client = ReplayUDSClient(sid_responses={"223516": ['0462351600AAAAAA']})
    assert client.read_field("7ec.24.623516") == pytest.approx(0.0)
