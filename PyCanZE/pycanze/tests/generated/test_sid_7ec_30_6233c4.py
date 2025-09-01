from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233c4():
    client = ReplayUDSClient(sid_responses={"2233C4": ['046233C400AAAAAA']})
    assert client.read_field("7ec.30.6233c4") == pytest.approx(0.0)
