from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62320b():
    client = ReplayUDSClient(sid_responses={"22320B": ['0462320BC8AAAAAA']})
    assert client.read_field("7ec.24.62320b") == pytest.approx(100.0)
