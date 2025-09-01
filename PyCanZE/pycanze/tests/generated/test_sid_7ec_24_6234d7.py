from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234d7():
    client = ReplayUDSClient(sid_responses={"2234D7": ['046234D728AAAAAA']})
    assert client.read_field("7ec.24.6234d7") == pytest.approx(0.0)
