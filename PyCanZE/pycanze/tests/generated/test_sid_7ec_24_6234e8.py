from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234e8():
    client = ReplayUDSClient(sid_responses={"2234E8": ['046234E803AAAAAA']})
    assert client.read_field("7ec.24.6234e8") == pytest.approx(3.0)
