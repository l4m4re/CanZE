from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62346b():
    client = ReplayUDSClient(sid_responses={"22346B": ['0462346B01AAAAAA']})
    assert client.read_field("7ec.24.62346b") == pytest.approx(1.0)
