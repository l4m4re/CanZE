from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f7():
    client = ReplayUDSClient(sid_responses={"2234F7": ['046234F732AAAAAA']})
    assert client.read_field("7ec.24.6234f7") == pytest.approx(10.0)
