from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_622078():
    client = ReplayUDSClient(sid_responses={"222078": ['0462207800AAAAAA']})
    assert client.read_field("7ec.29.622078") == pytest.approx(0.0)
