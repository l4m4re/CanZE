from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62335b():
    client = ReplayUDSClient(sid_responses={"22335B": ['0762335B001D6619']})
    assert client.read_field("7ec.24.62335b") == pytest.approx(1926681.0)
