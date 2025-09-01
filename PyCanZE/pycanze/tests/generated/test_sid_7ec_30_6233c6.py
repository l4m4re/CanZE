from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233c6():
    client = ReplayUDSClient(sid_responses={"2233C6": ['046233C600AAAAAA']})
    assert client.read_field("7ec.30.6233c6") == pytest.approx(0.0)
