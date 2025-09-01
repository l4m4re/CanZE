from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623301():
    client = ReplayUDSClient(sid_responses={"223301": ['04623301D8AAAAAA']})
    assert client.read_field("7ec.24.623301") == pytest.approx(13.5)
