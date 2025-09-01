from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623505():
    client = ReplayUDSClient(sid_responses={"223505": ['0462350500AAAAAA']})
    assert client.read_field("7ec.24.623505") == pytest.approx(0.0)
