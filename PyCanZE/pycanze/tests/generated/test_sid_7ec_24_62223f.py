from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62223f():
    client = ReplayUDSClient(sid_responses={"22223F": ['0562223F85A0AAAA']})
    assert client.read_field("7ec.24.62223f") == pytest.approx(720.0)
