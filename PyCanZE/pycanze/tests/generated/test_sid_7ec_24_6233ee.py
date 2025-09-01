from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233ee():
    client = ReplayUDSClient(sid_responses={"2233EE": ['056233EE2710AAAA']})
    assert client.read_field("7ec.24.6233ee") == pytest.approx(1000000.0)
