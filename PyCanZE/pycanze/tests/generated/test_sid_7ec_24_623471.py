from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623471():
    client = ReplayUDSClient(sid_responses={"223471": ['0462347114AAAAAA']})
    assert client.read_field("7ec.24.623471") == pytest.approx(100.0)
