from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f1():
    client = ReplayUDSClient(sid_responses={"2234F1": ['046234F100AAAAAA']})
    assert client.read_field("7ec.24.6234f1") == pytest.approx(0.0)
