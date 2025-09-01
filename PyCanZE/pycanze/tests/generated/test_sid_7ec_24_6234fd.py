from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234fd():
    client = ReplayUDSClient(sid_responses={"2234FD": ['056234FD0B85AAAA']})
    assert client.read_field("7ec.24.6234fd") == pytest.approx(21.9)
