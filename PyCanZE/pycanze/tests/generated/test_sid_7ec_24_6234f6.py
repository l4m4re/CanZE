from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f6():
    client = ReplayUDSClient(sid_responses={"2234F6": ['046234F678AAAAAA']})
    assert client.read_field("7ec.24.6234f6") == pytest.approx(80.0)
