from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622246():
    client = ReplayUDSClient(sid_responses={"222246": ['056222469A40AAAA']})
    assert client.read_field("7ec.24.622246") == pytest.approx(210.0)
