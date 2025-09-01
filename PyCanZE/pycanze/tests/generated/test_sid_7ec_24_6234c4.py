from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234c4():
    client = ReplayUDSClient(sid_responses={"2234C4": ['056234C405A0AAAA']})
    assert client.read_field("7ec.24.6234c4") == pytest.approx(1440.0)
