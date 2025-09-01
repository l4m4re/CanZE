from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234c3():
    client = ReplayUDSClient(sid_responses={"2234C3": ['056234C305A0AAAA']})
    assert client.read_field("7ec.24.6234c3") == pytest.approx(1440.0)
