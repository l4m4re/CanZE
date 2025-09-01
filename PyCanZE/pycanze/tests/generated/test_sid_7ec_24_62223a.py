from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62223a():
    client = ReplayUDSClient(sid_responses={"22223A": ['0562223A85A0AAAA']})
    assert client.read_field("7ec.24.62223a") == pytest.approx(720.0)
