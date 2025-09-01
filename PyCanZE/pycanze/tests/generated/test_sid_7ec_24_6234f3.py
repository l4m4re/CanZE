from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f3():
    client = ReplayUDSClient(sid_responses={"2234F3": ['056234F30B85AAAA']})
    assert client.read_field("7ec.24.6234f3") == pytest.approx(21.9)
