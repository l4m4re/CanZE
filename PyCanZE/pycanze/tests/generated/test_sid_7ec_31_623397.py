from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623397():
    client = ReplayUDSClient(sid_responses={"223397": ['0462339700AAAAAA']})
    assert client.read_field("7ec.31.623397") == pytest.approx(0.0)
