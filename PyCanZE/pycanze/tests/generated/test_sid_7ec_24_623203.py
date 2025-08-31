from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623203():
    client = ReplayUDSClient(sid_responses={"223203": ['0562320303E8AAAA']})
    assert client.read_field("7ec.24.623203") == pytest.approx(500.0)
