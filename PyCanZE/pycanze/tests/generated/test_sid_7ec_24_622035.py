from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622035():
    client = ReplayUDSClient(sid_responses={"222035": ['0462203500AAAAAA']})
    assert client.read_field("7ec.24.622035") == pytest.approx(0.0)
