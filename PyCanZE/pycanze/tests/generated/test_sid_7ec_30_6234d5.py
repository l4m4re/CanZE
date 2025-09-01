from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234d5():
    client = ReplayUDSClient(sid_responses={"2234D5": ['046234D501AAAAAA']})
    assert client.read_field("7ec.30.6234d5") == pytest.approx(1.0)
