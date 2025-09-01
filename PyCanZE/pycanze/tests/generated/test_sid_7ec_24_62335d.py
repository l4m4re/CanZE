from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62335d():
    client = ReplayUDSClient(sid_responses={"22335D": ['0762335D0015DA1E']})
    assert client.read_field("7ec.24.62335d") == pytest.approx(1432094.0)
