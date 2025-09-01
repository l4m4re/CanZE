from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623047():
    client = ReplayUDSClient(sid_responses={"223047": ['056230471388AAAA']})
    assert client.read_field("7ec.24.623047") == pytest.approx(100.0)
