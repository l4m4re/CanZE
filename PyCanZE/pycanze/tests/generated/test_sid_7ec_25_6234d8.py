from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_6234d8():
    client = ReplayUDSClient(sid_responses={"2234D8": ['046234D819AAAAAA']})
    assert client.read_field("7ec.25.6234d8") == pytest.approx(25.0)
