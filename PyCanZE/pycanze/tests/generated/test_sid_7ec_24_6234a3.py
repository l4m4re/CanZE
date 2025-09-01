from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234a3():
    client = ReplayUDSClient(sid_responses={"2234A3": ['056234A30BA4AAAA']})
    assert client.read_field("7ec.24.6234a3") == pytest.approx(25.0)
