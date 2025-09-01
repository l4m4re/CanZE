from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62353b():
    client = ReplayUDSClient(sid_responses={"22353B": ['0562353B00F0AAAA']})
    assert client.read_field("7ec.24.62353b") == pytest.approx(-16263.5)
