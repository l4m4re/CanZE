from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623515():
    client = ReplayUDSClient(sid_responses={"223515": ['0462351501AAAAAA']})
    assert client.read_field("7ec.24.623515") == pytest.approx(1.0)
