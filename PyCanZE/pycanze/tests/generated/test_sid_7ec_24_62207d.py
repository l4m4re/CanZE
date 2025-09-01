from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62207d():
    client = ReplayUDSClient(sid_responses={"22207D": ['0462207D00AAAAAA']})
    assert client.read_field("7ec.24.62207d") == pytest.approx(0.0)
