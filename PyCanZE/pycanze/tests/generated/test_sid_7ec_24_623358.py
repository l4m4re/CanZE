from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623358():
    client = ReplayUDSClient(sid_responses={"223358": ['0762335800016E48']})
    assert client.read_field("7ec.24.623358") == pytest.approx(93768.0)
