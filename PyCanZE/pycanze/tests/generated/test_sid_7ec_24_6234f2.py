from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f2():
    client = ReplayUDSClient(sid_responses={"2234F2": ['046234F200AAAAAA']})
    assert client.read_field("7ec.24.6234f2") == pytest.approx(0.0)
